# 🏗️ CliniQ Architecture

## System Architecture Overview

```mermaid
graph TB
    subgraph "Client Layer"
        User[👤 User/Clinician]
        Browser[🌐 Web Browser<br/>localhost:3000]
    end

    subgraph "Frontend - React Application"
        UI[⚛️ React UI<br/>Vite Dev Server]
        Components[📦 Components<br/>Chat, Upload, Config]
        Services[🔌 API Services<br/>HTTP Client]
    end

    subgraph "Backend - Flask Application"
        API[🐍 Flask API<br/>localhost:5000]
        
        subgraph "Core Services"
            Upload[📤 Document Upload<br/>PDF/DOCX/TXT]
            Processor[⚙️ Document Processor<br/>Text Extraction]
            Chunker[✂️ Text Chunking<br/>Semantic Splitting]
            Query[❓ Query Handler<br/>RAG Pipeline]
        end
        
        subgraph "AI/ML Layer"
            Embeddings[🧠 Embedding Generator<br/>text-embedding-3-small]
            Reranker[🎯 Reranker<br/>Cohere/BAAI]
            LLM[🤖 LLM Generator<br/>GPT-3.5-Turbo]
        end
        
        subgraph "Search Layer"
            VectorSearch[🔍 Vector Search<br/>Semantic Similarity]
            BM25[📊 BM25 Search<br/>Keyword Matching]
            Hybrid[🔀 Hybrid Search<br/>RRF Fusion]
        end
    end

    subgraph "Data Layer"
        ChromaDB[(🗄️ ChromaDB<br/>Vector Database<br/>.chromadb/)]
        Uploads[(📁 File Storage<br/>uploads/)]
        Memory[(💾 In-Memory<br/>BM25 Index)]
    end

    subgraph "External Services"
        OpenAI[🌐 OpenAI API<br/>api.openai.com]
    end

    subgraph "Infrastructure - Docker"
        FrontendContainer[🐳 Frontend Container<br/>Node 20 Alpine]
        BackendContainer[🐳 Backend Container<br/>Python 3.11 Slim]
        DockerNetwork[🔗 Docker Network<br/>configuration_default]
    end

    %% User interactions
    User -->|Enters API Key| Browser
    User -->|Uploads Documents| Browser
    User -->|Asks Questions| Browser
    
    %% Frontend flow
    Browser --> UI
    UI --> Components
    Components --> Services
    
    %% API communication
    Services -->|HTTP/REST| API
    
    %% Upload flow
    API --> Upload
    Upload -->|Immediate Success| Browser
    Upload -->|Background Thread| Processor
    Processor -->|Extract Text| Chunker
    Chunker -->|Send Chunks| Embeddings
    Embeddings -->|API Key| OpenAI
    OpenAI -->|Vectors| Embeddings
    Embeddings --> ChromaDB
    ChromaDB -->|Build Index| Memory
    Processor --> Uploads
    
    %% Query flow
    API --> Query
    Query --> Embeddings
    Query --> VectorSearch
    Query --> BM25
    VectorSearch --> ChromaDB
    BM25 --> Memory
    VectorSearch --> Hybrid
    BM25 --> Hybrid
    Hybrid --> Reranker
    Reranker --> LLM
    LLM -->|API Key| OpenAI
    OpenAI -->|Answer| LLM
    LLM --> API
    
    %% Docker infrastructure
    UI -.->|Runs in| FrontendContainer
    API -.->|Runs in| BackendContainer
    FrontendContainer -.->|Connected via| DockerNetwork
    BackendContainer -.->|Connected via| DockerNetwork
    BackendContainer -.->|Mounts| ChromaDB
    BackendContainer -.->|Mounts| Uploads

    %% Styling
    classDef frontend fill:#61dafb,stroke:#333,stroke-width:2px,color:#000
    classDef backend fill:#3776ab,stroke:#333,stroke-width:2px,color:#fff
    classDef data fill:#ffa500,stroke:#333,stroke-width:2px,color:#000
    classDef external fill:#10a37f,stroke:#333,stroke-width:2px,color:#fff
    classDef docker fill:#2496ed,stroke:#333,stroke-width:2px,color:#fff
    
    class UI,Components,Services,Browser frontend
    class API,Upload,Processor,Chunker,Query,Embeddings,Reranker,LLM,VectorSearch,BM25,Hybrid backend
    class ChromaDB,Uploads,Memory data
    class OpenAI external
    class FrontendContainer,BackendContainer,DockerNetwork docker
```

