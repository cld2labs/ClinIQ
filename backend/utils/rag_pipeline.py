"""
RAG (Retrieval-Augmented Generation) Pipeline Module

This module implements the core question-answering system using RAG architecture.
RAG combines two powerful techniques:
1. RETRIEVAL: Finds relevant information from documents
2. GENERATION: Uses AI to generate answers based on retrieved information

The pipeline works in these stages:
1. Query Rewriting: Makes follow-up questions self-contained
2. Document Retrieval: Searches for relevant document chunks
3. Reranking: Re-orders results by relevance
4. Answer Generation: Creates answer using retrieved context

This ensures answers are grounded in the actual documents, not hallucinated.
"""

from openai import OpenAI
import os
from utils.vector_store import search_documents, hybrid_search, rerank_chunks
from utils.constants import CHAT_MODEL, EMBEDDING_MODEL

# Export model constants for use in other modules
DEFAULT_CHAT_MODEL = CHAT_MODEL
DEFAULT_EMBEDDING_MODEL = EMBEDDING_MODEL

def _get_context_and_citations(query, api_key, use_hybrid_search, use_reranker):
    """
    THE RESEARCHER: Finds relevant document chunks for answering questions.
    
    This is the retrieval stage of RAG. It searches through all uploaded documents
    to find the most relevant pieces of information that can answer the user's question.
    
    Process:
    1. Converts the question into an embedding (vector representation)
    2. Searches documents using either hybrid or dense search
    3. Optionally reranks results for better relevance
    4. Extracts top chunks with their source information
    5. Formats context and citations for the AI to use
    
    Args:
        query (str): The user's question or search query
        api_key (str): OpenAI API key for creating query embeddings
        use_hybrid_search (bool): If True, uses hybrid search (semantic + keyword)
                                 If False, uses only semantic (dense) search
        use_reranker (bool): If True, reranks results by relevance
                            If False, uses original search order
    
    Returns:
        tuple: (context_text, citations)
            - context_text (str): Formatted text containing relevant document chunks
                                 Each chunk includes the content and source info
            - citations (list): List of citation strings for the retrieved chunks
                              Format: ["Source: filename.pdf | Page: 5", ...]
    
    Example:
        Input:
            query = "What are the side effects?"
            use_hybrid_search = True
            use_reranker = True
        
        Output:
            context_text = "Content: Side effects include nausea...\nSource: med_guide.pdf | Page: 3\n\n..."
            citations = ["Source: med_guide.pdf | Page: 3", "Source: med_guide.pdf | Page: 4"]
    
    Why This Matters:
        - Better context = Better answers
        - Citations allow users to verify information
        - Hybrid search finds more comprehensive results
        - Reranking ensures most relevant chunks are used
    """
    client = OpenAI(api_key=api_key)

    # ========================================================================
    # STEP 1: Convert question to embedding
    # ========================================================================
    # Embeddings allow semantic search - finding documents by meaning
    # Example: "heart attack" and "myocardial infarction" have similar embeddings
    emb_response = client.embeddings.create(
        input=query,  # The user's question
        model=DEFAULT_EMBEDDING_MODEL  # text-embedding-3-small
    )
    # Extract the embedding vector (list of 1536 numbers)
    query_embedding = emb_response.data[0].embedding

    # ========================================================================
    # STEP 2: Search for relevant document chunks
    # ========================================================================
    # Choose between hybrid search (recommended) or dense search only
    if use_hybrid_search:
        # Hybrid search combines:
        # - Dense search: Finds by meaning (semantic similarity)
        # - Sparse search: Finds by keywords (BM25 algorithm)
        # - Reciprocal Rank Fusion: Combines both results intelligently
        # This gives the best of both worlds: meaning + keywords
        results = hybrid_search(query_embedding, query, top_k=15)
    else:
        # Dense search only: Uses semantic similarity
        # Good for conceptual questions but may miss specific terms
        results = search_documents(query_embedding, top_k=15)

    # ========================================================================
    # STEP 3: Extract chunks from search results
    # ========================================================================
    # Convert ChromaDB results format into our internal format
    initial_chunks = []
    if results['documents'] and results['documents'][0]:
        # Iterate through each retrieved document chunk
        for i, doc in enumerate(results['documents'][0]):
            # Get metadata (source file, page number, chunk ID)
            meta = results['metadatas'][0][i]
            # Store as tuple: (document_text, metadata, score)
            # Score is set to 1.0 as placeholder (will be updated by reranking)
            initial_chunks.append((doc, meta, 1.0))

    # ========================================================================
    # STEP 4: Rerank chunks by relevance (optional)
    # ========================================================================
    # Reranking improves answer quality by ensuring the most relevant chunks
    # are used, even if they weren't ranked highest by the initial search
    if use_reranker and initial_chunks:
        # Re-ranks chunks using cosine similarity with the query
        # This is a second pass to refine the results
        reranked_chunks = rerank_chunks(query_embedding, initial_chunks, top_k=7)
    else:
        # If reranking is disabled, just take the top 7 chunks as-is
        reranked_chunks = initial_chunks[:7]

    # ========================================================================
    # STEP 5: Build context string and citations
    # ========================================================================
    # Format the chunks into a context string that the AI can use
    # Also create a list of citations for the user to see
    context_text = ""
    citations = []
    
    if reranked_chunks:
        # Process each relevant chunk
        for doc, meta, score in reranked_chunks:
            # Extract source information
            source = meta.get('source', 'Unknown')  # Filename
            page = meta.get('page', 'Unknown')  # Page number
            
            # Format: Content + Source information
            # This format helps the AI understand where information came from
            context_line = f"Content: {doc}\nSource: {source} | Page: {page}\n\n"
            context_text += context_line
            
            # Create citation for user display
            citations.append(f"Source: {source} | Page: {page}")
    else:
        # No relevant chunks found
        context_text = "No relevant context found in documents."
    
    return context_text, citations

