# 🏥 ClinIQ - Clinical Knowledge Assistant

**Transform clinical documents into an intelligent question-answering system using AI-powered RAG (Retrieval-Augmented Generation)**

ClinIQ is a modern web application that allows healthcare professionals to upload clinical documents and ask questions in plain English. Using advanced AI techniques including hybrid search, reranking, and OpenAI's GPT models, it provides accurate, evidence-based answers with source citations.


![ClinIQ Demo](Docs/assets/demo.gif)

---

## ✨ Features

- 📄 **Multi-Format Document Support**: Upload PDF, DOCX, or TXT files
- 🔍 **Advanced Search**: Hybrid search combining semantic (dense) and keyword (sparse) retrieval
- 🎯 **Intelligent Reranking**: Cosine similarity-based reranking for improved accuracy
- 💬 **Interactive Chat**: Natural language Q&A interface with conversation history
- 📚 **Source Citations**: Every answer includes citations from source documents
- 🤔 **AI Thinking Process**: Optional step-by-step reasoning display
- 🎨 **Modern UI**: Clean, responsive React-based interface
- 🐳 **Docker Support**: Containerized deployment for easy setup

---

## 🏗️ Architecture

```mermaid
graph TB
    subgraph "Client"
        User[👤 User]
        Browser[🌐 Browser<br/>localhost:3000]
    end

    subgraph "Frontend Container"
        React[⚛️ React + Vite<br/>Port 3000]
    end

    subgraph "Backend Container"
        Flask[🐍 Flask API<br/>Port 5000]
        RAG[🔄 RAG Pipeline]
        
        subgraph "Search"
            Vector[🔍 Vector Search]
            BM25[📊 BM25 Search]
            Hybrid[🔀 Hybrid Fusion]
        end
    end

    subgraph "Storage"
        ChromaDB[(🗄️ ChromaDB<br/>Vector DB)]
        Files[(📁 Uploads)]
    end

    subgraph "External"
        OpenAI[🤖 OpenAI API<br/>GPT-3.5 + Embeddings]
    end

    User -->|Upload & Query| Browser
    Browser -->|HTTP/REST| React
    React -->|Proxy /api/*| Flask
    Flask --> RAG
    RAG --> Vector
    RAG --> BM25
    Vector --> Hybrid
    BM25 --> Hybrid
    Hybrid -->|Context| OpenAI
    Vector --> ChromaDB
    BM25 --> ChromaDB
    Flask --> ChromaDB
    Flask --> Files
    Flask -->|API Key| OpenAI
    OpenAI -->|Answers| Flask

    classDef frontend fill:#61dafb,stroke:#333,stroke-width:2px
    classDef backend fill:#3776ab,stroke:#333,stroke-width:2px,color:#fff
    classDef data fill:#ffa500,stroke:#333,stroke-width:2px
    classDef external fill:#10a37f,stroke:#333,stroke-width:2px,color:#fff
    
    class Browser,React frontend
    class Flask,RAG,Vector,BM25,Hybrid backend
    class ChromaDB,Files data
    class OpenAI external
```

**🔗 [View Detailed Architecture →](./ARCHITECTURE.md)**

### Key Components:
- **Backend**: Flask REST API (Python) - Port 5000
- **Frontend**: React + Vite (JavaScript) - Port 3000
- **Vector Database**: ChromaDB (local persistent storage)
- **AI Models**: OpenAI GPT-3.5-Turbo & text-embedding-3-small

---

## 📋 Prerequisites

