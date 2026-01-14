"""
Vector Store Module - Document Storage and Search System

This module handles all operations related to storing and searching documents:
1. ChromaDB Operations: Vector database for storing embeddings
2. Dense Search: Semantic similarity search using embeddings
3. Sparse Search: Keyword-based search using BM25 algorithm
4. Hybrid Search: Combines dense + sparse search using RRF
5. Reranking: Re-orders results by relevance using cosine similarity

The module implements a sophisticated search system that combines:
- Semantic understanding (dense search)
- Keyword matching (sparse search)
- Intelligent fusion (RRF)
- Relevance refinement (reranking)

This ensures the most relevant document chunks are retrieved for answering questions.
"""

import chromadb
from chromadb.config import Settings
import os
from rank_bm25 import BM25Okapi
import numpy as np
from typing import List, Dict, Any, Tuple
from sklearn.metrics.pairwise import cosine_similarity

# ============================================================================
# CHROMADB OPERATIONS
# ============================================================================

def initialize_chromadb():
    """
    Initializes ChromaDB - The Vector Database Storage System.
    
    ChromaDB is a vector database optimized for storing and searching embeddings.
    Think of it as a specialized database that:
    - Stores document chunks and their embeddings (vector representations)
    - Performs fast similarity searches
    - Maintains metadata (source file, page number, chunk ID)
    
    How it works:
    1. Creates or connects to a persistent database at ".chromadb" folder
    2. Creates or retrieves a collection named "cliniq_docs"
    3. Returns the collection for storing/querying documents
    
    What is a Vector Database?
        - Traditional databases: Search by exact matches (SQL WHERE clauses)
        - Vector databases: Search by similarity (find "similar" vectors)
        - Example: Query "heart attack" finds documents about "myocardial infarction"
                  because their embeddings are similar
    
    Returns:
        Collection: ChromaDB collection object for storing and querying documents
        
    Persistence:
        - Data is stored in ".chromadb" folder on disk
        - Survives application restarts
        - Can be cleared with clear_store() function
    """
    # Use persistent client - data is saved to disk
    # This means documents persist even after the application restarts
    client = chromadb.PersistentClient(path=".chromadb")
    
    # Get or create the collection
    # If it doesn't exist, ChromaDB creates it automatically
    # If it exists, ChromaDB retrieves it with all existing data
    collection = client.get_or_create_collection(name="cliniq_docs")
    
    return collection

def add_documents(collection, documents, embeddings, metadata):
    """
    Adds document chunks to the vector database.
    
    This function stores the processed document chunks so they can be searched later.
    Each chunk is stored with:
    - The original text (for display and context)
    - Its embedding vector (for similarity search)
    - Metadata (source file, page number, chunk ID)
    
    How it works:
    1. Generates unique IDs for each chunk (required by ChromaDB)
    2. Stores chunks, embeddings, and metadata in the collection
    3. ChromaDB indexes everything for fast retrieval
    
    Args:
        collection: ChromaDB collection object (from initialize_chromadb)
        documents (list): List of text chunks (strings)
        embeddings (list): List of embedding vectors (lists of floats)
                         Each embedding is 1536 numbers representing the text's meaning
        metadata (list): List of metadata dictionaries
                        Each dict contains: {"source": "filename.pdf", "page": 5, "chunk_id": 0}
    
    Example:
        Input:
            documents = ["Chunk 1 text...", "Chunk 2 text..."]
            embeddings = [[0.1, 0.2, ...], [0.3, 0.4, ...]]  # 1536 numbers each
            metadata = [{"source": "doc.pdf", "page": 1}, {"source": "doc.pdf", "page": 2}]
        
        Result:
            Both chunks are stored in ChromaDB and can be searched immediately
    
    Why Unique IDs?
        ChromaDB requires unique identifiers for each document.
        UUIDs ensure no conflicts even if the same document is uploaded multiple times.
    """
    # ChromaDB requires unique IDs for each document
    # Generate UUIDs (Universally Unique Identifiers) for each chunk
    import uuid
    ids = [str(uuid.uuid4()) for _ in range(len(documents))]
    
    # Add all chunks to the collection in one operation
    # This is efficient - ChromaDB handles indexing automatically
    collection.add(
        documents=documents,  # Original text chunks
        embeddings=embeddings,  # Vector representations
        metadatas=metadata,  # Source information
        ids=ids  # Unique identifiers
    )