---

## 🔄 Data Flow Diagrams

### 1️⃣ Document Upload Flow

```mermaid
sequenceDiagram
    participant U as 👤 User
    participant F as ⚛️ Frontend
    participant A as 🐍 API
    participant P as ⚙️ Processor
    participant E as 🧠 Embeddings
    participant O as 🌐 OpenAI
    participant DB as 🗄️ ChromaDB
    participant FS as 📁 File Storage

    U->>F: Upload PDF/DOCX
    F->>F: Validate file
    F->>A: POST /api/upload<br/>(file + API key)
    A->>FS: Save original file
    A-->>F: HTTP 202: Processing Started (job_id)
    F-->>U: 📤 Uploading...
    
    Note over A,DB: Background Thread Starts
    A->>P: Extract text
    P->>P: Chunk text (semantic)
    P->>E: Generate embeddings
    E->>O: Create embeddings<br/>(API key)
    O-->>E: Return vectors
    E->>DB: Store chunks + embeddings
    P->>DB: Store metadata
    DB-->>A: Index Built
    
    loop Polling Status
        F->>A: GET /api/upload/status/job_id
        A-->>F: "Processing" or "Completed"
    end
    
    F-->>U: ✅ Document ready
```

### 2️⃣ Query/Question Flow

```mermaid
sequenceDiagram
    participant U as 👤 User
    participant F as ⚛️ Frontend
    participant A as 🐍 API
    participant Q as ❓ Query Handler
    participant V as 🔍 Vector Search
    participant B as 📊 BM25 Search
    participant H as 🔀 Hybrid Search
    participant R as 🎯 Reranker
    participant L as 🤖 LLM
    participant O as 🌐 OpenAI
    participant DB as 🗄️ ChromaDB

    U->>F: Ask question
    F->>A: POST /api/query<br/>(question + API key)
    A->>Q: Process query
    
    par Parallel Search
        Q->>V: Semantic search
        V->>O: Get query embedding
        O-->>V: Vector
        V->>DB: Search similar vectors
        DB-->>V: Top K results
    and
        Q->>B: Keyword search
        B->>B: BM25 scoring
        B-->>Q: Top K results
    end
    
    Q->>H: Merge results (RRF)
    H->>R: Rerank chunks
    R-->>Q: Ranked context
    Q->>L: Generate answer<br/>(context + question)
    L->>O: GPT-3.5-Turbo<br/>(API key)
    O-->>L: Stream response
    L-->>A: Stream chunks
    A-->>F: SSE stream
    F-->>U: 💬 Display answer
```

### 3️⃣ API Key Security Flow

```mermaid
sequenceDiagram
    participant U as 👤 User
    participant F as ⚛️ Frontend
    participant M as 💾 Memory (React State)
    participant A as 🐍 Backend API
    participant E as 🔒 Environment
    participant O as 🌐 OpenAI

    Note over U,O: Session Start
    U->>F: Enter API key
    F->>M: Store in state<br/>(NOT localStorage)
    
    Note over U,O: During Operation
    U->>F: Upload/Query action
    F->>A: Send API key<br/>(HTTPS)
    A->>O: Use key immediately
    O-->>A: Response
    A->>A: Teardown handler<br/>clears env vars
    A-->>F: Return result
    
    Note over U,O: Session End
    U->>F: Close browser/tab
    F->>M: State destroyed
    M->>M: ❌ Key vanishes
    
    Note over U,O: Next Session
    U->>F: Reopen application
    F->>U: ❓ Request API key again
```

---

## 📦 Component Architecture

### Frontend Components

