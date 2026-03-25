"""RAG (Retrieval-Augmented Generation) pipeline for question-answering."""

import os
from services.llm_service import create_llm_service
from utils.vector_store import search_documents, hybrid_search, rerank_chunks
from utils.constants import CHAT_MODEL, EMBEDDING_MODEL

DEFAULT_CHAT_MODEL = CHAT_MODEL
DEFAULT_EMBEDDING_MODEL = EMBEDDING_MODEL

def _get_context_and_citations(query, api_key, use_hybrid_search, use_reranker):
    """Retrieve relevant document chunks for the query."""
    llm_service = create_llm_service(api_key=api_key)
    query_embedding = llm_service.create_single_embedding(query)

    if use_hybrid_search:
        results = hybrid_search(query_embedding, query, top_k=15)
    else:
        results = search_documents(query_embedding, top_k=15)

    initial_chunks = []
    if results['documents'] and results['documents'][0]:
        for i, doc in enumerate(results['documents'][0]):
            meta = results['metadatas'][0][i]
            initial_chunks.append((doc, meta, 1.0))

    if use_reranker and initial_chunks:
        reranked_chunks = rerank_chunks(query_embedding, initial_chunks, top_k=7)
    else:
        reranked_chunks = initial_chunks[:7]

    context_text = ""
    citations = []

    if reranked_chunks:
        for doc, meta, score in reranked_chunks:
            source = meta.get('source', 'Unknown')
            page = meta.get('page', 'Unknown')

            context_line = f"Content: {doc}\nSource: {source} | Page: {page}\n\n"
            context_text += context_line
            citations.append(f"Source: {source} | Page: {page}")
    else:
        context_text = "No relevant context found in documents."

    return context_text, citations

def rewrite_query(query, history, api_key):
    """Rewrite follow-up questions to be self-contained."""
    if not history:
        return query

    llm_service = create_llm_service(api_key=api_key)

    history_text = ""
    for msg in history[-3:]:
        role = "User" if msg['role'] == 'user' else "Assistant"
        content = msg['content'][:200]
        history_text += f"{role}: {content}\n"

    REWRITE_PROMPT = f"""Given the following conversation history and a follow-up question, rewrite the follow-up question to be a standalone search query that can be used to find relevant documents.

History:
{history_text}

Follow-up Question: {query}

Standalone Query:"""

    messages = [{"role": "user", "content": REWRITE_PROMPT}]
    response = llm_service.create_chat_completion(messages=messages)

    rewritten = response.choices[0].message.content.strip()
    return rewritten

def generate_answer(query, api_key=None, history=[], use_hybrid_search=True, use_reranker=True, show_thinking=False):
    """Generate answer using RAG pipeline."""
    if not api_key:
        api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OpenAI API Key not found")

    llm_service = create_llm_service(api_key=api_key)

    search_query = rewrite_query(query, history, api_key)
    context_text, citations = _get_context_and_citations(
        search_query,
        api_key,
        use_hybrid_search,
        use_reranker
    )

    messages = []

    if show_thinking:
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

    messages.append({"role": "system", "content": system_content})

    for msg in history:
        messages.append({"role": msg['role'], "content": msg['content']})

    final_query = query
    if show_thinking:
        final_query = f"Question: {query}\n\nFirst, think step-by-step. Then provide your final answer with inline citations.\n\nThinking process:"
    else:
        final_query = f"Question: {query}\n\nAnswer with inline citations:"

    messages.append({"role": "user", "content": final_query})

    response = llm_service.create_chat_completion(
        messages=messages,
        temperature=0.3
    )

    answer = response.choices[0].message.content

    if show_thinking:
        thinking, final_answer = parse_thinking_and_answer(answer)
        return final_answer, citations, thinking
    else:
        return answer, citations, None

def generate_answer_stream(query, api_key=None, history=[], use_hybrid_search=True, use_reranker=True, show_thinking=False):
    """Generate answer with streaming response."""
    if not api_key:
        api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OpenAI API Key not found")

    llm_service = create_llm_service(api_key=api_key)

    search_query = rewrite_query(query, history, api_key)
    context_text, citations = _get_context_and_citations(search_query, api_key, use_hybrid_search, use_reranker)

    messages = []

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

    for msg in history:
        messages.append({"role": msg['role'], "content": msg['content']})

    final_query = query
    if show_thinking:
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

    import json
    yield json.dumps({"type": "metadata", "citations": citations})

    full_response = ""
    if show_thinking:
        full_buffer = ""
        found_final_answer = False
        sent_thinking_len = 0
        possible_markers = ["Final Answer:", "\n\n**\n", "\n**\n\n", "\n\n**"]
        found_marker = None

        for content_chunk in llm_service.create_chat_completion_stream(messages=messages, temperature=0.3):
            new_text = content_chunk
            full_buffer += new_text
            full_response += new_text

            if not found_final_answer:
                for marker in possible_markers:
                    if marker in full_buffer:
                        found_marker = marker
                        break

                if found_marker:
                    found_final_answer = True
                    parts = full_buffer.split(found_marker, 1)

                    thinking_to_send = parts[0][sent_thinking_len:].strip()
                    if thinking_to_send:
                        yield json.dumps({"type": "thinking", "content": thinking_to_send})

                    if parts[1].strip():
                        yield json.dumps({"type": "content", "content": parts[1]})
                else:
                    max_marker_len = max(len(m) for m in possible_markers)
                    safe_len = max(0, len(full_buffer) - max_marker_len - 5)
                    if safe_len > sent_thinking_len:
                        to_send = full_buffer[sent_thinking_len:safe_len]
                        yield json.dumps({"type": "thinking", "content": to_send})
                        sent_thinking_len = safe_len
            else:
                yield json.dumps({"type": "content", "content": new_text})

        if not found_final_answer and sent_thinking_len < len(full_buffer):
            remaining = full_buffer[sent_thinking_len:].strip()
            if remaining:
                yield json.dumps({"type": "thinking", "content": remaining})
    else:
        for content_chunk in llm_service.create_chat_completion_stream(messages=messages, temperature=0.3):
            new_text = content_chunk
            full_response += new_text
            yield json.dumps({"type": "content", "content": new_text})

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
    """Separate thinking process from final answer."""
    separators = ["\n\nFinal Answer:", "\n\nAnswer:", "\n\n**Final Answer:**", "\n\n**Answer:**"]

    for separator in separators:
        if separator in response_text:
            parts = response_text.split(separator, 1)
            if len(parts) == 2:
                thinking = parts[0].strip()
                answer = parts[1].strip()
                return thinking, answer

    lines = response_text.split('\n')
    if len(lines) > 1:
        for i, line in enumerate(lines):
            if line.strip().startswith(('The answer is', 'According to', 'Based on', 'The patient')):
                thinking = '\n'.join(lines[:i]).strip()
                answer = '\n'.join(lines[i:]).strip()
                return thinking, answer

    return "", response_text