def rewrite_query(query, history, api_key):
    """
    THE QUERY REWRITER: Makes follow-up questions self-contained for search.
    
    In conversations, users often ask follow-up questions that reference
    previous context. For example:
    - User: "What is Diabetes?"
    - AI: "Diabetes is..."
    - User: "What about treatment?"  ← This needs context!
    
    This function rewrites the follow-up question to include the context,
    making it searchable: "What about treatment?" → "Treatment for Diabetes"
    
    How it works:
    1. Checks if there's conversation history
    2. If no history, returns the query as-is
    3. If history exists, uses GPT to rewrite the question
    4. Returns a self-contained search query
    
    Args:
        query (str): The current user question (may be a follow-up)
        history (list): Previous conversation messages
                       Format: [{"role": "user", "content": "..."}, ...]
        api_key (str): OpenAI API key for the rewriting model
    
    Returns:
        str: Rewritten query that's self-contained and searchable
        
    Example:
        Input:
            query = "What about treatment?"
            history = [
                {"role": "user", "content": "What is Diabetes?"},
                {"role": "assistant", "content": "Diabetes is a condition..."}
            ]
        
        Output:
            "Recommended treatment for Diabetes"
    
    Why This Matters:
        - Makes follow-up questions searchable
        - Improves retrieval quality in conversations
        - Enables natural conversation flow
    """
    # If no history, the query is already self-contained
    if not history:
        return query

    client = OpenAI(api_key=api_key)
    
    # ========================================================================
    # Format conversation history for the rewriter
    # ========================================================================
    history_text = ""
    # Only use last 3 conversation rounds for efficiency
    # This keeps the prompt manageable while maintaining recent context
    for msg in history[-3:]:
        # Determine role label
        role = "User" if msg['role'] == 'user' else "Assistant"
        # Truncate content to 200 chars to keep prompt size reasonable
        content = msg['content'][:200]
        history_text += f"{role}: {content}\n"

    # ========================================================================
    # Create prompt for query rewriting
    # ========================================================================
    REWRITE_PROMPT = f"""Given the following conversation history and a follow-up question, rewrite the follow-up question to be a standalone search query that can be used to find relevant documents. 

History:
{history_text}

Follow-up Question: {query}

Standalone Query:"""

    # ========================================================================
    # Call GPT to rewrite the query
    # ========================================================================
    response = client.chat.completions.create(
        model=CHAT_MODEL,  # GPT-3.5-Turbo
        messages=[{"role": "user", "content": REWRITE_PROMPT}]
    )
    
    # Extract and return the rewritten query
    rewritten = response.choices[0].message.content.strip()
    return rewritten

