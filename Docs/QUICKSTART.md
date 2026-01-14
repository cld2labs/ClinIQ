# 🚀 Quick Start Guide

Get ClinIQ up and running in minutes! This guide explains what each step does.

---

## Option 1: Docker (Recommended - Easiest)

### Prerequisites
- **Docker Desktop** installed and running
  - Download from: https://www.docker.com/products/docker-desktop/
  - **What it does**: Docker allows you to run applications in isolated containers without installing dependencies on your computer

### Step-by-Step Instructions

#### Step 1: Clone the Repository

```bash
git clone <your-repo-url>
cd clinical-rag
```

**What this does:**
- Downloads the project code from GitHub to your computer
- Navigates into the project directory
- **Result**: You now have all the project files on your local machine

---

#### Step 2: Start Everything with Docker Compose

**First Time (Build + Run):**
```bash
docker-compose -f configuration/docker-compose.yml up --build
```

**Second Time and After (Just Run):**
```bash
docker-compose -f configuration/docker-compose.yml up
```

**What this does:**
1. **Reads the Docker configuration** (`docker-compose.yml`)
   - Tells Docker how to build and run both backend and frontend services

2. **Builds the Backend Container**:
   - Downloads Python 3.11 base image
   - Installs all Python dependencies (Flask, OpenAI, ChromaDB, etc.) **inside the container**
   - Copies backend code into the container
   - Creates a ready-to-run backend image
   - **Result**: Backend container image is created with everything pre-installed

3. **Builds the Frontend Container**:
   - Downloads Node.js 20 base image
   - Installs all npm packages (React, Vite, Tailwind, etc.) **inside the container**
   - Copies frontend code into the container
   - Creates a ready-to-run frontend image
   - **Result**: Frontend container image is created with everything pre-installed

4. **Starts Both Containers**:
   - Backend container runs `python api.py` → Flask API starts on port 5000
   - Frontend container runs `npm run dev` → React dev server starts on port 3000
   - **Result**: Both services are running and communicating with each other

**What you'll see:**
- Docker downloading base images (first time only)
- Installing dependencies in containers
- Starting both services
- Logs from both backend and frontend

**Time**: 
- **First time**: 2-5 minutes (building images with dependencies)
- **Second time onwards**: 10-30 seconds (just starting containers from existing images)

**Important**: 
- Use `--build` flag **only the first time** or when dependencies change
- For regular use, just run `docker-compose up` (without `--build`)

---

#### Step 3: Access the Application

Open your browser and navigate to: **http://localhost:3000**

**What this does:**
- Connects to the frontend container running on port 3000
- Loads the React application in your browser
- **Result**: You see the ClinIQ interface

---

#### Step 4: Stop the Services (When Done)

**To stop the containers:**
```bash
# Press Ctrl+C in the terminal where docker-compose is running
# OR run this command in a new terminal:
docker-compose -f configuration/docker-compose.yml down
```

**What this does:**
- Stops both backend and frontend containers
- Removes the containers (but keeps the images)
- Frees up ports 3000 and 5000
- **Result**: Services are stopped, but images remain for next time

**To stop and remove everything (including images):**
```bash
docker-compose -f configuration/docker-compose.yml down --rmi all
```