def search_documents(query_embedding, top_k=3):
    """
    DENSE SEARCH: Finds documents by semantic meaning.
    
    This is semantic/semantic similarity search. It finds documents based on
    meaning, not just keywords. This is powerful because:
    - "Heart attack" and "myocardial infarction" are found together
    - "High blood pressure" and "hypertension" are treated as similar
    - Works even if different words are used
    
    How it works:
    1. Takes the query embedding (vector representation of the question)
    2. ChromaDB calculates similarity between query and all stored embeddings
    3. Returns the top_k most similar document chunks
    
    What is Dense Search?
        - Uses embeddings (dense vectors) to find similar content
        - Measures semantic similarity (meaning-based)
        - Example: Query "cardiac event" finds documents about "heart problems"
                  because their embeddings are close in vector space
    
    Args:
        query_embedding (list): Embedding vector of the query (1536 numbers)
        top_k (int): Number of results to return (default: 3)
    
    Returns:
        dict: ChromaDB results in format:
            {
                'documents': [[chunk1, chunk2, chunk3]],  # Nested list format
                'metadatas': [[meta1, meta2, meta3]],
                'distances': [[0.1, 0.2, 0.3]]  # Lower = more similar
            }
    
    Example:
        Query: "What are the symptoms?"
        Finds: Documents about "clinical manifestations", "patient presentation", etc.
               Even if they don't contain the exact word "symptoms"
    """
    # Connect to the persistent ChromaDB instance
    client = chromadb.PersistentClient(path=".chromadb")
    collection = client.get_collection(name="cliniq_docs")
    
    # Query the collection using the query embedding
    # ChromaDB performs vector similarity search internally
    results = collection.query(
        query_embeddings=[query_embedding],  # Query vector
        n_results=top_k  # Number of results to return
    )
    
    return results

def clear_store():
    """
    Clears all documents from the vector database.
    
    This function deletes the entire ChromaDB collection, removing:
    - All document chunks
    - All embeddings
    - All metadata
    - All search indexes
    
    Use Cases:
        - Starting a new session
        - Clearing sensitive data
        - Resetting after testing
    
    Note:
        - This is a destructive operation (cannot be undone)
        - Physical files in uploads/ folder are NOT deleted here
        - Use with caution in production environments
        - Also clears any API keys from environment variables for security
    """
    client = chromadb.PersistentClient(path=".chromadb")
    try:
        # Delete the entire collection
        client.delete_collection(name="cliniq_docs")
    except Exception as e:
        # Collection might not exist (already cleared or never created)
        print(f"Error deleting collection: {e}")
    
    # Clear API key from environment variables if it exists
    # This ensures API keys are not persisted after session ends
    import os
    if "OPENAI_API_KEY" in os.environ:
        del os.environ["OPENAI_API_KEY"]

# ============================================================================
# BM25 (SPARSE SEARCH) OPERATIONS
# ============================================================================

# Global variables for BM25 index
# These are stored in memory for fast keyword search
bm25_index = None  # The BM25 search index
bm25_documents = []  # List of all document texts
bm25_metadata = []  # List of all metadata (parallel to bm25_documents)