### For Local Development:
- **Python 3.10+**
- **Node.js 18+** and npm
- **OpenAI API Key** ([Get one here](https://platform.openai.com/account/api-keys))

### For Docker:
- **Docker Desktop** ([Download here](https://www.docker.com/products/docker-desktop/))

---

## 🚀 Quick Start

### Option 1: Local Development (React + Flask)

#### Step 1: Clone the Repository

```bash
git clone <your-repo-url>
cd clinical-rag
```

#### Step 2: Install Backend Dependencies

```bash
cd backend
pip install -r requirements.txt
cd ..
```

#### Step 3: Install Frontend Dependencies

```bash
cd frontend
npm install
cd ..
```

#### Step 4: Start the Backend

Open a terminal and run:

```bash
cd backend
python api.py
```

The backend will start on `http://localhost:5000`

#### Step 5: Start the Frontend

Open another terminal and run:

```bash
cd frontend
npm run dev
```

The frontend will start on `http://localhost:3000`

#### Step 6: Access the Application

1. Open your browser and navigate to `http://localhost:3000`
2. Enter your OpenAI API key in the configuration panel
3. Upload a clinical document (PDF, DOCX, or TXT)
4. Start asking questions!

---

### Option 2: Docker Deployment

#### Step 1: Clone the Repository

```bash
git clone <your-repo-url>
cd clinical-rag
```

#### Step 2: Build and Run with Docker Compose

From the root directory:

```bash
docker-compose -f configuration/docker-compose.yml up --build
```

Or navigate to the configuration folder:

```bash
cd configuration
docker-compose up --build
```

This single command will:
- Build the backend container (Flask API)
- Build the frontend container (React app)
- Start both services automatically
- Frontend: `http://localhost:3000`
- Backend: `http://localhost:5000`

#### Step 3: Access the Application

1. Open your browser and navigate to `http://localhost:3000`
2. Enter your OpenAI API key in the configuration panel
3. Upload a clinical document
4. Start asking questions!

#### Docker Commands

```bash
# Run in background (detached mode)
docker-compose up -d --build

# View logs
docker-compose logs -f

# Stop services
docker-compose down

# Rebuild after changes
docker-compose up --build --force-recreate
```

---

## 📖 Detailed Setup Instructions

### Local Development Setup

#### Backend Setup

1. **Create a virtual environment (recommended)**:

```bash
python -m venv venv

# On Windows
venv\Scripts\activate

# On macOS/Linux
source venv/bin/activate
```

2. **Install dependencies**:

```bash
pip install -r requirements.txt
```

3. **Run the backend**:

```bash
python api.py
```

The API will be available at `http://localhost:5000`

#### Frontend Setup

1. **Navigate to frontend directory**:

```bash
cd frontend
```

2. **Install dependencies**:

```bash
npm install
```

3. **Start development server**:

```bash
npm run dev
```

The UI will be available at `http://localhost:3000`

---

### Docker Setup

#### Prerequisites

1. **Install Docker Desktop**:
   - Download from: https://www.docker.com/products/docker-desktop/
   - Install and ensure Docker Desktop is running

2. **Verify Docker installation**:

```bash
docker --version
docker compose version
```

#### Running with Docker Compose

1. **Build and start all services**:

```bash
docker-compose up --build
```

2. **Run in detached mode (background)**:

```bash
docker-compose up -d --build
```

3. **View logs**:

```bash
# All services
docker-compose logs -f

# Backend only
docker-compose logs -f backend

# Frontend only
docker-compose logs -f frontend
```

4. **Stop services**:

```bash
docker-compose down
```

#### Individual Container Commands

**Backend only**:

```bash
# Build
docker build -f backend/Dockerfile -t cliniq-backend ./backend

# Run
docker run -p 5000:5000 \
  -v "${PWD}/backend/.chromadb:/app/.chromadb" \
  -v "${PWD}/backend/uploads:/app/uploads" \
  cliniq-backend
```

**Frontend only**:

```bash
# Build
cd frontend
docker build -t cliniq-frontend .

# Run
docker run -p 3000:3000 \
  -v "${PWD}:/app" \
  -v /app/node_modules \
  cliniq-frontend
```

---

## 🎯 How to Use

### 1. First Time Setup

1. **Open the application** at `http://localhost:3000`
2. **Enter your OpenAI API key** in the configuration panel (left sidebar)
3. **Upload a clinical document** using the file uploader

### 2. Asking Questions

1. Type your question in the chat input
2. Examples:
   - "What are the contraindications for this medication?"
   - "How should I monitor this patient's vital signs?"
   - "What follow-up care is recommended?"
3. Review the answer with source citations

### 3. Configuration Options

- **Hybrid Search**: Combines semantic and keyword search (recommended: ON)
- **Reranker**: Re-ranks results for better accuracy (recommended: ON)
- **Show AI Thinking**: Displays step-by-step reasoning (optional)

---

## 🔧 API Endpoints

### Backend API (Flask)

- `GET /api/health` - Health check
- `POST /api/upload` - Upload document
  - Body: `FormData` with `file` and `api_key`
- `POST /api/query` - Query documents
  - Body: `JSON` with `query`, `api_key`, `use_hybrid_search`, `use_reranker`, `show_thinking`
- `POST /api/clear` - Clear knowledge base
- `GET /api/status` - Get document status

---

## 🧠 How It Works

### 1. Document Processing
- Extracts text from PDF/DOCX/TXT files
- Chunks text into manageable pieces (800 tokens with 150 token overlap)
- Creates embeddings using OpenAI's `text-embedding-3-small`

### 2. Storage
- Stores document chunks in ChromaDB (local vector database)
- Maintains metadata (source file, chunk ID, page numbers)

### 3. Query Processing
- **Hybrid Search**: Combines dense (semantic) and sparse (BM25 keyword) search using Reciprocal Rank Fusion (RRF)
- **Reranking**: Re-ranks results using cosine similarity with query embedding
- Retrieves top relevant chunks

### 4. Answer Generation
- Feeds relevant chunks to GPT-3.5-Turbo
- Generates answer based ONLY on document content
- Includes source citations

---

## 📁 Project Structure

```
clinical-rag/
├── README.md                 # Main documentation
├── LICENSE                   # MIT License
├── .gitignore               # Git ignore rules
│
├── backend/                  # Backend Python application
│   ├── api.py               # Flask REST API
│   ├── app.py               # Legacy Streamlit app (optional)
│   ├── requirements.txt     # Python dependencies
│   ├── Dockerfile           # Backend Docker configuration
│   ├── test_openai_api.py   # API testing utility
│   │
│   └── utils/              # Backend utilities
│       ├── __init__.py
│       ├── constants.py     # Model constants
│       ├── document_processor.py # Document extraction & chunking
│       ├── rag_pipeline.py  # RAG query processing
│       └── vector_store.py  # ChromaDB & search operations
│
├── frontend/                # React frontend
│   ├── package.json
│   ├── vite.config.js
│   ├── tailwind.config.js
│   ├── Dockerfile           # Frontend Docker configuration
│   │
│   ├── public/              # Static assets
│   │   └── cloud2labs-logo.png
│   │
│   └── src/
│       ├── main.jsx         # Entry point
│       ├── App.jsx         # Main app component
│       ├── index.css        # Global styles
│       │
│       ├── components/      # React components
│       │   ├── DocumentUpload.jsx
│       │   ├── ChatInterface.jsx
│       │   ├── ConfigSidebar.jsx
│       │   └── layout/
│       │       ├── Header.jsx
│       │       ├── Footer.jsx
│       │       └── Layout.jsx
│       │
│       ├── pages/          # Page components
│       │   ├── Home.jsx
│       │   └── Chat.jsx
│       │
│       └── services/       # API service layer
│           └── api.js
│
├── configuration/          # Configuration files
│   └── docker-compose.yml # Docker Compose configuration
│
├── Docs/                  # Documentation
│   ├── CONTRIBUTING.md
│   ├── DOCKER_SETUP.md
│   ├── PROJECT_DOCUMENTATION.md
│   ├── QUICKSTART.md
│   └── README_REACT_SETUP.md
│
├── .chromadb/             # ChromaDB data (gitignored)
└── uploads/               # Uploaded files (gitignored)
```

---

## 🛠️ Development

### Backend Development

- Edit `api.py` to modify API endpoints
- Edit files in `utils/` to modify core logic
- Backend uses Flask with CORS enabled

### Frontend Development

- Edit files in `frontend/src/`
- Hot reload is enabled during development
- Uses Vite for fast builds

### Building for Production

**Frontend**:

```bash
cd frontend
npm run build
```

Built files will be in `frontend/dist/`

**Backend**:

The Flask app can be deployed using:
- Gunicorn
- uWSGI
- Docker
- Any WSGI-compatible server

---

## 🐳 Docker Details

### Docker Compose Services

**Backend Service**:
- Image: Python 3.11-slim
- Port: 5000
- Volumes: `.chromadb`, `uploads`
- Environment: `FLASK_ENV=development`

**Frontend Service**:
- Image: Node.js 20-alpine
- Port: 3000
- Volumes: `frontend/` (for hot reload)
- Environment: `VITE_BACKEND_ENDPOINT`

### Docker Benefits

✅ No local Node.js installation needed  
✅ No local Python environment setup  
✅ Consistent environment across machines  
✅ Easy to share and deploy  
✅ Isolated dependencies  
✅ Easy cleanup (`docker-compose down`)

---

## 🔍 Troubleshooting

### Port Already in Use

**Backend**:
- Change port in `backend/api.py`: `app.run(port=5001)`

**Frontend**:
- Change port in `frontend/vite.config.js`:
  ```js
  server: {
    port: 3001
  }
  ```

**Docker**:
- Edit `configuration/docker-compose.yml`:
  ```yaml
  ports:
    - "3001:3000"  # Frontend
    - "5001:5000"  # Backend
  ```

### CORS Errors

- Ensure backend is running
- Check that `flask-cors` is installed
- Verify API URL in frontend proxy settings

### API Key Issues

- Ensure OpenAI API key is valid
- Check that key has sufficient credits
- Verify key format (starts with `sk-`)

### Docker Issues

**Container won't start**:
```bash
docker-compose down
docker-compose up --build --force-recreate
```

**View container logs**:
```bash
docker-compose logs -f backend
docker-compose logs -f frontend
```

**Clear Docker cache**:
```bash
docker-compose down -v
docker system prune -a
```

---

## 🔒 Security & Privacy

- **Documents stay local**: Files are processed on your computer/server
- **API keys**: Stored in browser localStorage (never sent to external servers)
- **No data sharing**: ClinIQ doesn't send your documents to external servers
- **OpenAI usage**: Only question text and document chunks sent to OpenAI for processing

---

## 📝 Environment Variables

### Backend

- `FLASK_ENV`: `development` or `production`
- `OPENAI_API_KEY`: Your OpenAI API key (optional, can be set in UI)

### Frontend

- `VITE_BACKEND_ENDPOINT`: Backend API URL (default: `http://localhost:5000`)

---


