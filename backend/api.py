"""
ClinIQ Backend API - Flask REST API Server

This is the main backend server that handles:
1. Document uploads and processing
2. Question answering using RAG (Retrieval-Augmented Generation)
3. Knowledge base management
4. Health checks and status monitoring

The API uses Flask framework and communicates with the React frontend via REST endpoints.
All document processing, vector storage, and AI interactions happen here.
"""

from flask import Flask, request, jsonify, Response, send_from_directory
from flask_cors import CORS
import os
import logging
import atexit
import threading
import uuid
import time
from werkzeug.utils import secure_filename
from dotenv import load_dotenv
from utils.document_processor import extract_text_from_pdf, extract_text_from_docx, chunk_text, create_embeddings
from utils.vector_store import initialize_chromadb, add_documents, clear_store, initialize_bm25_index
from utils.rag_pipeline import generate_answer, generate_answer_stream, DEFAULT_CHAT_MODEL, DEFAULT_EMBEDDING_MODEL

# ============================================================================
# LOGGING CONFIGURATION
# ============================================================================
# Setup logging to track what the application is doing
# This helps with debugging and monitoring the application's behavior
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Load environment variables from .env file (if it exists)
# This allows us to store sensitive information like API keys outside the code
load_dotenv()

# ============================================================================
# FLASK APPLICATION SETUP
# ============================================================================
# Create the Flask application instance
# This is the main WSGI application that handles HTTP requests
app = Flask(__name__)

# Configure Flask to use UTF-8 encoding for JSON responses
# This ensures emojis and Unicode characters are properly handled
app.config['JSON_AS_ASCII'] = False
app.config['JSONIFY_MIMETYPE'] = 'application/json; charset=utf-8'

# Enable CORS (Cross-Origin Resource Sharing)
# This allows the React frontend (running on port 3000) to make requests
# to this backend API (running on port 5000) without browser security errors
CORS(app)

# ============================================================================
# APPLICATION CONFIGURATION
# ============================================================================
# Folder where uploaded documents will be stored on the server
# This allows users to download/view original files when clicking citations
UPLOAD_FOLDER = 'uploads'

# File types that are allowed to be uploaded
# Currently supports: PDF, Word documents (.docx), and plain text files
ALLOWED_EXTENSIONS = {'pdf', 'docx', 'txt'}

# Maximum file size allowed for upload (50 megabytes)
# This prevents users from uploading extremely large files that could crash the server
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB

# Create the uploads directory if it doesn't exist
# This ensures the folder is available when users try to upload files
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# ============================================================================
# STARTUP INITIALIZATION
# ============================================================================
# Clear the knowledge base when the application starts
# This ensures each session starts fresh without leftover data from previous sessions
# In a production environment, you might want to remove this and persist data
logger.info("Starting fresh session: Clearing knowledge base.")
clear_store()

# ============================================================================
# CLEANUP HANDLERS
# ============================================================================

def cleanup_on_shutdown():
    """
    Cleanup function that runs when the application shuts down.
    
    Security measure to ensure API keys are not left in memory.
    Clears OpenAI API key from environment variables when app terminates.
    """
    if "OPENAI_API_KEY" in os.environ:
        del os.environ["OPENAI_API_KEY"]
        logger.info("Cleared API key from environment on shutdown")

# Register cleanup function to run when app terminates
atexit.register(cleanup_on_shutdown)

# ============================================================================
# JOB TRACKING STORE
# ============================================================================
# Stores the status of background document processing jobs
# job_id -> {"status": "processing"|"completed"|"failed", "message": "...", "chunks": 0, "files": []}
processing_jobs = {}