def initialize_bm25_index(collection):
    """
    Initializes BM25 index for keyword-based (sparse) search.
    
    BM25 (Best Matching 25) is a ranking algorithm used for keyword search.
    Unlike dense search (which finds by meaning), BM25 finds by exact keywords.
    This is perfect for:
    - Specific medication names (e.g., "Metformin")
    - Medical codes (e.g., "ICD-10")
    - Exact terminology that must match
    
    How BM25 Works:
        1. Tokenizes documents into words
        2. Calculates term frequency (how often words appear)
        3. Applies inverse document frequency (rare words score higher)
        4. Ranks documents by relevance to query keywords
    
    Why Both Dense and Sparse?
        - Dense search: Finds by meaning ("heart problem" finds "cardiac issue")
        - Sparse search: Finds by keywords ("Metformin" finds exact matches)
        - Hybrid: Combines both for comprehensive results
    
    Args:
        collection: ChromaDB collection containing all documents
    
    Process:
        1. Retrieves all documents from ChromaDB
        2. Tokenizes each document into words
        3. Builds BM25 index from tokenized documents
        4. Stores documents and metadata for retrieval
    
    Note:
        - Index is built in memory for fast searching
        - Must be rebuilt when new documents are added
        - Uses NLTK for tokenization (downloads punkt tokenizer if needed)
    """
    global bm25_index, bm25_documents, bm25_metadata

    try:
        # ====================================================================
        # STEP 1: Get all documents from ChromaDB
        # ====================================================================
        # Retrieve all stored documents and their metadata
        # This loads everything into memory for BM25 indexing
        results = collection.get(include=['documents', 'metadatas'])
        bm25_documents = results['documents']  # All document texts
        bm25_metadata = results['metadatas']  # All metadata (parallel array)

        if bm25_documents:
            # ================================================================
            # STEP 2: Tokenize documents for BM25
            # ================================================================
            # BM25 needs documents as lists of words (tokens)
            # Tokenization splits text into individual words
            import nltk
            from nltk.tokenize import word_tokenize
            
            # Download NLTK punkt tokenizer if not already available
            # This is a one-time download that tokenizes text into words
            try:
                nltk.data.find('tokenizers/punkt')
            except LookupError:
                nltk.download('punkt', quiet=True)

            # Tokenize each document into words
            # Lowercase everything for case-insensitive matching
            # Example: "Patient has Diabetes" → ["patient", "has", "diabetes"]
            tokenized_docs = [word_tokenize(doc.lower()) for doc in bm25_documents]
            
            # ================================================================
            # STEP 3: Build BM25 index
            # ================================================================
            # Create the BM25 index from tokenized documents
            # This index enables fast keyword search
            bm25_index = BM25Okapi(tokenized_docs)
        else:
            # No documents to index
            bm25_index = None
    except Exception as e:
        print(f"Error initializing BM25 index: {e}")
        bm25_index = None
        bm25_documents = []
        bm25_metadata = []

def bm25_search(query: str, top_k: int = 10) -> List[Tuple[str, Dict, float]]:
    """
    SPARSE SEARCH: Finds documents by exact keywords using BM25 algorithm.
    
    This function performs keyword-based search, which is excellent for:
    - Specific medication names: "Metformin", "Insulin"
    - Medical codes: "ICD-10", "CPT codes"
    - Exact terminology: "Type 2 Diabetes"
    - Technical terms that must match exactly
    
    How BM25 Scoring Works:
        - Term Frequency (TF): How often query words appear in document
        - Inverse Document Frequency (IDF): Rare words score higher
        - Document Length Normalization: Prevents bias toward long documents
        - Formula: score = TF * IDF (simplified)
    
    Why Sparse Search?
        - Dense search might miss exact keyword matches
        - Some queries need exact term matching (medication names, codes)
        - BM25 is proven effective for information retrieval
        - Fast and efficient for keyword queries
    
    Args:
        query (str): The search query (e.g., "Metformin side effects")
        top_k (int): Number of top results to return (default: 10)
    
    Returns:
        list: List of tuples, each containing:
            - document (str): The document chunk text
            - metadata (dict): Source information {"source": "...", "page": ...}
            - score (float): BM25 relevance score (higher = more relevant)
    
    Example:
        Query: "Metformin dosage"
        Finds: Documents containing both "Metformin" and "dosage"
        Scores: Higher scores for documents with more occurrences
    
    Note:
        - Returns empty list if BM25 index is not initialized
        - Only returns documents with positive scores (some relevance)
    """
    # Check if BM25 index is available
    if bm25_index is None or not bm25_documents:
        return []

    # Tokenize the query (same process as documents)
    import nltk
    from nltk.tokenize import word_tokenize
    try:
        nltk.data.find('tokenizers/punkt')
    except LookupError:
        nltk.download('punkt', quiet=True)

    # Convert query to lowercase and tokenize
    # Example: "Metformin dosage" → ["metformin", "dosage"]
    tokenized_query = word_tokenize(query.lower())

    # ========================================================================
    # Calculate BM25 scores for all documents
    # ========================================================================
    # get_scores() returns a score for each document
    # Higher score = more relevant to the query
    scores = bm25_index.get_scores(tokenized_query)

    # ========================================================================
    # Get top-k results
    # ========================================================================
    # argsort returns indices sorted by score (descending)
    # [::-1] reverses to get highest scores first
    # [:top_k] takes only the top k results
    top_indices = np.argsort(scores)[::-1][:top_k]

    # ========================================================================
    # Build results list
    # ========================================================================
    results = []
    for idx in top_indices:
        # Only include documents with positive scores
        # Zero or negative scores mean no relevance
        if scores[idx] > 0:
            results.append((
                bm25_documents[idx],  # Document text
                bm25_metadata[idx],  # Metadata (source, page, etc.)
                float(scores[idx])  # BM25 relevance score
            ))

    return results

