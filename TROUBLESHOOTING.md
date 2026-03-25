# Troubleshooting Guide

This guide covers common issues and solutions for the ClinIQ Clinical Q&A AI Assistant application.

---

## Table of Contents

- [Installation Issues](#installation-issues)
- [Configuration Errors](#configuration-errors)
- [Runtime Errors](#runtime-errors)
- [Backend Failures](#backend-failures)
- [Performance Issues](#performance-issues)
- [Docker Issues](#docker-issues)
- [Network and API Errors](#network-and-api-errors)
- [Advanced Debugging](#advanced-debugging)

---

## Installation Issues

### Docker Container Build Fails

**Error:** `ERROR [internal] load build context`

**Cause:** Docker daemon not running or insufficient permissions.

**Solution:**
```bash
# Start Docker daemon (Linux/Mac)
sudo systemctl start docker

# On Windows, start Docker Desktop application

# Verify Docker is running
docker ps
```

### Port Already in Use

**Error:** `Error starting userland proxy: listen tcp 0.0.0.0:5000: bind: address already in use`

**Cause:** Another service is using port 5000 (backend) or 3000 (frontend).

**Solution:**
```bash
# Find process using the port
# On Linux/Mac:
lsof -i :5000
lsof -i :3000

# On Windows:
netstat -ano | findstr :5000
netstat -ano | findstr :3000

# Kill the process or change ports in docker-compose.yml
```

### Python Dependencies Installation Fails

**Error:** `ERROR: Could not find a version that satisfies the requirement...`

**Cause:** Python version incompatibility or network issues.

**Solution:**
```bash
# Ensure Python 3.10+ is installed
python --version

# Upgrade pip
pip install --upgrade pip

# Install with verbose output to diagnose
cd backend
pip install -r requirements.txt --verbose

# For SSL errors, try:
pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org -r requirements.txt
```

### Node.js Dependencies Installation Fails

**Error:** `npm ERR! code ERESOLVE` or `Cannot find module`

**Cause:** Node version incompatibility or corrupted package-lock.

**Solution:**
```bash
cd frontend

# Remove existing node_modules and lock file
rm -rf node_modules package-lock.json

# Ensure Node 18+ is installed
node --version

# Clean install
npm install

# If issues persist, try:
npm install --legacy-peer-deps
```

---

## Configuration Errors

### Missing OpenAI API Key

**Error:** `ValueError: OpenAI API key is required` or `401 Unauthorized`

**Cause:** OpenAI API key not configured in the application.

**Solution:**

**Option 1: Configure via UI (Recommended)**
1. Open the application at `http://localhost:3000`
2. Click on the configuration sidebar (gear icon)
3. Enter your OpenAI API key in the provided field
4. The key is stored in browser memory only (not persisted)

**Option 2: Set Environment Variable**
```bash
# Add to backend/.env file
echo "OPENAI_API_KEY=your_actual_api_key_here" >> backend/.env

# Or set as system environment variable
export OPENAI_API_KEY=your_actual_api_key_here  # Linux/Mac
set OPENAI_API_KEY=your_actual_api_key_here     # Windows CMD
```

### Invalid OpenAI API Key

**Error:** `401 Unauthorized` or `Invalid API key`

**Cause:** OpenAI API key is incorrect, expired, or revoked.

**Solution:**
1. Verify your API key at https://platform.openai.com/api-keys
2. Generate a new key if needed
3. Update the key in the configuration sidebar
4. API key format should start with `sk-`

### OpenAI API Key Without Credits

**Error:** `429 You exceeded your current quota` or `Insufficient credits`

**Cause:** OpenAI account has insufficient credits or billing not set up.

**Solution:**
1. Check your usage at https://platform.openai.com/usage
2. Add billing information at https://platform.openai.com/account/billing
3. Purchase credits or upgrade plan
4. Wait for rate limits to reset if on free tier

### ChromaDB Initialization Fails

**Error:** `chromadb.errors.NoIndexException` or `Cannot connect to ChromaDB`

**Cause:** ChromaDB directory not accessible or corrupted.

**Solution:**
```bash
# Remove and recreate ChromaDB directory
rm -rf .chromadb
mkdir .chromadb

# Ensure proper permissions
chmod 755 .chromadb

# Restart the application
docker compose down
docker compose up --build
```

### File Upload Directory Missing

**Error:** `FileNotFoundError: [Errno 2] No such file or directory: 'uploads'`

**Cause:** Uploads directory doesn't exist.

**Solution:**
```bash
# Create uploads directory in project root
mkdir -p uploads

# Ensure proper permissions
chmod 755 uploads

# Restart backend
docker compose restart backend
```

---

## Runtime Errors

### Document Upload Fails

**Error:** `Failed to upload document` or `Unsupported file type`

**Cause:** File format not supported or file corrupted.

**Solution:**
1. Verify file is PDF, DOCX, or TXT format
2. Check file size (max recommended: 50MB)
3. Try opening the file to ensure it's not corrupted
4. For PDFs, ensure they contain extractable text (not scanned images)
5. Check backend logs for specific error:
   ```bash
   docker compose logs backend --tail 50
   ```

### Document Processing Stuck

**Error:** Status shows "processing" indefinitely

**Cause:** Document processing failed or backend crashed.

**Solution:**
```bash
# Check backend logs for errors
docker compose logs backend --tail 100

# Restart backend service
docker compose restart backend

# Check if document was too large
# Look for memory errors in logs

# Clear stuck documents
curl -X DELETE http://localhost:5000/clear
```

### Query Returns "No Documents Found"

**Error:** `No documents found in vector store`

**Cause:** Documents not properly indexed or ChromaDB cleared.

**Solution:**
1. Verify documents were successfully uploaded
2. Check document status at `/status` endpoint:
   ```bash
   curl http://localhost:5000/status
   ```
3. Re-upload documents if necessary
4. Check ChromaDB directory exists and contains data:
   ```bash
   ls -la .chromadb/
   ```

### Empty or Incomplete Answers

**Error:** AI returns empty responses or cuts off mid-sentence

**Cause:** Context retrieval failed or token limit exceeded.

**Solution:**
1. Check if documents are properly chunked and indexed
2. Verify query is specific enough
3. Review backend logs for retrieval errors
4. Try disabling hybrid search and reranking to isolate issue
5. Increase token limits in `backend/utils/constants.py` if needed

### Citations Not Showing

**Error:** Answers provided without source citations

**Cause:** Citation parsing failed or metadata missing.

**Solution:**
1. Check document metadata was stored during upload
2. Review citation format in backend logs
3. Verify `rag_pipeline.py` is properly extracting citations
4. Re-upload documents to regenerate metadata

---

## Backend Failures

### Flask Server Won't Start

**Error:** `Address already in use` or `ModuleNotFoundError`

**Cause:** Port conflict or missing dependencies.

**Solution:**
```bash
# Check if port 5000 is available
lsof -i :5000  # Linux/Mac
netstat -ano | findstr :5000  # Windows

# Kill conflicting process or change port in api.py
# Change: app.run(host='0.0.0.0', port=5000)
# To:    app.run(host='0.0.0.0', port=5001)

# Verify all dependencies installed
cd backend
pip install -r requirements.txt
```

### ChromaDB Connection Errors

**Error:** `chromadb.errors.ChromaError: Could not connect to tenant`

**Cause:** ChromaDB client misconfigured or directory permissions issue.

**Solution:**
```bash
# Reset ChromaDB
rm -rf .chromadb
mkdir .chromadb

# Ensure backend has write permissions
chmod -R 755 .chromadb

# Update ChromaDB settings in vector_store.py if needed
# Verify persistence directory path is correct

# Restart application
docker compose down
docker compose up --build
```

### Embedding Generation Fails

**Error:** `OpenAI API error during embedding creation`

**Cause:** API key invalid, network issues, or rate limits.

**Solution:**
1. Verify OpenAI API key is valid
2. Check network connectivity to OpenAI API:
   ```bash
   curl https://api.openai.com/v1/models \
     -H "Authorization: Bearer YOUR_API_KEY"
   ```
3. Check rate limits at https://platform.openai.com/account/limits
4. Review embedding model configuration in `constants.py`:
   ```python
   DEFAULT_EMBEDDING_MODEL = "text-embedding-3-small"
   ```
5. Wait and retry if rate limited

### Hybrid Search Errors

**Error:** `Failed to perform hybrid search` or BM25 errors

**Cause:** BM25 index not built or sparse search configuration issue.

**Solution:**
```bash
# Check backend logs for specific BM25 error
docker compose logs backend | grep -i "bm25"

# Clear and rebuild vector store
curl -X DELETE http://localhost:5000/clear

# Re-upload documents to rebuild both dense and sparse indexes

# Disable hybrid search temporarily in UI to test
# If works without hybrid search, rebuild BM25 index
```

### Reranking Fails

**Error:** `Reranking failed` or cosine similarity errors

**Cause:** Query embedding generation failed or metadata missing.

**Solution:**
1. Check if query embeddings are being created
2. Verify cosine similarity calculation in `vector_store.py`
3. Test without reranking to isolate issue
4. Check backend logs for numpy/math errors
5. Ensure chunk embeddings exist in ChromaDB

### Document Chunking Errors

**Error:** `Failed to chunk document` or tiktoken errors

**Cause:** Token counting failed or document format issue.

**Solution:**
```bash
# Verify tiktoken is properly installed
pip install --upgrade tiktoken

# Check document encoding
# Ensure UTF-8 encoding for text files

# Review chunking parameters in document_processor.py:
# - chunk_size (default: 800 tokens)
# - chunk_overlap (default: 150 tokens)

# Try simpler document first to isolate issue
```

---

## Performance Issues

### Slow Query Response Times

**Symptom:** Queries take longer than 10 seconds to respond

**Causes and Solutions:**

1. **Large document corpus**
   - Reduce number of retrieved chunks (default: 5)
   - Enable reranking to improve quality of fewer chunks
   - Consider document filtering by metadata

2. **Hybrid search overhead**
   - Disable hybrid search in UI if not needed
   - Profile search times in backend logs
   - Optimize BM25 index parameters

3. **Network latency to OpenAI**
   - Check internet connection speed
   - Monitor OpenAI API status at https://status.openai.com
   - Consider using streaming mode for faster perceived response

4. **Reranking computation**
   - Disable reranking if not necessary
   - Reduce number of chunks to rerank
   - Profile cosine similarity calculations

### High Memory Usage

**Symptom:** Backend container using excessive memory (>2GB)

**Cause:** Large document embeddings or ChromaDB cache.

**Solution:**
```bash
# Increase Docker memory limit in Docker Desktop
# Recommended: 4GB minimum

# Clear old documents
curl -X DELETE http://localhost:5000/clear

# Optimize chunking strategy
# Reduce chunk_size in document_processor.py

# Monitor memory usage
docker stats

# Restart backend periodically if needed
docker compose restart backend
```

### Slow Document Upload Processing

**Symptom:** Document processing takes longer than 2 minutes

**Cause:** Large document or slow embedding generation.

**Solution:**
1. Check document size - consider splitting large PDFs
2. Verify network speed to OpenAI API
3. Review backend logs for bottlenecks
4. Monitor embedding generation time
5. Consider increasing chunk size to reduce total chunks
6. Process documents in smaller batches

### Frontend Freezing During Streaming

**Symptom:** UI becomes unresponsive during answer streaming

**Cause:** Too many rapid DOM updates or memory leak.

**Solution:**
1. Check browser console for JavaScript errors
2. Reduce update frequency in ChatInterface.jsx
3. Clear browser cache and cookies
4. Test in different browser
5. Check for memory leaks in React DevTools

---

## Docker Issues

### Backend Container Won't Start

**Error:** `backend exited with code 1`

**Solution:**
```bash
# Check backend logs for specific error
docker compose logs backend

# Common causes:
# 1. Missing dependencies - rebuild:
docker compose build --no-cache backend
docker compose up -d

# 2. Port conflict - see Port Already in Use section

# 3. Volume mount issues - verify paths in docker-compose.yml
```

### Frontend Container Build Fails

**Error:** `npm install failed` or `Cannot find module`

**Solution:**
```bash
# Rebuild frontend with clean cache
docker compose build --no-cache frontend
docker compose up -d frontend

# Verify Node.js version in Dockerfile (should be 18+)

# Check if package.json is valid
cd frontend
npm install  # Test locally first
```

### Container Memory Issues

**Error:** `Killed` or `Out of memory`

**Solution:**
```bash
# Increase Docker memory limit in Docker Desktop settings
# Recommended: 4GB minimum, 8GB preferred

# Reduce memory usage:
# - Clear old documents
# - Reduce chunk size
# - Process fewer documents concurrently

# Monitor memory usage
docker stats
```

### Cannot Connect to Backend from Frontend

**Error:** `Network error` or `Connection refused` in browser console

**Cause:** Docker network misconfiguration or CORS issue.

**Solution:**
```bash
# Verify both containers are running
docker compose ps

# Check backend is accessible
curl http://localhost:5000/health

# Verify Vite proxy configuration in frontend/vite.config.js:
# proxy: {
#   '/api': 'http://backend:5000'
# }

# Check CORS settings in backend/api.py
# CORS(app, origins=["*"])  # or specific origins

# Restart services
docker compose restart
```

### Volume Mount Permission Errors

**Error:** `Permission denied` when accessing volumes

**Cause:** Docker volume permissions mismatch.

**Solution:**
```bash
# Fix permissions on host
sudo chown -R $USER:$USER .chromadb uploads

# Or in docker-compose.yml, add user directive:
# user: "1000:1000"  # Your UID:GID

# Rebuild containers
docker compose down
docker compose up --build
```

---

## Network and API Errors

### OpenAI API Connection Refused

**Error:** `ConnectionRefusedError: [Errno 111] Connection refused`

**Cause:** OpenAI API unreachable or network firewall blocking.

**Solution:**
```bash
# Test connectivity to OpenAI
curl https://api.openai.com/v1/models \
  -H "Authorization: Bearer YOUR_API_KEY"

# Check firewall/proxy settings allow outbound HTTPS
# Verify DNS resolution
ping api.openai.com

# Check OpenAI status
# https://status.openai.com

# Try with different network if behind corporate proxy
```

### OpenAI API Timeout

**Error:** `Timeout waiting for OpenAI response`

**Cause:** Network latency or OpenAI API overloaded.

**Solution:**
```bash
# Increase timeout in backend code
# In rag_pipeline.py or document_processor.py:
# timeout = 300  # Increase to 300 seconds

# Check network speed
# Test with smaller document first

# Switch to streaming mode for better user experience
```

### Rate Limit Exceeded

**Error:** `429 Too Many Requests` or `Rate limit exceeded`

**Cause:** Too many concurrent API requests.

**Solution:**
- Wait 60 seconds before retrying
- Reduce document processing concurrency
- Check rate limits at https://platform.openai.com/account/limits
- Upgrade to higher tier OpenAI plan
- Process documents in smaller batches

### SSL Certificate Errors

**Error:** `SSLError: [SSL: CERTIFICATE_VERIFY_FAILED]`

**Cause:** SSL certificate verification issues or corporate proxy.

**Solution:**
```bash
# Update CA certificates
pip install --upgrade certifi

# For development only (not recommended for production):
# Add SSL verification bypass in api calls
# requests.post(..., verify=False)

# Or use corporate CA bundle
# export REQUESTS_CA_BUNDLE=/path/to/corporate-ca.pem
```

### CORS Errors in Browser

**Error:** `CORS policy: No 'Access-Control-Allow-Origin' header`

**Cause:** Backend not allowing frontend origin.

**Solution:**
```python
# In backend/api.py, ensure CORS is configured:
from flask_cors import CORS

app = Flask(__name__)
CORS(app, origins=["http://localhost:3000", "http://localhost:5173"])

# Or allow all origins for development (not for production):
CORS(app, origins="*")

# Restart backend
docker compose restart backend
```

---

## Advanced Debugging

### Enable Debug Logging

To get more detailed logs for debugging:

```bash
# In backend/api.py, set Flask debug mode:
app.run(debug=True, host='0.0.0.0', port=5000)

# Or set environment variable
export FLASK_ENV=development

# Restart backend
docker compose restart backend

# View detailed logs
docker compose logs -f backend
```

### Check Application Health

```bash
# Backend health check
curl http://localhost:5000/health

# Expected response:
# {"status": "healthy", "chromadb": "connected", "models": "loaded"}

# Check document count
curl http://localhost:5000/status

# View ChromaDB stats
ls -lah .chromadb/
```

### Test Individual Components

**Test Document Upload:**
```bash
curl -X POST http://localhost:5000/upload \
  -F "file=@test-document.pdf"
```

**Test Query (Non-streaming):**
```bash
curl -X POST http://localhost:5000/query \
  -H "Content-Type: application/json" \
  -H "X-OpenAI-Key: YOUR_API_KEY" \
  -d '{
    "query": "What is the patient diagnosis?",
    "use_hybrid_search": true,
    "use_reranker": true
  }'
```

**Test Embeddings:**
```bash
# Test in Python console
python3
>>> from openai import OpenAI
>>> client = OpenAI(api_key="YOUR_KEY")
>>> response = client.embeddings.create(
...     model="text-embedding-3-small",
...     input="test"
... )
>>> print(len(response.data[0].embedding))
# Should print: 1536
```

### Inspect ChromaDB Contents

```python
# In Python console
import chromadb

client = chromadb.PersistentClient(path=".chromadb")
collection = client.get_or_create_collection("clinical_documents")

# Get count
print(f"Total chunks: {collection.count()}")

# Sample some documents
results = collection.get(limit=5, include=["documents", "metadatas"])
for i, (doc, meta) in enumerate(zip(results['documents'], results['metadatas'])):
    print(f"\nChunk {i}:")
    print(f"Source: {meta.get('source', 'unknown')}")
    print(f"Text: {doc[:200]}...")
```

### Monitor API Token Usage

```bash
# Add logging to track token usage in backend
# In rag_pipeline.py or document_processor.py:

import logging
logging.basicConfig(level=logging.INFO)

# Log before API calls:
logging.info(f"Generating embeddings for {num_chunks} chunks")
logging.info(f"Query: {query}")
logging.info(f"Context length: {len(context)} tokens")

# Check logs
docker compose logs backend | grep -i "token\|embedding"
```

### Reset Application State

To completely reset the application:

```bash
# Stop and remove containers
docker compose down -v

# Remove data directories
rm -rf .chromadb uploads

# Recreate directories
mkdir .chromadb uploads

# Remove temporary files
rm -rf backend/__pycache__ backend/utils/__pycache__

# Rebuild and restart
docker compose build --no-cache
docker compose up -d

# Verify clean state
curl http://localhost:5000/status
# Should show: {"status": "ready", "document_count": 0}
```

### Profile Performance

```python
# Add timing to critical functions in backend
import time

def timed_function():
    start = time.time()
    # ... function code ...
    duration = time.time() - start
    print(f"Function took {duration:.2f} seconds")

# Example: Profile search performance
start = time.time()
results = vector_store.hybrid_search(query, k=5)
print(f"Hybrid search: {time.time() - start:.2f}s")

start = time.time()
reranked = vector_store.rerank_results(query, results)
print(f"Reranking: {time.time() - start:.2f}s")
```

---

## Getting Help

If you continue to experience issues:

1. **Check Logs:** Review backend logs with `docker compose logs backend -f`
2. **Verify Configuration:** Ensure OpenAI API key is valid and has credits
3. **Test Connectivity:** Verify network access to OpenAI API
4. **Inspect Data:** Check ChromaDB and uploads directories exist and have proper permissions
5. **Report Issues:** If the problem persists, collect:
   - Error messages from logs
   - Document type and size
   - Query that caused the issue
   - Browser console errors (for frontend issues)
   - Docker container status (`docker compose ps`)
   - Configuration settings (redact API key)

---

## Common Success Indicators

A successful run should show:

```
✅ Backend started successfully on port 5000
✅ Frontend accessible at http://localhost:3000
✅ ChromaDB initialized and persistent
✅ Document uploaded and processed
✅ Embeddings created and stored
✅ Query returns relevant answer with citations
✅ Streaming works smoothly without errors
✅ Sources properly cited with document references
```

All components should be running without errors, and queries should return contextually relevant answers based on uploaded documents.

---