def generate_answer(query, api_key=None, history=[], use_hybrid_search=True, use_reranker=True, show_thinking=False):
    """
    THE CLINICAL ASSISTANT: Core function that generates answers using RAG.
    
    This is the main function that orchestrates the entire RAG pipeline:
    1. Rewrites the query if there's conversation history
    2. Retrieves relevant document chunks
    3. Generates an answer using GPT with the retrieved context
    4. Returns answer with citations
    
    The RAG (Retrieval-Augmented Generation) approach ensures:
    - Answers are grounded in actual documents (not hallucinated)
    - Sources are tracked and cited
    - Answers are accurate and verifiable
    
    Args:
        query (str): The user's question
        api_key (str, optional): OpenAI API key. If not provided, tries environment variable
        history (list, optional): Conversation history for context
                                 Format: [{"role": "user", "content": "..."}, ...]
        use_hybrid_search (bool): Enable hybrid search (default: True)
        use_reranker (bool): Enable reranking (default: True)
        show_thinking (bool): Show AI reasoning process (default: False)
    
    Returns:
        tuple: (answer, citations, thinking)
            - answer (str): The generated answer
            - citations (list): List of source citations
            - thinking (str or None): AI reasoning process if show_thinking=True
    
    Example:
        Input:
            query = "What are the contraindications?"
            history = []
            use_hybrid_search = True
            use_reranker = True
            show_thinking = False
        
        Output:
            (
                "Based on the document, contraindications include...",
                ["Source: guide.pdf | Page: 5"],
                None
            )
    
    Process Flow:
        1. Query Rewriting → Makes question searchable
        2. Document Retrieval → Finds relevant chunks
        3. Reranking → Refines results
        4. Answer Generation → GPT creates answer from context
        5. Response Formatting → Returns answer with citations
    """
    # ========================================================================
    # Validate API key
    # ========================================================================
    if not api_key:
        api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OpenAI API Key not found")

    client = OpenAI(api_key=api_key)

    # ========================================================================
    # STEP 1: Rewrite query for better search (if history exists)
    # ========================================================================
    # Makes follow-up questions self-contained
    # Example: "What about treatment?" → "Treatment for Diabetes"
    search_query = rewrite_query(query, history, api_key)
    
    # ========================================================================
    # STEP 2: Retrieve relevant document chunks
    # ========================================================================
    # This function:
    # - Searches documents (hybrid or dense)
    # - Reranks results (if enabled)
    # - Returns formatted context and citations
    context_text, citations = _get_context_and_citations(
        search_query, 
        api_key, 
        use_hybrid_search, 
        use_reranker
    )

    # ========================================================================
    # STEP 3: Prepare messages for GPT
    # ========================================================================
    messages = []
    
    # ========================================================================
    # System prompt: Defines the AI's role and behavior
    # ========================================================================
    # The system prompt is crucial - it tells GPT:
    # - What its role is (clinical assistant)
    # - What rules to follow (cite sources, use only context, etc.)
    # - How to format answers
    if show_thinking:
        # Version with thinking process enabled
        system_content = f"""You are ClinIQ, an AI assistant for healthcare professionals.

RULES:
- Answer ONLY using the provided context.
- SYNTHESIZE information from all relevant documents provided in the context.
- If documents contain different or complementary information on the same topic, include BOTH perspectives.
- Always cite sources as [Source: filename | Page: X].
- If the answer isn't in the context, say "I don't have that information in the uploaded documents".
- Use clear, professional medical terminology.
- Be concise but complete.
- Show your reasoning process step by step before providing the final answer.

CONTEXT:
{context_text}"""
    else:
        # Version without thinking process (faster, cleaner output)
        system_content = f"""You are ClinIQ, an AI assistant for healthcare professionals.

RULES:
- Answer ONLY using the provided context.
- SYNTHESIZE information from all relevant documents provided in the context.
- If documents contain different or complementary information on the same topic, include BOTH perspectives.
- Always cite sources as [Source: filename | Page: X].
- If the answer isn't in the context, say "I don't have that information in the uploaded documents".
- Use clear, professional medical terminology.
- Be concise but complete.

CONTEXT:
{context_text}"""

    # Add system message (defines AI behavior)
    messages.append({"role": "system", "content": system_content})
    
    # ========================================================================
    # Add conversation history for context
    # ========================================================================
    # This allows the AI to understand the conversation flow
    # Example: If user asked about "Diabetes" before, it knows what "it" refers to
    for msg in history:
        messages.append({"role": msg['role'], "content": msg['content']})
    
    # ========================================================================
    # Add the current question
    # ========================================================================
    # Format the question based on whether thinking is enabled
    final_query = query
    if show_thinking:
        # Request thinking process before answer
        final_query = f"Question: {query}\n\nFirst, think step-by-step. Then provide your final answer with inline citations.\n\nThinking process:"
    else:
        # Direct answer request
        final_query = f"Question: {query}\n\nAnswer with inline citations:"
        
    messages.append({"role": "user", "content": final_query})

    # ========================================================================
    # STEP 4: Generate answer using GPT
    # ========================================================================
    # Send the complete message history to GPT
    # GPT will:
    # - Read the system prompt (knows its role and rules)
    # - Review conversation history (understands context)
    # - Read the retrieved document chunks (has information to answer)
    # - Generate an answer based ONLY on the provided context
    response = client.chat.completions.create(
        model=DEFAULT_CHAT_MODEL,  # GPT-3.5-Turbo
        messages=messages,
        max_tokens=1000,  # Allow longer responses
        temperature=0.3   # Lower temperature for more consistent, focused responses
    )

    # Extract the generated answer
    answer = response.choices[0].message.content

    # ========================================================================
    # STEP 5: Parse and return response
    # ========================================================================
    if show_thinking:
        # Separate thinking process from final answer
        thinking, final_answer = parse_thinking_and_answer(answer)
        return final_answer, citations, thinking
    else:
        # Return answer with citations (no thinking)
        return answer, citations, None

