const API_BASE_URL = '/api';

export const uploadDocument = async (files) => {
  const formData = new FormData();

  if (Array.isArray(files)) {
    files.forEach(file => {
      formData.append('file', file);
    });
  } else {
    formData.append('file', files);
  }

  const response = await fetch(`${API_BASE_URL}/upload`, {
    method: 'POST',
    body: formData,
  });

  if (!response.ok) {
    let errorMsg = 'Failed to upload document';
    try {
      const errorData = await response.json();
      errorMsg = errorData.error || errorMsg;
    } catch (e) {
      errorMsg = `Server error (${response.status}): ${response.statusText}`;
    }
    throw new Error(errorMsg);
  }

  return response.json();
};

export const getUploadStatus = async (jobId) => {
  const response = await fetch(`${API_BASE_URL}/upload/status/${jobId}`);

  if (!response.ok) {
    const errorData = await response.json();
    throw new Error(errorData.error || 'Failed to get upload status');
  }

  return response.json();
};

export const queryDocuments = async (query, options = {}) => {
  const { onChunk, history = [], ...otherOptions } = options;

  const response = await fetch(`${API_BASE_URL}/query`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      query,
      history,
      use_hybrid_search: otherOptions.useHybridSearch ?? true,
      use_reranker: otherOptions.useReranker ?? true,
      show_thinking: otherOptions.showThinking ?? false,
      stream: !!onChunk,
    }),
  });

  if (!response.ok) {
    let errorMsg = 'Failed to query documents';
    try {
      const errorData = await response.json();
      errorMsg = errorData.error || errorMsg;
    } catch (e) {
      errorMsg = `Server error (${response.status}): ${response.statusText}`;
    }
    throw new Error(errorMsg);
  }

  if (onChunk) {
    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    let buffer = '';

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      buffer += decoder.decode(value, { stream: true });
      const lines = buffer.split('\n\n');
      buffer = lines.pop();

      for (const line of lines) {
        if (line.trim().startsWith('data: ')) {
          try {
            const data = JSON.parse(line.trim().slice(6));
            onChunk(data);
          } catch (e) {
            console.error('Error parsing stream chunk:', e, line);
          }
        }
      }
    }
    return;
  }

  return response.json();
};

export const clearDocuments = async () => {
  const response = await fetch(`${API_BASE_URL}/clear`, {
    method: 'POST',
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.error || 'Failed to clear documents');
  }

  return response.json();
};

export const getStatus = async () => {
  const response = await fetch(`${API_BASE_URL}/status`);

  if (!response.ok) {
    return { has_documents: false, document_count: 0 };
  }

  return response.json();
};