```mermaid
graph TD
    subgraph "React Application Structure"
        App[App.jsx<br/>Main Application]
        Layout[Layout.jsx<br/>Page Structure]
        
        subgraph "Pages"
            Home[Home.jsx<br/>Landing Page]
            Chat[Chat.jsx<br/>Main Interface]
        end
        
        subgraph "Components"
            Header[Header.jsx<br/>Navigation]
            Footer[Footer.jsx<br/>Info Bar]
            Config[ConfigSidebar.jsx<br/>Settings & API Key]
            Upload[DocumentUpload.jsx<br/>File Upload]
            ChatUI[ChatInterface.jsx<br/>Q&A Interface]
        end
        
        subgraph "Services"
            API[api.js<br/>HTTP Client]
        end
        
        App --> Layout
        Layout --> Header
        Layout --> Home
        Layout --> Chat
        Layout --> Footer
        
        Chat --> Config
        Chat --> Upload
        Chat --> ChatUI
        
        Config --> API
        Upload --> API
        ChatUI --> API
    end
    
    classDef page fill:#4caf50,stroke:#333,stroke-width:2px
    classDef component fill:#2196f3,stroke:#333,stroke-width:2px
    classDef service fill:#ff9800,stroke:#333,stroke-width:2px
    
    class Home,Chat page
    class Header,Footer,Config,Upload,ChatUI component
    class API service
```

### Backend Services

```mermaid
graph TD
    subgraph "Flask Backend Structure"
        API[api.py<br/>Main API Server]
        
        subgraph "Utilities"
            DocProc[document_processor.py<br/>PDF/DOCX Processing]
            VectorStore[vector_store.py<br/>ChromaDB Operations]
            RAG[rag_pipeline.py<br/>Retrieval & Generation]
            Constants[constants.py<br/>Configuration]
        end
        
        subgraph "Endpoints"
            Status[GET /api/status]
            UploadEP[POST /api/upload]
            QueryEP[POST /api/query]
            ClearEP[POST /api/clear]
            FileEP[GET /api/files/:filename]
        end
        
        API --> Status
        API --> UploadEP
        API --> QueryEP
        API --> ClearEP
        API --> FileEP
        
        UploadEP --> DocProc
        UploadEP --> VectorStore
        
        QueryEP --> RAG
        
        RAG --> VectorStore
        RAG --> DocProc
        
        ClearEP --> VectorStore
    end
    
    classDef endpoint fill:#e91e63,stroke:#333,stroke-width:2px
    classDef utility fill:#9c27b0,stroke:#333,stroke-width:2px
    
    class Status,UploadEP,QueryEP,ClearEP,FileEP endpoint
    class DocProc,VectorStore,RAG,Constants utility
```

---

## 🐳 Docker Architecture

```mermaid
graph TB
    subgraph "Host Machine"
        Code[📁 Source Code<br/>CliniQ/]
        HostData[💾 Host Volumes<br/>backend/.chromadb<br/>backend/uploads]
    end
    
    subgraph "Docker Compose Network: configuration_default"
        subgraph "Frontend Container - Port 3000"
            Vite[Vite Dev Server<br/>Node 20 Alpine]
            FrontCode[React Application<br/>HMR Enabled]
            FrontVol[Volume Mount<br/>/app]
        end
        
        subgraph "Backend Container - Port 5000"
            Flask[Flask Server<br/>Python 3.11]
            BackendCode[API + Utils<br/>Debug Mode]
            DBVol[Volume Mount<br/>/app/.chromadb]
            UpVol[Volume Mount<br/>/app/uploads]
        end
        
        Vite --> FrontCode
        FrontCode --> FrontVol
        
        Flask --> BackendCode
        BackendCode --> DBVol
        BackendCode --> UpVol
        
        FrontCode -->|Proxy /api/*| Flask
    end
    
    Code -.->|Build Context| Vite
    Code -.->|Build Context| Flask
    HostData -.->|Persistent| DBVol
    HostData -.->|Persistent| UpVol
    
    Internet[🌐 Internet] -->|localhost:3000| Vite
    Internet -->|localhost:5000| Flask
    
    classDef container fill:#2496ed,stroke:#333,stroke-width:3px,color:#fff
    classDef volume fill:#ffa726,stroke:#333,stroke-width:2px
    classDef external fill:#66bb6a,stroke:#333,stroke-width:2px
    
    class Vite,Flask container
    class FrontVol,DBVol,UpVol,HostData volume
    class Internet,Code external
```