**What this does:**
- Stops containers
- Removes containers
- Removes images (you'll need to rebuild next time)
- **Result**: Complete cleanup

---

### First Time Using the App

#### Step 1: Enter Your OpenAI API Key

1. Look for the **Configuration** panel on the left sidebar
2. Enter your OpenAI API key in the "OpenAI API Key" field
3. Click outside the field or press Enter

**What this does:**
- Stores your API key in browser localStorage (stays local, never sent to servers)
- Enables the app to make API calls to OpenAI for document processing and Q&A
- **Result**: API key is saved and ready to use

**Where to get API key**: https://platform.openai.com/account/api-keys

---

#### Step 2: Upload a Clinical Document

1. In the **Document Upload** section, click "Browse Files" or drag & drop
2. Select a PDF, DOCX, or TXT file
3. Click "Upload & Process Document"

**What this does:**
1. **File Upload**: Sends your file to the backend API
2. **Text Extraction**: 
   - If PDF: Extracts text from all pages
   - If DOCX: Extracts text from Word document
   - If TXT: Reads the text file
3. **Text Chunking**: 
   - Breaks the document into smaller pieces (800 tokens each)
   - Creates overlapping chunks for better context
4. **Embedding Creation**: 
   - Converts each chunk into AI-readable format (embeddings)
   - Uses OpenAI's `text-embedding-3-small` model
5. **Storage**: 
   - Saves chunks and embeddings in ChromaDB (vector database)
   - Stores metadata (filename, chunk IDs, page numbers)
6. **Index Creation**: 
   - Creates search indexes for fast retrieval
   - Initializes BM25 index for keyword search

**What you'll see:**
- "Processing document..." message
- Progress indicator
- Success message: "Document processed! Created X chunks"

**Result**: Your document is now searchable and ready for questions

---

#### Step 3: Ask Questions

1. Type your question in the chat input at the bottom
2. Press Enter or click "Send"

**What this does:**
1. **Query Processing**:
   - Converts your question into an embedding (AI-readable format)
   - Prepares search query

2. **Document Search** (if Hybrid Search enabled):
   - **Dense Search**: Finds documents by meaning/semantics
   - **Sparse Search**: Finds documents by keywords (BM25)
   - **Reciprocal Rank Fusion (RRF)**: Combines both search results
   - Retrieves top 15 relevant chunks

3. **Reranking** (if enabled):
   - Re-ranks results using cosine similarity
   - Ensures most relevant chunks are at the top
   - Selects top 7 chunks for context

4. **Answer Generation**:
   - Sends your question + relevant document chunks to GPT-3.5-Turbo
   - AI generates answer based ONLY on your document content
   - Includes source citations

5. **Response Display**:
   - Shows the answer in the chat
   - Displays source citations
   - Shows AI thinking process (if enabled)

**What you'll see:**
- "Analyzing..." message
- Answer appears in the chat
- Source citations below the answer
- AI thinking process (if enabled)

**Result**: You get an accurate answer with citations from your document

---

## Option 2: Local Development (React + Flask)

### Prerequisites
- **Python 3.10+** installed
- **Node.js 18+** and npm installed
- **OpenAI API Key**

### First Time Setup

#### Step 1: Clone the Repository

```bash
git clone <your-repo-url>
cd clinical-rag
```

**What this does:**
- Downloads project code to your computer
- **Result**: Project files are on your machine

---

#### Step 2: Install Backend Dependencies

```bash
cd backend
pip install -r requirements.txt
cd ..
```

**What this does:**
1. Navigates to the backend directory
2. Reads `requirements.txt` (list of Python packages needed)
3. Installs all packages using pip:
   - `flask` - Web framework for API
   - `flask-cors` - Enables frontend-backend communication
   - `openai` - OpenAI API client
   - `chromadb` - Vector database
   - `PyPDF2` - PDF processing
   - `python-docx` - Word document processing
   - And 6 more packages...
4. **Result**: All Python dependencies are installed on your system

**Time**: 1-3 minutes

---

#### Step 3: Install Frontend Dependencies

```bash
cd frontend
npm install
cd ..
```

**What this does:**
1. Navigates to the frontend directory
2. Reads `package.json` (list of npm packages needed)
3. Installs all packages using npm:
   - `react` & `react-dom` - React framework
   - `react-router-dom` - Routing
   - `vite` - Build tool and dev server
   - `tailwindcss` - CSS framework
   - And 10+ more packages...
4. Creates `node_modules/` folder with all dependencies
5. **Result**: All frontend dependencies are installed

**Time**: 1-2 minutes

---

#### Step 4: Start the Backend

Open a terminal and run:

```bash
cd backend
python api.py
```

**What this does:**
1. Starts the Flask web server
2. Creates API endpoints:
   - `/api/health` - Health check
   - `/api/upload` - Document upload
   - `/api/query` - Question answering
   - `/api/clear` - Clear knowledge base
   - `/api/status` - Get status
3. Enables CORS (allows frontend to connect)
4. **Result**: Backend API is running on `http://localhost:5000`

**What you'll see:**
- "Starting ClinIQ Backend on port 5000"
- "Running on http://127.0.0.1:5000"
- Server logs

---

#### Step 5: Start the Frontend

Open another terminal and run:

```bash
cd frontend
npm run dev
```

**What this does:**
1. Starts Vite development server
2. Compiles React components
3. Sets up hot module replacement (auto-refresh on code changes)
4. Proxies API requests to backend (port 5000)
5. **Result**: Frontend is running on `http://localhost:3000`

**What you'll see:**
- "VITE v5.x.x ready in xxx ms"
- "Local: http://localhost:3000"
- Dev server logs

---

#### Step 6: Access the Application

1. Open your browser
2. Navigate to `http://localhost:3000`

**What this does:**
- Loads the React application
- Connects to backend API
- **Result**: ClinIQ interface is ready to use

---

### Running After First Time Setup

Once you've installed dependencies, you only need to **start the services**:

**Terminal 1 - Backend:**
```bash
cd backend
python api.py
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```

**What this does:**
- Starts the services without reinstalling dependencies
- **Result**: Application is running (much faster than first time)

**Note**: You don't need to run `pip install` or `npm install` again unless:
- You add new dependencies to `requirements.txt` or `package.json`
- You delete `node_modules/` or Python packages
- You're setting up on a new machine

---

#### Stopping the Services (When Done)

**To stop the backend:**
- Go to Terminal 1 (where backend is running)
- Press `Ctrl+C`
- **Result**: Flask server stops, port 5000 is freed

**To stop the frontend:**
- Go to Terminal 2 (where frontend is running)
- Press `Ctrl+C`
- **Result**: Vite dev server stops, port 3000 is freed

**What this does:**
- Gracefully shuts down the servers
- Stops all processes
- Frees up the ports
- **Result**: Services are stopped, ready to start again anytime

---

## Quick Reference: Commands Summary

### Docker Commands

| When | Command | What It Does |
|------|---------|--------------|
| **First time** | `docker-compose -f configuration/docker-compose.yml up --build` | Builds images + Starts containers |
| **Every other time** | `docker-compose -f configuration/docker-compose.yml up` | Just starts containers (fast!) |
| **Stop services** | `docker-compose -f configuration/docker-compose.yml down` | Stops and removes containers |
| **Stop (keep images)** | Press `Ctrl+C` in terminal | Stops containers but keeps them |
| **View logs** | `docker-compose -f configuration/docker-compose.yml logs -f` | Shows logs from both services |
| **Stop & cleanup** | `docker-compose -f configuration/docker-compose.yml down --rmi all` | Stops and removes everything |

### Local Development Commands

| When | Command | What It Does |
|------|---------|--------------|
| **First time - Backend** | `cd backend && pip install -r requirements.txt` | Installs Python packages |
| **First time - Frontend** | `cd frontend && npm install` | Installs Node.js packages |
| **Every time - Backend** | `cd backend && python api.py` | Starts Flask API server |
| **Every time - Frontend** | `cd frontend && npm run dev` | Starts React dev server |
| **Stop Backend** | Press `Ctrl+C` in backend terminal | Stops Flask server |
| **Stop Frontend** | Press `Ctrl+C` in frontend terminal | Stops React dev server |

---

## Understanding the Two Options

### Docker vs Local Development

| Aspect | Docker | Local Development |
|--------|--------|-------------------|
| **Dependencies** | Installed in containers | Installed on your system |
| **Setup Time** | 2-5 min (first time) | 3-5 min total |
| **System Impact** | None (isolated) | Installs packages on your machine |
| **Portability** | Works anywhere Docker runs | Requires Python + Node.js |
| **Cleanup** | `docker-compose down` | Manual uninstall |
| **Best For** | Production, sharing, consistency | Development, debugging |

---

## How to Stop the Application

### Docker Method

**Option 1: Stop containers (recommended)**
```bash
docker-compose -f configuration/docker-compose.yml down
```
- Stops both containers
- Removes containers (but keeps images)
- Ports are freed
- **Next time**: Just run `docker-compose up` (fast!)

**Option 2: Stop with Ctrl+C**
- Press `Ctrl+C` in the terminal where docker-compose is running
- Stops containers but keeps them running
- **Next time**: Run `docker-compose up` again

**Option 3: Complete cleanup**
```bash
docker-compose -f configuration/docker-compose.yml down --rmi all
```
- Stops containers
- Removes containers
- Removes images (you'll need to rebuild next time)
- **Use when**: You want to free up disk space

### Local Development Method

**Stop Backend:**
1. Go to the terminal where backend is running
2. Press `Ctrl+C`
3. **Result**: Flask server stops, port 5000 is freed

**Stop Frontend:**
1. Go to the terminal where frontend is running
2. Press `Ctrl+C`
3. **Result**: Vite dev server stops, port 3000 is freed

**What happens:**
- Servers shut down gracefully
- All processes stop
- Ports become available for other applications
- No data is lost (documents and database remain)

---

## Troubleshooting

### Docker Issues

**"Port already in use"**:
- Another application is using port 3000 or 5000
- **Fix**: Stop other applications or change ports in `docker-compose.yml`

**"Cannot connect to Docker daemon"**:
- Docker Desktop is not running
- **Fix**: Start Docker Desktop application

### Local Development Issues

**"Module not found" (Python)**:
- Dependencies not installed
- **Fix**: Run `pip install -r backend/requirements.txt`

**"Cannot find module" (Node.js)**:
- Dependencies not installed
- **Fix**: Run `npm install` in `frontend/` directory

**"Port already in use"**:
- Another process is using the port
- **Fix**: Stop the other process or change port in code

---

## Next Steps

After getting the app running:

1. **Upload a document** - Try a clinical PDF or Word document
2. **Ask questions** - Test the Q&A functionality
3. **Explore settings** - Try enabling/disabling hybrid search and reranker
4. **Read the docs** - Check `Docs/` folder for more detailed documentation

---

## Need Help?

- Check the main [README.md](../README.md) for detailed documentation
- Review [DOCKER_SETUP.md](DOCKER_SETUP.md) for Docker-specific help
- Open an issue on GitHub if you encounter problems

**Ready to get started? Choose your preferred method above and follow the steps!** 🚀