# ============================================================================
# HYBRID SEARCH OPERATIONS
# ============================================================================

def reciprocal_rank_fusion(dense_results: List[Tuple[str, Dict, float]],
                          sparse_results: List[Tuple[str, Dict, float]],
                          k: int = 60) -> List[Tuple[str, Dict, float]]:
    """
    Combines dense and sparse search results using Reciprocal Rank Fusion (RRF).
    
    RRF is a powerful technique that merges results from different search methods
    without needing to normalize scores. It's particularly effective because:
    1. Doesn't require score normalization (dense and sparse scores are different scales)
    2. Gives equal weight to both search methods
    3. Promotes documents that appear in both result sets
    4. Is robust and widely used in information retrieval
    
    How RRF Works:
        - Each result gets a score based on its rank (position) in the results
        - Formula: score = 1 / (k + rank)
        - Rank 1 (first result) gets highest score
        - Rank 2 gets lower score, etc.
        - Results from both searches are combined
        - Documents appearing in both searches get scores from both
        - Final ranking is by combined RRF score
    
    Why RRF?
        - Dense search scores: 0.0 to 1.0 (similarity)
        - Sparse search scores: 0.0 to 10.0+ (BM25)
        - Can't directly compare or average these
        - RRF uses ranks instead, which are comparable
    
    Args:
        dense_results: Results from semantic search
                      List of (document, metadata, score) tuples
        sparse_results: Results from keyword search
                       List of (document, metadata, score) tuples
        k: RRF constant (default: 60)
           - Higher k = less difference between ranks
           - Lower k = more emphasis on top results
           - 60 is a standard value in research
    
    Returns:
        list: Combined and sorted results by RRF score
              Format: List of (document, metadata, rrf_score) tuples
    
    Example:
        Dense results: [doc1, doc2, doc3]
        Sparse results: [doc2, doc4, doc1]
        
        RRF combines them:
        - doc2: Appears in both (rank 2 dense, rank 1 sparse) → High RRF score
        - doc1: Appears in both (rank 1 dense, rank 3 sparse) → High RRF score
        - doc3: Only in dense → Lower score
        - doc4: Only in sparse → Lower score
        
        Final: [doc2, doc1, doc3, doc4] (sorted by RRF score)
    """
    # Dictionary to track RRF scores for each unique document
    # Key: Unique document identifier
    # Value: Document data and accumulated RRF score
    rrf_scores = {}

    # ========================================================================
    # Process dense search results
    # ========================================================================
    # Rank starts at 0 (first result)
    for rank, (doc, meta, score) in enumerate(dense_results):
        # Create unique key to identify this document
        # Uses first 100 chars of text + source + chunk_id
        # This ensures we can match the same document across both searches
        key = f"{doc[:100]}|{meta.get('source', '')}|{meta.get('chunk_id', '')}"
        
        # Initialize if this document hasn't been seen before
        if key not in rrf_scores:
            rrf_scores[key] = {'doc': doc, 'meta': meta, 'score': 0.0}
        
        # Add RRF score contribution from dense search
        # Formula: 1 / (k + rank)
        # Rank 0: 1/(60+0) = 0.0167
        # Rank 1: 1/(60+1) = 0.0164
        # Rank 2: 1/(60+2) = 0.0161
        rrf_scores[key]['score'] += 1.0 / (k + rank + 1)

    # ========================================================================
    # Process sparse search results
    # ========================================================================
    # Same process for BM25 results
    for rank, (doc, meta, score) in enumerate(sparse_results):
        key = f"{doc[:100]}|{meta.get('source', '')}|{meta.get('chunk_id', '')}"
        
        if key not in rrf_scores:
            rrf_scores[key] = {'doc': doc, 'meta': meta, 'score': 0.0}
        
        # Add RRF score contribution from sparse search
        # Documents appearing in both searches get scores from both
        rrf_scores[key]['score'] += 1.0 / (k + rank + 1)

    # ========================================================================
    # Sort by RRF score and return
    # ========================================================================
    # Sort all results by their combined RRF score (descending)
    sorted_results = sorted(rrf_scores.values(), key=lambda x: x['score'], reverse=True)
    
    # Convert back to tuple format
    return [(item['doc'], item['meta'], item['score']) for item in sorted_results]