@app.teardown_appcontext
def teardown_request(exception=None):
    """
    Teardown handler that runs after each request.
    
    Security measure to ensure API keys don't persist between requests.
    This clears any API key that might have been set during request processing.
    """
    if "OPENAI_API_KEY" in os.environ:
        del os.environ["OPENAI_API_KEY"]

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def allowed_file(filename):
    """
    Validates if an uploaded file has an allowed extension.
    
    This security check ensures only supported file types can be uploaded,
    preventing potential security issues from malicious file uploads.
    
    Args:
        filename (str): The name of the file to check
        
    Returns:
        bool: True if the file extension is allowed, False otherwise
        
    Example:
        allowed_file("document.pdf") -> True
        allowed_file("script.exe") -> False
    """
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# ============================================================================
# API ENDPOINTS
# ============================================================================

@app.route('/api/health', methods=['GET'])
def health_check():
    """
    Health Check Endpoint
    
    A simple endpoint to verify that the backend server is running and responsive.
    This is useful for:
    - Monitoring tools to check if the service is alive
    - Docker health checks
    - Frontend to verify backend connectivity
    
    Returns:
        JSON response with status "healthy" and HTTP 200 status code
        
    Example Response:
        {"status": "healthy"}
    """
    return jsonify({"status": "healthy"}), 200

@app.route('/api/files/<filename>', methods=['GET'])
def serve_file(filename):
    """
    File Serving Endpoint
    
    Serves the original uploaded document files so users can view/download them
    when clicking on citations in the chat interface.
    
    This endpoint allows the frontend to display the original document
    that a citation refers to, providing transparency and verification.
    
    Args:
        filename (str): The name of the file to serve (from URL path)
        
    Returns:
        File content if found, or 404 error if file doesn't exist
        
    Security Note:
        Uses secure_filename() to prevent directory traversal attacks
    """
    try:
        # send_from_directory safely serves files from a specific directory
        # It prevents directory traversal attacks (e.g., ../../../etc/passwd)
        return send_from_directory(UPLOAD_FOLDER, filename)
    except Exception as e:
        logger.error(f"Error serving file {filename}: {str(e)}")
        return jsonify({"error": "File not found"}), 404

def process_documents_background(job_id, file_paths, api_key):
    """
    Background worker that handles the heavy document processing:
    text extraction, chunking, embedding, and indexing.
    """
    try:
        processing_jobs[job_id] = {
            "status": "processing",
            "message": "Extracting text and creating embeddings...",
            "chunks": 0,
            "files": []
        }
        
        global_chunk_counter = 0
        processed_files = []
        collection = initialize_chromadb()
        
        for file_path in file_paths:
            filename = os.path.basename(file_path)
            file_chunks = []
            file_metadata = []
            
            with open(file_path, 'rb') as f:
                if filename.endswith('.pdf'):
                    pages_data = extract_text_from_pdf(f)
                elif filename.endswith('.docx'):
                    text = extract_text_from_docx(f)
                    pages_data = [(text, 1)]
                else:
                    f.seek(0)
                    text = str(f.read(), "utf-8")
                    pages_data = [(text, 1)]
            
            for text, page_num in pages_data:
                if not text or not text.strip():
                    continue
                
                page_chunks = chunk_text(text)
                for chunk in page_chunks:
                    file_chunks.append(chunk)
                    file_metadata.append({
                        "source": filename,
                        "page": page_num,
                        "chunk_id": global_chunk_counter
                    })
                    global_chunk_counter += 1
            
            if file_chunks:
                embeddings = create_embeddings(file_chunks, api_key)
                add_documents(collection, file_chunks, embeddings, file_metadata)
                processed_files.append(filename)
        
        if not processed_files:
            processing_jobs[job_id].update({
                "status": "failed",
                "error": "No text could be extracted from the uploaded documents"
            })
            return

        initialize_bm25_index(collection)
        
        processing_jobs[job_id].update({
            "status": "completed",
            "message": f"Successfully processed {len(processed_files)} documents",
            "chunks": global_chunk_counter,
            "files": processed_files
        })
        
    except Exception as e:
        logger.error(f"Background upload error for job {job_id}: {str(e)}", exc_info=True)
        processing_jobs[job_id].update({
            "status": "failed",
            "error": str(e)
        })