def generate_answer_stream(query, api_key=None, history=[], use_hybrid_search=True, use_reranker=True, show_thinking=False):
    """
    Streaming version of generate_answer - sends answer in real-time chunks.
    
    This function works the same as generate_answer, but instead of waiting
    for the complete answer, it streams chunks as they're generated. This
    provides a better user experience with a typing effect.
    
    How streaming works:
    1. Same retrieval process as generate_answer
    2. Calls GPT with stream=True
    3. Yields answer chunks as they're generated
    4. Frontend receives chunks and displays them in real-time
    
    Args:
        Same as generate_answer()
    
    Yields:
        str: JSON strings containing answer chunks
            Format: '{"type": "content", "content": "chunk text"}'
            Or: '{"type": "metadata", "citations": [...]}'
    
    Example Usage:
        for chunk in generate_answer_stream("What is diabetes?"):
            # Process each chunk as it arrives
            data = json.loads(chunk)
            if data["type"] == "content":
                print(data["content"], end="")  # Print without newline
    
    Benefits:
        - Better UX: Users see answer appearing in real-time
        - Perceived faster response (don't wait for complete answer)
        - More engaging interaction
    """
    # Validate API key (same as generate_answer)
    if not api_key:
        api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OpenAI API Key not found")

    client = OpenAI(api_key=api_key)

    # Same retrieval process as generate_answer
    search_query = rewrite_query(query, history, api_key)
    context_text, citations = _get_context_and_citations(search_query, api_key, use_hybrid_search, use_reranker)

    # Prepare messages (same as generate_answer)
    messages = []
    
    # System prompt (same logic as generate_answer)
    if show_thinking:
        system_content = f"""You are ClinIQ, an AI assistant for healthcare professionals.

STRICT RULES:
- Answer ONLY using the provided context below
- If the question is NOT directly related to the context, you MUST say: "I don't have that information in the uploaded documents"
- Do NOT answer general knowledge questions - ONLY use the provided context
- SYNTHESIZE information from across ALL provided document fragments
- Always cite sources as [Source: filename | Page: X]
- Use clear, professional medical terminology
- Be concise but complete
- Show your reasoning process step by step before providing the final answer

CONTEXT:
{context_text}"""
    else:
        system_content = f"""You are ClinIQ, an AI assistant for healthcare professionals.

STRICT RULES:
- Answer ONLY using the provided context below
- If the question is NOT directly related to the context, you MUST say: "I don't have that information in the uploaded documents"
- Do NOT answer general knowledge questions - ONLY use the provided context
- SYNTHESIZE information from across ALL provided document fragments
- Always cite sources as [Source: filename | Page: X]
- Use clear, professional medical terminology
- Be concise but complete

CONTEXT:
{context_text}"""

    messages.append({"role": "system", "content": system_content})
    
    # Add history
    for msg in history:
        messages.append({"role": msg['role'], "content": msg['content']})
        
    # Format query based on whether thinking process is requested
    final_query = query
    if show_thinking:
        # Strict instructions to avoid repeating the answer in the thinking section
        final_query = (
            f"Question: {query}\n\n"
            "Instructions:\n"
            "1. First, provide your step-by-step reasoning as a numbered list\n"
            "2. After your reasoning, write EXACTLY this text on a new line: 'Final Answer:'\n"
            "3. Then provide your concise summary answer\n\n"
            "Example format:\n"
            "1. Point one\n"
            "2. Point two\n\n"
            "Final Answer: Your summary here\n\n"
            "Now answer the question:"
        )
    else:
        final_query = f"Question: {query}\n\nAnswer with inline citations:"

    messages.append({"role": "user", "content": final_query})

    # Send citations as metadata first (consistent with user request)
    import json
    yield json.dumps({"type": "metadata", "citations": citations})

    # ========================================================================
    # Stream the answer with robust buffering
    # ========================================================================
    # Call GPT with stream=True to get chunks as they're generated
    response = client.chat.completions.create(
        model=DEFAULT_CHAT_MODEL,
        messages=messages,
        stream=True,
        max_tokens=1000,  # Allow longer responses
        temperature=0.3    # Lower temperature for more consistent, focused responses
    )

    full_response = ""
    if show_thinking:
        # ROBUST BUFFERING: Detects the marker even if split across chunks
        full_buffer = ""
        found_final_answer = False
        sent_thinking_len = 0
        # Try multiple possible separators
        possible_markers = ["Final Answer:", "\n\n**\n", "\n**\n\n", "\n\n**"]
        found_marker = None
        
        for chunk in response:
            if chunk.choices and chunk.choices[0].delta.content:
                new_text = chunk.choices[0].delta.content
                full_buffer += new_text
                full_response += new_text
                
                if not found_final_answer:
                    # Check for any of the possible markers
                    for marker in possible_markers:
                        if marker in full_buffer:
                            found_marker = marker
                            break
                    
                    if found_marker:
                        # Marker FOUND!
                        found_final_answer = True
                        parts = full_buffer.split(found_marker, 1)
                        
                        # Send the remaining thinking text before the marker
                        thinking_to_send = parts[0][sent_thinking_len:].strip()
                        if thinking_to_send:
                            yield json.dumps({"type": "thinking", "content": thinking_to_send})
                        
                        # Send everything after the marker as final answer content
                        if parts[1].strip():
                            yield json.dumps({"type": "content", "content": parts[1]})
                    else:
                        # Marker NOT YET found.
                        # Send text that is "safe" (far enough from the end to not be a partial marker)
                        # Use longest possible marker length for safety
                        max_marker_len = max(len(m) for m in possible_markers)
                        safe_len = max(0, len(full_buffer) - max_marker_len - 5)
                        if safe_len > sent_thinking_len:
                            to_send = full_buffer[sent_thinking_len:safe_len]
                            yield json.dumps({"type": "thinking", "content": to_send})
                            sent_thinking_len = safe_len
                else:
                    # After marker, everything is content
                    yield json.dumps({"type": "content", "content": new_text})
        
        # FLUSH REMAINING BUFFER: Send any unsent content at the end of the stream
        if not found_final_answer and sent_thinking_len < len(full_buffer):
            # No "Final Answer:" marker found, send remaining buffer as thinking
            remaining = full_buffer[sent_thinking_len:].strip()
            if remaining:
                yield json.dumps({"type": "thinking", "content": remaining})
    else:
        # Simple mode: send everything as content
        for chunk in response:
            if chunk.choices and chunk.choices[0].delta.content:
                new_text = chunk.choices[0].delta.content
                full_response += new_text
                yield json.dumps({"type": "content", "content": new_text})

    # ========================================================================
    # CITATION CLEARING: If we find "I don't have that information", clear citations
    # ========================================================================
    no_info_phrases = [
        "i don't have that information",
        "don't have that information",
        "don't have information",
        "not mentioned in the provided context",
        "not mentioned in the context",
        "no information in the uploaded documents",
        "not found in the documents",
        "not available in the uploaded documents",
        "not directly related to the context",
        "cannot find",
        "no information about"
    ]
    if any(phrase in full_response.lower() for phrase in no_info_phrases):
        yield json.dumps({"type": "clear_citations"})

