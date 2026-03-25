"""ClinIQ Backend API - Flask REST API Server"""

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
from config import config
from utils.document_processor import extract_text_from_pdf, extract_text_from_docx, chunk_text, create_embeddings
from utils.vector_store import initialize_chromadb, add_documents, clear_store, initialize_bm25_index
from utils.rag_pipeline import generate_answer, generate_answer_stream, DEFAULT_CHAT_MODEL, DEFAULT_EMBEDDING_MODEL

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

load_dotenv()

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False
app.config['JSONIFY_MIMETYPE'] = 'application/json; charset=utf-8'
CORS(app)

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'pdf', 'docx', 'txt'}
MAX_FILE_SIZE = 50 * 1024 * 1024

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

logger.info("Starting fresh session: Clearing knowledge base.")
clear_store()

def cleanup_on_shutdown():
    """Clear API key from environment on shutdown."""
    if "OPENAI_API_KEY" in os.environ:
        del os.environ["OPENAI_API_KEY"]
        logger.info("Cleared API key from environment on shutdown")

atexit.register(cleanup_on_shutdown)

processing_jobs = {}

@app.teardown_appcontext
def teardown_request(exception=None):
    """Clear API key after each request."""
    if "OPENAI_API_KEY" in os.environ:
        del os.environ["OPENAI_API_KEY"]

def allowed_file(filename):
    """Check if file extension is allowed."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({"status": "healthy"}), 200

@app.route('/api/files/<filename>', methods=['GET'])
def serve_file(filename):
    """Serve uploaded files."""
    try:
        return send_from_directory(UPLOAD_FOLDER, filename)
    except Exception as e:
        logger.error(f"Error serving file {filename}: {str(e)}")
        return jsonify({"error": "File not found"}), 404

def process_documents_background(job_id, file_paths, api_key):
    """Background worker for document processing."""
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
    """Handle file uploads and start background processing."""
    try:
        if 'file' not in request.files:
            return jsonify({"error": "No file provided"}), 400

        files = request.files.getlist('file')
        api_key = request.form.get('api_key', '')

        if not files or all(f.filename == '' for f in files):
            return jsonify({"error": "No files selected"}), 400

        api_key = api_key.strip() if api_key else ''
        if api_key == 'from_env' or not api_key:
            api_key = config.get_api_key()
            logger.info("Using API key from environment configuration")

        if not api_key or len(api_key) < 10:
            return jsonify({"error": "Valid API key is required. Please configure in .env file"}), 400

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

        thread = threading.Thread(
            target=process_documents_background,
            args=(job_id, saved_file_paths, api_key)
        )
        thread.daemon = True
        thread.start()

        return jsonify({
            "success": True,
            "job_id": job_id,
            "message": "Files uploaded successfully. Processing started in background."
        }), 202

    except Exception as e:
        logger.error(f"Upload start error: {str(e)}", exc_info=True)
        return jsonify({"error": str(e)}), 500

@app.route('/api/upload/status/<job_id>', methods=['GET'])
def get_upload_status(job_id):
    """Check status of background processing job."""
    job = processing_jobs.get(job_id)
    if not job:
        return jsonify({"error": "Job not found"}), 404
    return jsonify(job), 200

@app.route('/api/query', methods=['POST'])
def query_documents():
    """Handle question-answering queries using RAG pipeline."""
    try:
        data = request.json
        if not data:
            return jsonify({"error": "No data provided"}), 400

        query = data.get('query', '')
        api_key = data.get('api_key', '')
        use_hybrid_search = data.get('use_hybrid_search', True)
        use_reranker = data.get('use_reranker', True)
        show_thinking = data.get('show_thinking', True)
        stream = data.get('stream', False)

        logger.info(f"Processing query (stream={stream}): {query}")

        if not query:
            return jsonify({"error": "Query is required"}), 400

        api_key = api_key.strip() if api_key else ''
        if api_key == 'from_env' or not api_key:
            api_key = config.get_api_key()
            logger.info("Using API key from environment configuration")

        if not api_key or len(api_key) < 10:
            return jsonify({"error": "Valid API key is required. Please configure in .env file"}), 400

        if stream:
            def sse_stream():
                """Generate SSE stream for real-time responses."""
                try:
                    for chunk in generate_answer_stream(
                        query,
                        api_key=api_key,
                        history=data.get('history', []),
                        use_hybrid_search=use_hybrid_search,
                        use_reranker=use_reranker,
                        show_thinking=show_thinking
                    ):
                        yield f"data: {chunk}\n\n"
                except Exception as stream_err:
                    logger.error(f"Stream error: {str(stream_err)}")
                    yield f"data: {{\"error\": \"{str(stream_err)}\"}}\n\n"

            return Response(sse_stream(), mimetype='text/event-stream; charset=utf-8')

        result = generate_answer(
            query,
            api_key=api_key,
            history=data.get('history', []),
            use_hybrid_search=use_hybrid_search,
            use_reranker=use_reranker,
            show_thinking=show_thinking
        )

        if show_thinking:
            answer, citations, thinking = result
            return jsonify({
                "answer": answer,
                "citations": citations,
                "thinking": thinking
            }), 200
        else:
            answer, citations, _ = result
            return jsonify({
                "answer": answer,
                "citations": citations
            }), 200

    except Exception as e:
        logger.error(f"Error in query_documents: {str(e)}", exc_info=True)
        return jsonify({"error": str(e)}), 500

@app.route('/api/clear', methods=['POST'])
def clear_documents():
    """Clear all documents from knowledge base."""
    try:
        clear_store()

        for f in os.listdir(UPLOAD_FOLDER):
            file_path = os.path.join(UPLOAD_FOLDER, f)
            if os.path.isfile(file_path):
                os.remove(file_path)

        return jsonify({"success": True, "message": "Knowledge base and files cleared"}), 200
    except Exception as e:
        logger.error(f"Error in clear_documents: {str(e)}", exc_info=True)
        return jsonify({"error": str(e)}), 500

@app.route('/api/status', methods=['GET'])
def get_status():
    """Get current system status and configuration."""
    try:
        from chromadb import PersistentClient

        client = PersistentClient(path=".chromadb")

        has_documents = False
        document_count = 0

        try:
            collection = client.get_collection(name="cliniq_docs")
            count = collection.count()
            has_documents = count > 0
            document_count = count
        except Exception:
            pass

        return jsonify({
            "has_documents": has_documents,
            "document_count": document_count,
            "chat_model": config.LLM_CHAT_MODEL,
            "embedding_model": config.LLM_EMBEDDING_MODEL,
            "provider": config.LLM_PROVIDER,
            "provider_info": config.get_provider_info()
        }), 200
    except Exception as e:
        logger.error(f"Error in get_status: {str(e)}", exc_info=True)
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    logger.info("Starting ClinIQ Backend on port 5000")
    app.run(debug=True, host='0.0.0.0', port=5000)
