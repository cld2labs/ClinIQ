import { useState, useEffect } from 'react';
import DocumentUpload from '../components/DocumentUpload';
import ChatInterface from '../components/ChatInterface';
import { getStatus, clearDocuments } from '../services/api';
import toast from 'react-hot-toast';

const Chat = () => {
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
    checkDocumentStatus();
  }, []);

  const checkDocumentStatus = async () => {
    try {
      const status = await getStatus();
      setHasDocuments(status.has_documents);
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
      setCurrentDocument(result.filename);
    }

    setHasDocuments(true);

    let attempts = 0;
    const maxAttempts = 10;
    const pollStatus = async () => {
      try {
        const status = await getStatus();
        if (status.has_documents && status.document_count > 0) {
          setHasDocuments(true);
        } else if (attempts < maxAttempts) {
          attempts++;
          setTimeout(pollStatus, 200);
        }
      } catch (error) {
        console.error('Error polling status:', error);
      }
    };

    setTimeout(pollStatus, 100);
  };

  const handleClearDocuments = async () => {
    try {
      await clearDocuments();
      setCurrentDocument(null);
      setHasDocuments(false);
      toast.success('Knowledge base cleared');
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
        <div className="inline-flex flex-wrap items-center justify-center gap-3 mt-4 text-sm">
          <span className="px-3 py-1.5 bg-blue-50 text-blue-700 rounded-full font-medium border border-blue-200">
            Hybrid Retrieval (Vector + BM25)
          </span>
          <span className="px-3 py-1.5 bg-purple-50 text-purple-700 rounded-full font-medium border border-purple-200">
            Cosine Similarity Reranking
          </span>
          <span className="px-3 py-1.5 bg-green-50 text-green-700 rounded-full font-medium border border-green-200">
            text to vec embedding
          </span>
        </div>
      </div>

      <div className="max-w-5xl mx-auto space-y-6">
        <DocumentUpload
          onUploadSuccess={handleUploadSuccess}
          currentDocument={currentDocument}
          onClear={handleClearDocuments}
        />

        <ChatInterface
          hasDocuments={hasDocuments}
          config={config}
        />
      </div>
    </div>
  );
};

export default Chat;