def parse_thinking_and_answer(response_text):
    """
    Separates the AI's thinking process from the final answer.
    
    When show_thinking=True, GPT generates both a reasoning process
    and a final answer. This function parses the response to separate them.
    
    How it works:
    1. Looks for common separators like "Final Answer:" or "Answer:"
    2. If found, splits on the separator
    3. If not found, tries to detect where thinking ends
    4. Returns (thinking, answer) tuple
    
    Args:
        response_text (str): The complete response from GPT
        
    Returns:
        tuple: (thinking, answer)
            - thinking (str): The reasoning process
            - answer (str): The final answer
            
    Example:
        Input:
            "Let me think about this...\n\nFinal Answer: The treatment is..."
        
        Output:
            ("Let me think about this...", "The treatment is...")
    """
    # Look for common separators between thinking and answer
    separators = ["\n\nFinal Answer:", "\n\nAnswer:", "\n\n**Final Answer:**", "\n\n**Answer:**"]

    # Try each separator
    for separator in separators:
        if separator in response_text:
            # Split on the separator
            parts = response_text.split(separator, 1)
            if len(parts) == 2:
                thinking = parts[0].strip()
                answer = parts[1].strip()
                return thinking, answer

    # If no clear separator found, try to detect where thinking ends
    lines = response_text.split('\n')
    if len(lines) > 1:
        # Look for lines that start with answer-like phrases
        for i, line in enumerate(lines):
            if line.strip().startswith(('The answer is', 'According to', 'Based on', 'The patient')):
                # Assume everything before this line is thinking
                thinking = '\n'.join(lines[:i]).strip()
                answer = '\n'.join(lines[i:]).strip()
                return thinking, answer

    # Fallback: treat everything as answer (no thinking detected)
    return "", response_text