@app.route('/api/upload', methods=['POST'])
def upload_document():
    """
    STAY-RESPONSIVE UPLOAD ENDPOINT
    Saves the files then kicks off background processing.
    """
    try:
        if 'file' not in request.files:
            return jsonify({"error": "No file provided"}), 400
        
        files = request.files.getlist('file')
        api_key = request.form.get('api_key', '')
        
        if not files or all(f.filename == '' for f in files):
            return jsonify({"error": "No files selected"}), 400
        
        api_key = api_key.strip() if api_key else ''
        if not api_key or len(api_key) < 10 or not api_key.startswith('sk-'):
            return jsonify({"error": "Valid OpenAI API key is required"}), 400
        
        job_id = str(uuid.uuid4())
        saved_file_paths = []
        
        for file in files:
            if file.filename == '' or not allowed_file(file.filename):
                continue
                
            filename = secure_filename(file.filename)
            file_path = os.path.join(UPLOAD_FOLDER, filename)
            file.save(file_path)
            saved_file_paths.append(file_path)
        
        if not saved_file_paths:
             return jsonify({"error": "No valid files were uploaded"}), 400

        # Start background processing
        thread = threading.Thread(
            target=process_documents_background, 
            args=(job_id, saved_file_paths, api_key)
        )
        thread.daemon = True # Ensure thread closes with main app
        thread.start()
        
        return jsonify({
            "success": True,
            "job_id": job_id,
            "message": "Files uploaded successfully. Processing started in background."
        }), 202 # 202 Accepted
        
    except Exception as e:
        logger.error(f"Upload start error: {str(e)}", exc_info=True)
        return jsonify({"error": str(e)}), 500

@app.route('/api/upload/status/<job_id>', methods=['GET'])
def get_upload_status(job_id):
    """Checks the status of a background processing job."""
    job = processing_jobs.get(job_id)
    if not job:
        return jsonify({"error": "Job not found"}), 404
    return jsonify(job), 200