def hybrid_search(query_embedding: List[float], query_text: str, top_k: int = 5,
                 alpha: float = 0.5) -> Dict[str, Any]:
    """
    Performs HYBRID SEARCH: Combines dense (semantic) and sparse (keyword) search.
    
    This is the most powerful search method, combining the best of both worlds:
    - Dense Search: Finds by meaning (semantic similarity)
    - Sparse Search: Finds by keywords (BM25)
    - RRF Fusion: Intelligently combines both result sets
    
    Why Hybrid Search?
        - Dense alone: Might miss exact keyword matches
        - Sparse alone: Might miss semantic variations
        - Hybrid: Gets comprehensive results from both methods
    
    Process:
        1. Perform dense search (semantic similarity)
        2. Perform sparse search (keyword matching)
        3. Combine results using Reciprocal Rank Fusion (RRF)
        4. Return top-k most relevant chunks
    
    Args:
        query_embedding (list): Embedding vector for semantic search (1536 numbers)
        query_text (str): Original query text for keyword search
        top_k (int): Number of results to return (default: 5)
        alpha (float): Weight parameter (currently not used, RRF handles weighting)
    
    Returns:
        dict: Results in ChromaDB format:
            {
                'documents': [[chunk1, chunk2, ...]],  # Nested list
                'metadatas': [[meta1, meta2, ...]],
                'distances': [[0.1, 0.2, ...]]  # Lower = more similar
            }
    
    Example:
        Query: "cardiac medication side effects"
        
        Dense search finds:
            - Documents about "heart drug adverse reactions" (semantic match)
            - Documents about "cardiovascular medicine complications"
        
        Sparse search finds:
            - Documents containing exact words "cardiac", "medication", "side effects"
        
        RRF combines both, prioritizing documents that appear in both result sets
    
    Performance:
        - Gets 2x top_k results from each method (for better RRF fusion)
        - RRF combines and selects best top_k
        - More comprehensive than either method alone
    """
    # Connect to ChromaDB
    client = chromadb.PersistentClient(path=".chromadb")
    collection = client.get_collection(name="cliniq_docs")

    # ========================================================================
    # Initialize BM25 index if needed
    # ========================================================================
    # BM25 index must be built before sparse search can work
    if bm25_index is None:
        initialize_bm25_index(collection)

    # ========================================================================
    # STEP 1: Dense Search (Semantic Similarity)
    # ========================================================================
    # Search using embeddings (vector similarity)
    # Gets more results (top_k * 2) to have more candidates for RRF
    dense_results_chroma = collection.query(
        query_embeddings=[query_embedding],  # Query embedding vector
        n_results=top_k * 2  # Get more results for better RRF fusion
    )

    # ========================================================================
    # Convert ChromaDB results to our internal format
    # ========================================================================
    dense_results = []
    if dense_results_chroma['documents'] and dense_results_chroma['documents'][0]:
        for i, doc in enumerate(dense_results_chroma['documents'][0]):
            meta = dense_results_chroma['metadatas'][0][i]
            # Approximate score based on rank (ChromaDB doesn't return exact scores)
            # Rank 0 (most similar) gets score 1.0, rank 1 gets 0.9, etc.
            score = 1.0 - (i * 0.1)
            dense_results.append((doc, meta, score))

    # ========================================================================
    # STEP 2: Sparse Search (Keyword Matching)
    # ========================================================================
    # Search using BM25 (keyword-based)
    # Also gets more results for better RRF fusion
    sparse_results = bm25_search(query_text, top_k=top_k * 2)

    # ========================================================================
    # STEP 3: Combine using Reciprocal Rank Fusion (RRF)
    # ========================================================================
    # RRF intelligently merges dense and sparse results
    # Documents appearing in both searches get higher scores
    combined_results = reciprocal_rank_fusion(dense_results, sparse_results)

    # ========================================================================
    # STEP 4: Take top-k results
    # ========================================================================
    # Select the best top_k chunks after RRF fusion
    top_results = combined_results[:top_k]

    # ========================================================================
    # STEP 5: Convert back to ChromaDB format
    # ========================================================================
    # Format results to match ChromaDB's expected structure
    # ChromaDB uses nested lists: [[doc1, doc2, ...]]
    documents = [[doc for doc, _, _ in top_results]] if top_results else [[]]
    metadatas = [[meta for _, meta, _ in top_results]] if top_results else [[]]
    # Convert RRF score to distance (ChromaDB uses distances, lower = more similar)
    distances = [[1.0 - score for _, _, score in top_results]] if top_results else [[]]

    return {
        'documents': documents,
        'metadatas': metadatas,
        'distances': distances
    }

