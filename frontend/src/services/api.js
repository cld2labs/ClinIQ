/**
 * THE COMMUNICATION BRIDGE:
 * These functions allow the frontend (what you see) to talk to the backend (the brain).
 * Think of this file like a "Python Client" for your Flask API.
 */
const API_BASE_URL = '/api';

/**
 * Sends a new health document to the assistant to be 'learned'.
 * Python analogy: Like using the 'requests' library to POST a file.
 * 'async' means this function runs in the background (like a thread or coroutine).
 */
export const uploadDocument = async (files, apiKey) => {
  // FormData is like a Python dictionary specifically for sending files.
  const formData = new FormData();

  // Handle multiple files
  if (Array.isArray(files)) {
    files.forEach(file => {
      formData.append('file', file);
    });
  } else {
    formData.append('file', files);
  }

  formData.append('api_key', apiKey);

  // 'fetch' is the standard way JavaScript makes HTTP requests (like requests.post).
  // 'await' means we wait for the server to reply before moving to the next line.
  const response = await fetch(`${API_BASE_URL}/upload`, {
    method: 'POST',
    body: formData,
  });

  // Check if the server return a 200 OK status.
  if (!response.ok) {
    let errorMsg = 'Failed to upload document';
    try {
      // .json() parses the server's reply (like response.json() in Python).
      const errorData = await response.json();
      errorMsg = errorData.error || errorMsg;
    } catch (e) {
      errorMsg = `Server error (${response.status}): ${response.statusText}`;
    }
    throw new Error(errorMsg);
  }

  return response.json();
};

/**
 * Checks the status of a background document processing job.
 */
export const getUploadStatus = async (jobId) => {
  const response = await fetch(`${API_BASE_URL}/upload/status/${jobId}`);

  if (!response.ok) {
    const errorData = await response.json();
    throw new Error(errorData.error || 'Failed to get upload status');
  }

  return response.json();
};

/**
 * Sends your question to the assistant and handles the incoming answer.
 * We use 'streaming' here to show the answer as it's being typed.
 */
export const queryDocuments = async (query, apiKey, options = {}) => {
  const { onChunk, history = [], ...otherOptions } = options;

  const response = await fetch(`${API_BASE_URL}/query`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      query,
      api_key: apiKey,
      history, // Send Chat History to the backend for context.
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

  // If we are 'streaming' (getting the answer bit by bit):
  if (onChunk) {
    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    let buffer = '';

    // This is like a 'while True' loop reading lines from a socket.
    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      buffer += decoder.decode(value, { stream: true });
      const lines = buffer.split('\n\n');
      buffer = lines.pop(); // Keep partial line in buffer

      for (const line of lines) {
        if (line.trim().startsWith('data: ')) {
          try {
            const data = JSON.parse(line.trim().slice(6));
            onChunk(data); // This calls a function in the GUI to update the screen.
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

/** Wipes the clinical memory clean. */
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

/** Asks the backend for its current status (models used, docs indexed). */
export const getStatus = async () => {
  const response = await fetch(`${API_BASE_URL}/status`);

  if (!response.ok) {
    return { has_documents: false, document_count: 0 };
  }

  return response.json();
};