@app.route('/api/query', methods=['POST'])
def query_documents():
    """
    Query Documents Endpoint - THE QUESTION ANSWERING SYSTEM
    
    This is the core endpoint that handles user questions. It implements
    the RAG (Retrieval-Augmented Generation) pipeline:
    
    1. RECEIVES QUESTION: Gets the user's question from the frontend
    2. REWRITES QUERY: If there's conversation history, rewrites the question
       to be self-contained (e.g., "What about treatment?" -> "Treatment for Diabetes")
    3. SEARCHES DOCUMENTS: Uses hybrid search to find relevant document chunks
       - Dense search: Finds by meaning (semantic similarity)
       - Sparse search: Finds by keywords (BM25)
       - Combines both using Reciprocal Rank Fusion (RRF)
    4. RERANKS RESULTS: Re-orders results by relevance using cosine similarity
    5. GENERATES ANSWER: Sends question + relevant chunks to GPT-3.5-Turbo
    6. RETURNS ANSWER: Sends back the answer with source citations
    
    Request Format:
        JSON body with:
            - query: The user's question (string)
            - api_key: OpenAI API key (string)
            - history: Optional conversation history (array of messages)
            - use_hybrid_search: Whether to use hybrid search (boolean, default: True)
            - use_reranker: Whether to rerank results (boolean, default: True)
            - show_thinking: Whether to show AI reasoning process (boolean, default: True)
            - stream: Whether to stream the response (boolean, default: False)
    
    Returns:
        JSON response with:
            - answer: The generated answer (string)
            - citations: List of source citations (array of strings)
            - thinking: AI reasoning process (string, if show_thinking is True)
            
    OR (if stream=True):
        Server-Sent Events (SSE) stream with chunks of the answer
        
    Error Responses:
        - 400: Missing query or API key
        - 500: Server error during processing
        
    Example Request:
        {
            "query": "What are the side effects of this medication?",
            "api_key": "sk-...",
            "use_hybrid_search": true,
            "use_reranker": true,
            "show_thinking": false
        }
        
    Example Response:
        {
            "answer": "Based on the document, the side effects include...",
            "citations": [
                "Source: medication_guide.pdf | Page: 5",
                "Source: medication_guide.pdf | Page: 6"
            ]
        }
    """
    try:
        # Get JSON data from request body
        data = request.json
        if not data:
            return jsonify({"error": "No data provided"}), 400
            
        # Extract parameters from request
        query = data.get('query', '')  # User's question
        api_key = data.get('api_key', '')  # OpenAI API key
        # Defaults are set to True for better search quality
        use_hybrid_search = data.get('use_hybrid_search', True)  # Enable hybrid search
        use_reranker = data.get('use_reranker', True)  # Enable reranking
        show_thinking = data.get('show_thinking', True)  # Show AI reasoning
        stream = data.get('stream', False)  # Stream response or return all at once
        
        logger.info(f"Processing query (stream={stream}): {query}")
        
        # Validate required parameters
        if not query:
            return jsonify({"error": "Query is required"}), 400
        
        # Validate API key is provided and has minimum length
        api_key = api_key.strip() if api_key else ''
        if not api_key or len(api_key) < 10 or not api_key.startswith('sk-'):
            logger.warning(f"Invalid API key in query: length={len(api_key)}, starts_with_sk={api_key.startswith('sk-') if api_key else False}")
            return jsonify({"error": "Valid OpenAI API key is required (must start with 'sk-')"}), 401
        
        # ================================================================
        # STREAMING MODE: Send answer in real-time chunks
        # ================================================================
        if (stream):
            def sse_stream():
                """
                Server-Sent Events (SSE) generator function.
                Yields answer chunks as they're generated by the AI.
                This provides a real-time typing effect in the frontend.
                """
                try:
                    # Generate answer with streaming enabled
                    for chunk in generate_answer_stream(
                        query,
                        api_key=api_key,
                        history=data.get('history', []),  # Conversation history
                        use_hybrid_search=use_hybrid_search,
                        use_reranker=use_reranker,
                        show_thinking=show_thinking
                    ):
                        # Format as SSE (Server-Sent Events)
                        # Frontend receives chunks and displays them in real-time
                        yield f"data: {chunk}\n\n"
                except Exception as stream_err:
                    logger.error(f"Stream error: {str(stream_err)}")
                    # Send error as SSE event
                    yield f"data: {{\"error\": \"{str(stream_err)}\"}}\n\n"

            # Return streaming response
            # mimetype='text/event-stream' tells the browser this is an SSE stream
            # charset=utf-8 ensures proper encoding of Unicode characters (emojis)
            return Response(sse_stream(), mimetype='text/event-stream; charset=utf-8')

        # ================================================================
        # NON-STREAMING MODE: Generate complete answer and return
        # ================================================================
        # Generate answer using the RAG pipeline
        # This function handles:
        # - Query rewriting (if history exists)
        # - Document search (hybrid or dense)
        # - Reranking (if enabled)
        # - Answer generation with GPT-3.5-Turbo
        result = generate_answer(
            query,
            api_key=api_key,
            history=data.get('history', []),  # Previous conversation messages
            use_hybrid_search=use_hybrid_search,
            use_reranker=use_reranker,
            show_thinking=show_thinking
        )
        
        # Format response based on whether thinking process is shown
        if show_thinking:
            # If thinking is enabled, result contains: (answer, citations, thinking)
            answer, citations, thinking = result
            return jsonify({
                "answer": answer,  # Final answer
                "citations": citations,  # Source citations
                "thinking": thinking  # AI reasoning process
            }), 200
        else:
            # If thinking is disabled, result contains: (answer, citations, None)
            answer, citations, _ = result
            return jsonify({
                "answer": answer,
                "citations": citations
            }), 200
        
    except Exception as e:
        # Log full error details for debugging
        logger.error(f"Error in query_documents: {str(e)}", exc_info=True)
        return jsonify({"error": str(e)}), 500