---

## 🔐 Security Architecture

```mermaid
graph TB
    subgraph "Security Layers"
        subgraph "Frontend Security"
            NoStore[❌ No localStorage<br/>API keys in memory only]
            HTTPS[🔒 HTTPS<br/>Encrypted transmission]
            Validate[✅ Input Validation<br/>File type checks]
        end
        
        subgraph "Backend Security"
            Teardown[🧹 Request Teardown<br/>Clear env vars after each request]
            Shutdown[🛑 Shutdown Handler<br/>Clear on app termination]
            NoEnv[❌ No env persistence<br/>Keys as parameters only]
        end
        
        subgraph "Data Security"
            LocalOnly[💾 Local Data<br/>Not in version control]
            Shared[🔒 System Isolation<br/>Docker private network]
            NoLog[📝 No Key Logging<br/>Sensitive data excluded]
        end
    end
    
    User[👤 User] -->|Provides API Key| NoStore
    NoStore -->|Encrypted| HTTPS
    HTTPS -->|Transmitted| NoEnv
    NoEnv -->|Used once| Teardown
    Teardown -->|Final cleanup| Shutdown
    
    Shutdown -->|Stores data| LocalOnly
    LocalOnly -->|Ensures| Isolated
    Isolated -->|Protected by| NoLog
    
    classDef security fill:#f44336,stroke:#333,stroke-width:2px,color:#fff
    class NoStore,HTTPS,Validate,Teardown,Shutdown,NoEnv,LocalOnly,Isolated,NoLog security
```

---

## 🔍 RAG Pipeline Detail

```mermaid
graph LR
    subgraph "Retrieval-Augmented Generation Pipeline"
        Query[❓ User Query]
        
        subgraph "Query Rewriting"
            Original[Original Query]
            History[Chat History]
            Rewrite[🔄 Query Rewriter<br/>GPT-3.5-Turbo]
            Enhanced[Enhanced Query]
        end
        
        subgraph "Retrieval Phase"
            VectorEmbed[Vector Embedding<br/>text-embedding-3-small]
            
            subgraph "Hybrid Search"
                Dense[Dense Retrieval<br/>ChromaDB Vector Search]
                Sparse[Sparse Retrieval<br/>BM25 Keyword Search]
                Fusion[🔀 RRF Fusion<br/>Reciprocal Rank]
            end
            
            Reranker[🎯 Reranking<br/>Optional: Cohere/BAAI]
            TopK[Top K Documents]
        end
        
        subgraph "Generation Phase"
            Context[📄 Retrieved Context]
            Prompt[🎭 Prompt Template<br/>System + Context + Query]
            Generate[🤖 LLM Generation<br/>GPT-3.5-Turbo Streaming]
            Answer[💬 Final Answer<br/>+ Citations]
        end
        
        Query --> Original
        Original --> Rewrite
        History --> Rewrite
        Rewrite --> Enhanced
        
        Enhanced --> VectorEmbed
        VectorEmbed --> Dense
        Enhanced --> Sparse
        
        Dense --> Fusion
        Sparse --> Fusion
        Fusion --> Reranker
        Reranker --> TopK
        
        TopK --> Context
        Enhanced --> Prompt
        Context --> Prompt
        Prompt --> Generate
        Generate --> Answer
    end
    
    classDef retrieval fill:#9c27b0,stroke:#333,stroke-width:2px,color:#fff
    classDef generation fill:#ff9800,stroke:#333,stroke-width:2px,color:#fff
    
    class VectorEmbed,Dense,Sparse,Fusion,Reranker,TopK retrieval
    class Rewrite,Context,Prompt,Generate,Answer generation
```

---

## 📊 Technology Stack

