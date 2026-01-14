# 🏥 ClinIQ - Deep Technical Documentation & Architecture Guide

## 🏢 Stakeholder Summary (Non-Technical)
ClinIQ is an intelligent assistant designed to help healthcare professionals quickly find accurate information within their own clinical documents (Guidelines, Manuals, Protocols).

**How it works for you:**
1. **Upload**: You provide your PDF or Word documents. The system "reads" and organizes them.
2. **Search**: When you ask a question, the system uses "Hybrid Search"—a dual-check method that looks for both the *meaning* of your words and specific *keywords* (like drug names).
3. **Verify**: The assistant doesn't just give an answer; it shows you its **Thinking Process** so you can trust its logic, and provides **Direct Citations** (with links) to the exact page where it found the information.
4. **Memory**: The assistant now remembers what you talked about earlier. You can ask followup questions like "Tell me more about the treatment for that" without repeating yourself.

*This tool acts as a high-speed research assistant, ensuring that every answer is grounded in your verified clinical documents.*

---

ClinIQ is a high-precision AI Clinical Knowledge Assistant. This document provides a deep dive into the architectural decisions, code implementation, and the roadmap for scaling to an enterprise-grade solution.

---

## 🏛️ Architectural Reasoning: Why This Design?

The architecture of ClinIQ is built on the **Retrieval-Augmented Generation (RAG)** pattern, specifically optimized for the high-stakes clinical domain.

### 1. The RAG Pattern vs. Fine-tuning
**Choice**: RAG (Retrieval-Augmented Generation).
**Reasoning**: 
- **Verifiability**: Clinical decisions require citations. RAG provides direct links to source documents, which fine-tuned models cannot do reliably.
- **Dynamic Knowledge**: Clinical protocols change frequently. RAG allows for instant updates by simply replacing documents, whereas fine-tuning is expensive and slow.
- **Hallucination Mitigation**: By forcing the LLM to use only the provided context, we significantly reduce the risk of "invented" medical advice.

### 2. Hybrid Search: Dense + Sparse Retrieval
**Choice**: Combination of ChromaDB (Dense/Vector) and BM25 (Sparse/Keyword).
**Reasoning**:
- **Dense Search (Vector)**: Captures semantic meaning (e.g., "respiratory distress" matches "difficulty breathing"). Used via `text-embedding-3-small`.
- **Sparse Search (BM25)**: Captures exact clinical terminology and rare drug names (e.g., "Sjogren's" or "Rituximab") that might be "diluted" in a high-dimensional vector space.
- **Reciprocal Rank Fusion (RRF)**: We use RRF to merge these two lists, ensuring that a document that is both semantically relevant AND contains exact keywords rises to the top.

### 3. Reranking: The Precision Filter
**Choice**: Secondary similarity check after initial retrieval.
**Reasoning**:
- Initial search might retrieve 10 chunks based on broad relevance. Reranking performs a more compute-intensive comparison on just these 10 chunks to select the top 3. This ensures the LLM's context window is filled with only the highest-quality information, saving tokens and improving answer accuracy.

### 4. Step-by-Step Thinking Process
**Choice**: Mandatory Chain-of-Thought (CoT) prompting.
**Reasoning**:
- **Clinical Transparency**: Doctors need to know *why* an AI suggests a protocol.
- **Self-Correction**: Forcing the model to "think" before answering often leads it to catch its own errors in interpretation before generating the final clinical advice.

---

## 💻 Code Walkthrough: Data Flow

### A. Document Ingestion (`api.py` -> `document_processor.py`)
1. **Upload**: User uploads a PDF/Docx via the React frontend.
2. **Extraction**: `extract_text_from_pdf` (using `PyMuPDF`) extracts text and preserves page numbers.
3. **Chunking**: Text is broken into ~1000-character chunks with overlap. Overlap ensures that context isn't lost at the boundaries of chunks.
4. **Embedding**: Chunks are sent to OpenAI's `text-embedding-3-small`.
5. **Storage**: Vectors and metadata (filename, page) are stored in **ChromaDB**.

### B. Query Execution (`rag_pipeline.py` -> `vector_store.py`)
1. **Query Rewriting**: If chat history exists, the assistant first uses the LLM to rewrite the followup question into a self-contained search query. (e.g., "What about treatment?" -> "Recommended treatment for [Previously Mentioned Disease]").
2. **Query Embedding**: The rewritten query is converted into a vector.
3. **Hybrid Retrieval**:
   - `search_documents` gets semantic matches.
   - `bm25_search` gets keyword matches.
   - `reciprocal_rank_fusion` merges them.
4. **Reranking**: `rerank_chunks` re-evaluates the top candidates.
5. **LLM Synthesis**: The top chunks and the **entire conversation history** are provided to the LLM. The system prompt enforces clinical rules (Professional tone, "I don't know" if not found, mandatory citations).

---

## 🚀 Scaling Roadmap: Architecture & Implementation

To scale ClinIQ from a local tool to a hospital-wide system, the following upgrades are recommended:

### 1. Scaling the Architecture (Infrastructure)
- **Distributed Vector Database**: Replace local ChromaDB with **Qdrant** or **Weaviate** in a cluster configuration to handle millions of documents.
- **Asynchronous Processing**: Use **Celery + Redis** for document ingestion. Uploading a 500-page guideline should happen in the background, not blocking the user session.
- **Load Balancing**: Deploy the Flask API behind **NGINX** with multiple workers (Gunicorn/Uvicorn) across multiple containers.
- **Document Management Service**: Move file storage from local `/uploads` to **AWS S3** or **Google Cloud Storage** for persistence and scalability.

### 2. Scaling the Implementation (Features)
- **Multi-Document Reasoning**: Improve the pipeline to compare contraindications across multiple different uploaded drug manuals simultaneously.
- **Streaming Responses**: Fully implement Server-Sent Events (SSE) to show the answer as it generates, reducing perceived latency.
- **User Authentication**: Integrate **Supabase Auth** or **OAuth2** to allow individual doctors to have private, secure "knowledge silos".
- **Medical LLMs**: Experiment with domain-specific models like **Med-PaLM 2** or fine-tuned Llama-3 for deeper clinical reasoning.
- **Caching**: Implement **Redis caching** for common queries to avoid redundant LLM calls and reduce costs.

---

## 📂 Key Project Files
- `api.py`: The control center (Flask API).
- `utils/vector_store.py`: The indexing engine (ChromaDB + BM25).
- `utils/rag_pipeline.py`: The reasoning engine (RAG workflow).
- `frontend/src/`: Modern UI built with React/Vite.

---

