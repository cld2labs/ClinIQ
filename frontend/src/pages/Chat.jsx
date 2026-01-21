import { useState, useEffect } from 'react';
import DocumentUpload from '../components/DocumentUpload';
import ChatInterface from '../components/ChatInterface';
import ConfigSidebar from '../components/ConfigSidebar';
import { getStatus, clearDocuments } from '../services/api';
import toast from 'react-hot-toast';

const Chat = () => {
  // API key stored only in memory - will be cleared when app closes
  const [apiKey, setApiKey] = useState('');
  const [currentDocument, setCurrentDocument] = useState(null);
  const [hasDocuments, setHasDocuments] = useState(false);
  const [models, setModels] = useState({
    chat: 'gpt-3.5-turbo',
    embedding: 'text-embedding-3-small'
  });
  const [config, setConfig] = useState({
    useHybridSearch: true,
    useReranker: true,
    showThinking: true,
  });

  useEffect(() => {
    // Check document status on mount
    checkDocumentStatus();
    
    // Remove any previously stored API key from localStorage (cleanup from old version)
    if (localStorage.getItem('cliniq_api_key')) {
      localStorage.removeItem('cliniq_api_key');
    }
  }, []);

  const checkDocumentStatus = async () => {
    try {
      const status = await getStatus();
      setHasDocuments(status.has_documents);
      // Update model names dynamically from backend
      if (status.chat_model) {
        setModels({
          chat: status.chat_model,
          embedding: status.embedding_model
        });
      }
    } catch (error) {
      console.error('Error checking status:', error);
    }
  };

  const handleUploadSuccess = async (result) => {
    if (result.files && result.files.length > 0) {
      if (result.files.length === 1) {
        setCurrentDocument(result.files[0]);
      } else {
        setCurrentDocument(`${result.files.length} documents uploaded`);
      }
    } else if (result.filename) {
      // Fallback for single file if backend was still returning filename
      setCurrentDocument(result.filename);
    }
    
    // Immediately set to true based on upload result
    setHasDocuments(true);
    
    // Poll status to ensure backend has fully processed
    let attempts = 0;
    const maxAttempts = 10;
    const pollStatus = async () => {
      try {
        const status = await getStatus();
        if (status.has_documents && status.document_count > 0) {
          // Documents confirmed in backend
          setHasDocuments(true);
        } else if (attempts < maxAttempts) {
          // Retry after a short delay
          attempts++;
          setTimeout(pollStatus, 200);
        }
      } catch (error) {
        console.error('Error polling status:', error);
      }
    };
    
    // Start polling after a short delay
    setTimeout(pollStatus, 100);
  };

  const handleClearDocuments = async () => {
    try {
      await clearDocuments();
      setCurrentDocument(null);
      setHasDocuments(false);
      // Clear API key from memory when clearing knowledge base
      setApiKey('');
      toast.success('Knowledge base and API key cleared');
    } catch (error) {
      toast.error(error.message || 'Failed to clear documents');
    }
  };

  return (
    <div className="space-y-6">
      <div className="text-center mb-8">
        <h1 className="text-4xl font-bold text-gray-900 mb-2">
          Clinical Knowledge Assistant
        </h1>
        <p className="text-gray-600 mb-4">
          Upload your clinical documents and ask questions
        </p>
        {/* RAG Technology Highlight */}
        <div className="inline-flex flex-wrap items-center justify-center gap-3 mt-4 text-sm">
          <span className="px-3 py-1.5 bg-blue-50 text-blue-700 rounded-full font-medium border border-blue-200">
            Hybrid Retrieval (Vector + BM25)
          </span>
          <span className="px-3 py-1.5 bg-purple-50 text-purple-700 rounded-full font-medium border border-purple-200">
            Cosine Similarity Reranking
          </span>
          <span className="px-3 py-1.5 bg-green-50 text-green-700 rounded-full font-medium border border-green-200">
            {models.embedding}
          </span>
          <span className="px-3 py-1.5 bg-orange-50 text-orange-700 rounded-full font-medium border border-orange-200">
            {models.chat}
          </span>
        </div>
      </div>

      <div className="grid lg:grid-cols-3 gap-6">
        {/* Left Sidebar - Configuration */}
        <div className="lg:col-span-1">
          <ConfigSidebar
            apiKey={apiKey}
            onApiKeyChange={setApiKey}
            config={config}
            onConfigChange={setConfig}
            models={models}
          />
        </div>

        {/* Main Content */}
        <div className="lg:col-span-2 space-y-6">
          <DocumentUpload
            apiKey={apiKey}
            onUploadSuccess={handleUploadSuccess}
            currentDocument={currentDocument}
            onClear={handleClearDocuments}
          />

          <ChatInterface
            apiKey={apiKey}
            hasDocuments={hasDocuments}
            config={config}
          />
        </div>
      </div>
    </div>
  );
};

export default Chat;





