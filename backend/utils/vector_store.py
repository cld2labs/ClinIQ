"""Vector store operations for document storage and retrieval."""

import chromadb
from chromadb.config import Settings
import os
from rank_bm25 import BM25Okapi
import numpy as np
from typing import List, Dict, Any, Tuple
from sklearn.metrics.pairwise import cosine_similarity

def initialize_chromadb():
    """Initialize ChromaDB persistent client and collection."""
    client = chromadb.PersistentClient(path=".chromadb")
    collection = client.get_or_create_collection(name="cliniq_docs")
    return collection

def add_documents(collection, documents, embeddings, metadata):
    """Add document chunks to the vector database."""
    import uuid
    ids = [str(uuid.uuid4()) for _ in range(len(documents))]

    collection.add(
        documents=documents,
        embeddings=embeddings,
        metadatas=metadata,
        ids=ids
    )

def search_documents(query_embedding, top_k=3):
    """Search documents using semantic similarity (dense search)."""
    client = chromadb.PersistentClient(path=".chromadb")
    collection = client.get_collection(name="cliniq_docs")

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k
    )

    return results

def clear_store():
    """Clear all documents from the vector database."""
    client = chromadb.PersistentClient(path=".chromadb")
    try:
        client.delete_collection(name="cliniq_docs")
    except Exception as e:
        print(f"Error deleting collection: {e}")

    import os
    if "OPENAI_API_KEY" in os.environ:
        del os.environ["OPENAI_API_KEY"]

bm25_index = None
bm25_documents = []
bm25_metadata = []

def initialize_bm25_index(collection):
    """Initialize BM25 index for keyword-based search."""
    global bm25_index, bm25_documents, bm25_metadata

    try:
        results = collection.get(include=['documents', 'metadatas'])
        bm25_documents = results['documents']
        bm25_metadata = results['metadatas']

        if bm25_documents:
            import nltk
            from nltk.tokenize import word_tokenize

            try:
                nltk.data.find('tokenizers/punkt')
            except LookupError:
                nltk.download('punkt', quiet=True)

            tokenized_docs = [word_tokenize(doc.lower()) for doc in bm25_documents]
            bm25_index = BM25Okapi(tokenized_docs)
        else:
            bm25_index = None
    except Exception as e:
        print(f"Error initializing BM25 index: {e}")
        bm25_index = None
        bm25_documents = []
        bm25_metadata = []

def bm25_search(query: str, top_k: int = 10) -> List[Tuple[str, Dict, float]]:
    """Search documents using BM25 keyword matching (sparse search)."""
    if bm25_index is None or not bm25_documents:
        return []

    import nltk
    from nltk.tokenize import word_tokenize
    try:
        nltk.data.find('tokenizers/punkt')
    except LookupError:
        nltk.download('punkt', quiet=True)

    tokenized_query = word_tokenize(query.lower())
    scores = bm25_index.get_scores(tokenized_query)
    top_indices = np.argsort(scores)[::-1][:top_k]

    results = []
    for idx in top_indices:
        if scores[idx] > 0:
            results.append((
                bm25_documents[idx],
                bm25_metadata[idx],
                float(scores[idx])
            ))

    return results

def reciprocal_rank_fusion(dense_results: List[Tuple[str, Dict, float]],
                          sparse_results: List[Tuple[str, Dict, float]],
                          k: int = 60) -> List[Tuple[str, Dict, float]]:
    """Combine dense and sparse search results using Reciprocal Rank Fusion."""
    rrf_scores = {}

    for rank, (doc, meta, score) in enumerate(dense_results):
        key = f"{doc[:100]}|{meta.get('source', '')}|{meta.get('chunk_id', '')}"

        if key not in rrf_scores:
            rrf_scores[key] = {'doc': doc, 'meta': meta, 'score': 0.0}

        rrf_scores[key]['score'] += 1.0 / (k + rank + 1)

    for rank, (doc, meta, score) in enumerate(sparse_results):
        key = f"{doc[:100]}|{meta.get('source', '')}|{meta.get('chunk_id', '')}"

        if key not in rrf_scores:
            rrf_scores[key] = {'doc': doc, 'meta': meta, 'score': 0.0}

        rrf_scores[key]['score'] += 1.0 / (k + rank + 1)

    sorted_results = sorted(rrf_scores.values(), key=lambda x: x['score'], reverse=True)
    return [(item['doc'], item['meta'], item['score']) for item in sorted_results]

def hybrid_search(query_embedding: List[float], query_text: str, top_k: int = 5,
                 alpha: float = 0.5) -> Dict[str, Any]:
    """Perform hybrid search combining dense and sparse methods."""
    client = chromadb.PersistentClient(path=".chromadb")
    collection = client.get_collection(name="cliniq_docs")

    if bm25_index is None:
        initialize_bm25_index(collection)

    dense_results_chroma = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k * 2
    )

    dense_results = []
    if dense_results_chroma['documents'] and dense_results_chroma['documents'][0]:
        for i, doc in enumerate(dense_results_chroma['documents'][0]):
            meta = dense_results_chroma['metadatas'][0][i]
            score = 1.0 - (i * 0.1)
            dense_results.append((doc, meta, score))

    sparse_results = bm25_search(query_text, top_k=top_k * 2)
    combined_results = reciprocal_rank_fusion(dense_results, sparse_results)
    top_results = combined_results[:top_k]

    documents = [[doc for doc, _, _ in top_results]] if top_results else [[]]
    metadatas = [[meta for _, meta, _ in top_results]] if top_results else [[]]
    distances = [[1.0 - score for _, _, score in top_results]] if top_results else [[]]

    return {
        'documents': documents,
        'metadatas': metadatas,
        'distances': distances
    }

def rerank_chunks(query_embedding: List[float], chunks: List[Tuple[str, Dict, float]],
                  top_k: int = 3) -> List[Tuple[str, Dict, float]]:
    """Re-rank retrieved chunks using cosine similarity."""
    import os

    if not chunks:
        return []

    documents = [chunk[0] for chunk in chunks]
    metadatas = [chunk[1] for chunk in chunks]

    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        return chunks[:top_k]

    try:
        from services.llm_service import create_llm_service
        llm_service = create_llm_service(api_key=api_key)

        chunk_embeddings = llm_service.create_embeddings(documents)

        query_embedding = np.array(query_embedding).reshape(1, -1)
        chunk_embeddings = np.array(chunk_embeddings)

        similarities = cosine_similarity(query_embedding, chunk_embeddings)[0]

        reranked_results = []
        for i, similarity in enumerate(similarities):
            reranked_results.append((
                documents[i],
                metadatas[i],
                float(similarity)
            ))

        reranked_results.sort(key=lambda x: x[2], reverse=True)
        return reranked_results[:top_k]

    except Exception as e:
        print(f"Error in reranking: {e}")
        return chunks[:top_k]
