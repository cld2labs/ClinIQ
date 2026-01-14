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
    } catch (error) {
      console.error('Error checking status:', error);
    }
  };

  const handleUploadSuccess = (result) => {
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
    setHasDocuments(true);
    checkDocumentStatus();
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
        <p className="text-gray-600">
          Upload your clinical documents and ask questions
        </p>
      </div>

      <div className="grid lg:grid-cols-3 gap-6">
        {/* Left Sidebar - Configuration */}
        <div className="lg:col-span-1">
          <ConfigSidebar
            apiKey={apiKey}
            onApiKeyChange={setApiKey}
            config={config}
            onConfigChange={setConfig}
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