```mermaid
mindmap
  root((🏥 CliniQ))
    Frontend
      React 18
      Vite 5
      TailwindCSS
      Lucide Icons
      React Hot Toast
    Backend
      Python 3.11
      Flask
      Flask-CORS
    AI/ML
      OpenAI API
        GPT-3.5-Turbo
        text-embedding-3-small
      ChromaDB
      Rank-BM25
    Infrastructure
      Docker
      Docker Compose
      Node 20 Alpine
      Python 3.11 Slim
    Document Processing
      PyPDF2
      python-docx
      Semantic Chunking
```

---

## 🎯 Key Design Principles

| Principle | Implementation |
|-----------|----------------|
| **🔒 Security First** | No API key persistence, cleared after each use |
| **📦 Modularity** | Separated concerns: Frontend, Backend, AI, Storage |
| **🐳 Containerization** | Docker for consistent environments |
| **🔄 Scalability** | Stateless API, can scale horizontally |
| **⚡ Performance** | Hybrid search, streaming responses |
| **💾 Persistence** | Local volumes for data, code in Git |
| **🎨 User Experience** | Real-time streaming, progress indicators |
| **📚 Documentation** | Comprehensive guides and inline comments |

---

## 📈 Deployment Architecture

```mermaid
graph TB
    subgraph "Development Environment"
        Dev[👨‍💻 Developer]
        DevCode[💻 Local Code]
        DevDocker[🐳 Docker Desktop]
    end
    
    subgraph "Version Control"
        GitHub[<img src='https://github.githubassets.com/images/modules/logos_page/GitHub-Mark.png' width='20'/> GitHub<br/>cld2labs/CliniQ]
        DevBranch[dev/feature]
        MainBranch[main]
    end
    
    subgraph "CI/CD Pipeline"
        Actions[⚙️ GitHub Actions<br/>Build & Test]
    end
    
    subgraph "Production Environment"
        ProdServer[🖥️ Production Server]
        ProdDocker[🐳 Docker Compose]
        LoadBalancer[⚖️ Load Balancer<br/>Optional]
        HTTPS[🔒 HTTPS/SSL]
    end
    
    Dev -->|git commit| DevCode
    DevCode -->|git push| DevBranch
    DevBranch -->|Pull Request| MainBranch
    MainBranch -->|Trigger| Actions
    Actions -->|Deploy| ProdServer
    ProdServer --> ProdDocker
    ProdDocker --> LoadBalancer
    LoadBalancer --> HTTPS
    
    DevCode -.->|Local Testing| DevDocker
    
    classDef dev fill:#4caf50,stroke:#333,stroke-width:2px
    classDef cicd fill:#ff9800,stroke:#333,stroke-width:2px
    classDef prod fill:#f44336,stroke:#333,stroke-width:2px,color:#fff
    
    class Dev,DevCode,DevDocker dev
    class GitHub,DevBranch,MainBranch,Actions cicd
    class ProdServer,ProdDocker,LoadBalancer,HTTPS prod
```

---

## 🚀 Quick Start Architecture

For users starting the application:

```mermaid
graph LR
    Start([▶️ Start]) --> Clone[git clone]
    Clone --> CD[cd CliniQ/configuration]
    CD --> Compose[docker-compose up --build]
    
    Compose --> BuildFront[🔨 Build Frontend<br/>npm install]
    Compose --> BuildBack[🔨 Build Backend<br/>pip install]
    
    BuildFront --> StartFront[▶️ Vite Server<br/>localhost:3000]
    BuildBack --> StartBack[▶️ Flask Server<br/>localhost:5000]
    
    StartFront --> Ready1[✅ Frontend Ready]
    StartBack --> Ready2[✅ Backend Ready]
    
    Ready1 --> Use[🎉 Use Application]
    Ready2 --> Use
    
    Use --> Enter[Enter API Key]
    Enter --> Upload[Upload Documents]
    Upload --> Ask[Ask Questions]
    Ask --> Answer[Get Answers]
    
    classDef action fill:#2196f3,stroke:#333,stroke-width:2px,color:#fff
    classDef ready fill:#4caf50,stroke:#333,stroke-width:2px
    
    class Clone,CD,Compose,BuildFront,BuildBack,StartFront,StartBack action
    class Ready1,Ready2,Use,Answer ready
```

---

**Last Updated:** January 2026  
**Version:** 2.0  
**Status:** ✅ Production Ready

