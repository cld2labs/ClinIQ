import { useState, useEffect } from 'react';
import { Upload, FileText, X, Loader2 } from 'lucide-react';
import { uploadDocument, getUploadStatus } from '../services/api';
import toast from 'react-hot-toast';

const DocumentUpload = ({ onUploadSuccess, currentDocument, onClear }) => {
  const [dragActive, setDragActive] = useState(false);
  const [files, setFiles] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [processingStatus, setProcessingStatus] = useState(null);

  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);

    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      const droppedFiles = Array.from(e.dataTransfer.files);
      addFiles(droppedFiles);
    }
  };

  const handleChange = (e) => {
    e.preventDefault();
    if (e.target.files && e.target.files.length > 0) {
      const selectedFiles = Array.from(e.target.files);
      addFiles(selectedFiles);
    }
  };

  const addFiles = (newFiles) => {
    const validFiles = newFiles.filter(file => {
      if (isValidFile(file)) {
        return true;
      } else {
        toast.error(`Invalid file type: ${file.name}. Please upload PDF, DOCX, or TXT files.`);
        return false;
      }
    });

    setFiles(prev => [...prev, ...validFiles]);
  };

  const isValidFile = (file) => {
    const validExtensions = ['.pdf', '.docx', '.txt'];
    const fileExtension = '.' + file.name.split('.').pop().toLowerCase();
    return validExtensions.includes(fileExtension);
  };

  const handleRemoveFile = (index) => {
    setFiles(prev => prev.filter((_, i) => i !== index));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (files.length === 0) return;

    setIsLoading(true);
    setProcessingStatus('Uploading files...');

    try {
      const uploadResult = await uploadDocument(files);
      const jobId = uploadResult.job_id;

      if (!jobId) {
        toast.success(uploadResult.message || 'Documents processed!');
        setFiles([]);
        if (onUploadSuccess) onUploadSuccess(uploadResult);
        setIsLoading(false);
        return;
      }

      const pollInterval = setInterval(async () => {
        try {
          const status = await getUploadStatus(jobId);

          if (status.status === 'completed') {
            clearInterval(pollInterval);
            toast.success(status.message);
            setFiles([]);
            setProcessingStatus(null);
            setIsLoading(false);
            if (onUploadSuccess) onUploadSuccess(status);
          } else if (status.status === 'failed') {
            clearInterval(pollInterval);
            toast.error(status.error || 'Processing failed');
            setProcessingStatus(null);
            setIsLoading(false);
          } else {
            setProcessingStatus(status.message || 'Processing documents...');
          }
        } catch (pollError) {
          clearInterval(pollInterval);
          console.error('Polling error:', pollError);
          setIsLoading(false);
          setProcessingStatus(null);
        }
      }, 2000);

    } catch (error) {
      toast.error(error.message || 'Failed to upload documents');
      setIsLoading(false);
      setProcessingStatus(null);
    }
  };

  return (
    <div className="card animate-fadeIn">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center">
          <Upload className="h-6 w-6 text-primary-600 mr-2" />
          <h2 className="text-xl font-semibold text-gray-800">Knowledge Intake</h2>
        </div>

        {currentDocument && (
          <button
            onClick={onClear}
            className="btn-secondary text-sm"
            disabled={isLoading}
          >
            Clear Knowledge Base
          </button>
        )}
      </div>

      {currentDocument && (
        <div className="mb-4 p-3 bg-primary-50 rounded-lg border border-primary-200">
          <div className="flex items-center gap-2">
            <FileText className="h-5 w-5 text-primary-600" />
            <span className="text-sm font-medium text-primary-900">
              {currentDocument}
            </span>
          </div>
        </div>
      )}

      <form onSubmit={handleSubmit} className="space-y-4">
        <div
          className={`file-drop-zone ${dragActive ? 'file-drop-zone-active' : 'file-drop-zone-inactive'}`}
          onDragEnter={handleDrag}
          onDragLeave={handleDrag}
          onDragOver={handleDrag}
          onDrop={handleDrop}
        >
          <Upload className="mx-auto h-12 w-12 text-gray-400 mb-4" />
          <p className="text-lg font-medium text-gray-700 mb-2">
            Add clinical documents for analysis
          </p>
          <p className="text-sm text-gray-500 mb-4">
            PDF, DOCX, or TXT (Max 50MB per file)
          </p>
          <input
            type="file"
            id="file-upload"
            className="hidden"
            accept=".pdf,.docx,.txt"
            onChange={handleChange}
            multiple
            disabled={isLoading}
          />
          <label
            htmlFor="file-upload"
            className="btn-secondary cursor-pointer inline-block"
          >
            Browse Files
          </label>
        </div>

        {files.length > 0 && (
          <div className="space-y-2 mt-4">
            <h3 className="text-sm font-semibold text-gray-600 uppercase tracking-wider">
              Selected Files ({files.length})
            </h3>
            <div className="max-h-48 overflow-y-auto space-y-2 p-1">
              {files.map((f, index) => (
                <div key={index} className="flex items-center justify-between bg-white p-3 rounded-lg border border-gray-200 shadow-sm animate-fadeIn">
                  <div className="flex items-center space-x-3 overflow-hidden">
                    <FileText className="h-5 w-5 text-primary-600 flex-shrink-0" />
                    <div className="overflow-hidden">
                      <p className="font-medium text-gray-800 text-sm truncate">{f.name}</p>
                      <p className="text-xs text-gray-500">
                        {(f.size / 1024 / 1024).toFixed(2)} MB
                      </p>
                    </div>
                  </div>
                  <button
                    type="button"
                    onClick={() => handleRemoveFile(index)}
                    className="text-gray-400 hover:text-red-500 transition-colors p-1"
                    disabled={isLoading}
                  >
                    <X className="h-4 h-4" />
                  </button>
                </div>
              ))}
            </div>
          </div>
        )}

        <button
          type="submit"
          disabled={files.length === 0 || isLoading}
          className="btn-primary w-full flex items-center justify-center gap-2"
        >
          {isLoading ? (
            <>
              <Loader2 className="w-5 h-5 animate-spin" />
              {processingStatus || `Processing ${files.length} Document${files.length > 1 ? 's' : ''}...`}
            </>
          ) : (
            `Ingest ${files.length > 0 ? files.length : ''} Document${files.length !== 1 ? 's' : ''}`
          )}
        </button>
      </form>
    </div>
  );
};

export default DocumentUpload;