@app.route('/api/clear', methods=['POST'])
def clear_documents():
    """
    Clear Knowledge Base Endpoint
    
    Removes all uploaded documents and their embeddings from the system.
    This effectively resets the knowledge base to an empty state.
    
    Use Cases:
        - Starting a new session with different documents
        - Clearing sensitive data
        - Resetting after testing
        
    What it does:
        1. Deletes the ChromaDB collection (removes all embeddings and chunks)
        2. Deletes all files from the uploads folder
        3. Resets the BM25 index
        4. Clears OpenAI API key from environment variables (security)
        
    Returns:
        JSON response with success status
        
    Example Response:
        {
            "success": true,
            "message": "Knowledge base and files cleared"
        }
    """
    try:
        # Clear the vector database (ChromaDB collection)
        # This removes all document chunks, embeddings, and metadata
        clear_store()
        
        # Also delete the physical files from the uploads folder
        # This ensures no files remain on the server
        for f in os.listdir(UPLOAD_FOLDER):
            file_path = os.path.join(UPLOAD_FOLDER, f)
            # Only delete files, not directories
            if os.path.isfile(file_path):
                os.remove(file_path)
        
        return jsonify({"success": True, "message": "Knowledge base and files cleared"}), 200
    except Exception as e:
        logger.error(f"Error in clear_documents: {str(e)}", exc_info=True)
        return jsonify({"error": str(e)}), 500

@app.route('/api/status', methods=['GET'])
def get_status():
    """
    Status Check Endpoint
    
    Returns the current status of the knowledge base and system configuration.
    This helps the frontend know:
    - Whether documents have been uploaded
    - How many documents are in the system
    - Which AI models are being used
    
    Returns:
        JSON response with:
            - has_documents: Boolean indicating if any documents exist
            - document_count: Number of document chunks in the database
            - chat_model: AI model used for answering questions
            - embedding_model: AI model used for creating embeddings
            
    Example Response:
        {
            "has_documents": true,
            "document_count": 45,
            "chat_model": "gpt-3.5-turbo",
            "embedding_model": "text-embedding-3-small"
        }
    """
    try:
        # Import ChromaDB client to check collection status
        from chromadb import PersistentClient
        
        # Connect to the persistent ChromaDB instance
        client = PersistentClient(path=".chromadb")
        
        # Initialize status data with defaults
        status_data = {
            "has_documents": False,  # No documents by default
            "document_count": 0,  # Zero chunks by default
            "chat_model": DEFAULT_CHAT_MODEL,  # Model used for Q&A
            "embedding_model": DEFAULT_EMBEDDING_MODEL  # Model used for embeddings
        }
        
        try:
            # Try to get the collection
            collection = client.get_collection(name="cliniq_docs")
            
            # Count documents in the collection
            count = collection.count()
            status_data["has_documents"] = count > 0
            status_data["document_count"] = count
        except Exception:
            # Collection doesn't exist yet (no documents uploaded)
            # This is normal and not an error
            pass
            
        return jsonify(status_data), 200
    except Exception as e:
        logger.error(f"Error in get_status: {str(e)}", exc_info=True)
        return jsonify({"error": str(e)}), 500

# ============================================================================
# APPLICATION ENTRY POINT
# ============================================================================

if __name__ == '__main__':
    """
    Main entry point when running the Flask app directly (not via WSGI server).
    
    This starts the development server with:
    - debug=True: Enables debug mode (auto-reload, detailed errors)
    - host='0.0.0.0': Makes server accessible from any network interface
    - port=5000: Runs on port 5000
    
    For production, use a WSGI server like Gunicorn instead:
        gunicorn -w 4 -b 0.0.0.0:5000 api:app
    """
    logger.info("Starting ClinIQ Backend on port 5000")
    app.run(debug=True, host='0.0.0.0', port=5000)