# ============================================================================
# RERANKING OPERATIONS
# ============================================================================

def rerank_chunks(query_embedding: List[float], chunks: List[Tuple[str, Dict, float]],
                  top_k: int = 3) -> List[Tuple[str, Dict, float]]:
    """
    Re-ranks retrieved chunks by relevance using cosine similarity.
    
    Reranking is a refinement step that improves answer quality. Even after
    hybrid search, the initial ranking might not be perfect. Reranking:
    1. Creates fresh embeddings for the retrieved chunks
    2. Calculates cosine similarity with the query embedding
    3. Re-orders chunks by similarity score
    4. Returns the most relevant chunks
    
    Why Rerank?
        - Initial search might have ranking errors
        - Fresh similarity calculation is more accurate
        - Ensures the most relevant chunks are used for answering
        - Improves answer quality significantly
    
    How Cosine Similarity Works:
        - Measures angle between two vectors in high-dimensional space
        - Range: -1 to 1 (1 = identical, 0 = orthogonal, -1 = opposite)
        - Higher similarity = more relevant to the query
        - Formula: cos(θ) = (A · B) / (||A|| * ||B||)
    
    Args:
        query_embedding (list): Embedding vector of the query (1536 numbers)
        chunks (list): List of (document, metadata, score) tuples from initial search
        top_k (int): Number of top chunks to return after reranking (default: 3)
    
    Returns:
        list: Re-ranked chunks sorted by cosine similarity
              Format: List of (document, metadata, similarity_score) tuples
              Higher similarity_score = more relevant
    
    Example:
        Input chunks (from hybrid search):
            [chunk1 (score: 0.8), chunk2 (score: 0.9), chunk3 (score: 0.7)]
        
        After reranking (by cosine similarity):
            [chunk2 (similarity: 0.95), chunk1 (similarity: 0.88), chunk3 (similarity: 0.72)]
        
        Returns top 3: [chunk2, chunk1, chunk3] (reordered by relevance)
    
    Performance:
        - Makes additional API call to create embeddings for chunks
        - Adds latency but significantly improves answer quality
        - Typically processes 7-15 chunks, so cost is minimal
    """
    from openai import OpenAI
    import os

    # Validate input
    if not chunks:
        return []

    # ========================================================================
    # Extract documents and metadata
    # ========================================================================
    # Separate the chunks into components
    documents = [chunk[0] for chunk in chunks]  # Text chunks
    metadatas = [chunk[1] for chunk in chunks]  # Metadata (source, page, etc.)

    # ========================================================================
    # Get API key for creating embeddings
    # ========================================================================
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        # If no API key, can't rerank - return original order
        return chunks[:top_k]

    try:
        # ====================================================================
        # Create embeddings for all chunks
        # ====================================================================
        # This creates fresh embeddings for the retrieved chunks
        # These embeddings are then compared with the query embedding
        client = OpenAI(api_key=api_key)
        from utils.constants import EMBEDDING_MODEL
        response = client.embeddings.create(
            input=documents,  # All chunk texts
            model=EMBEDDING_MODEL  # text-embedding-3-small
        )
        # Extract embedding vectors
        chunk_embeddings = [data.embedding for data in response.data]

        # ====================================================================
        # Calculate cosine similarities
        # ====================================================================
        # Convert to numpy arrays for efficient computation
        query_embedding = np.array(query_embedding).reshape(1, -1)  # Shape: (1, 1536)
        chunk_embeddings = np.array(chunk_embeddings)  # Shape: (n_chunks, 1536)

        # Calculate cosine similarity between query and each chunk
        # Result: Array of similarity scores (one per chunk)
        # Higher score = more similar = more relevant
        similarities = cosine_similarity(query_embedding, chunk_embeddings)[0]

        # ====================================================================
        # Re-rank chunks by similarity
        # ====================================================================
        reranked_results = []
        for i, similarity in enumerate(similarities):
            reranked_results.append((
                documents[i],  # Original document text
                metadatas[i],  # Original metadata
                float(similarity)  # Cosine similarity score
            ))

        # ====================================================================
        # Sort by similarity score (descending)
        # ====================================================================
        # Most similar chunks come first
        reranked_results.sort(key=lambda x: x[2], reverse=True)

        # Return top-k most relevant chunks
        return reranked_results[:top_k]

    except Exception as e:
        # If reranking fails, fall back to original ranking
        print(f"Error in reranking: {e}")
        return chunks[:top_k]
