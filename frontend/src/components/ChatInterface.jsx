import { useState, useRef, useEffect } from 'react';
import { Send, Loader2, Bot, User, FileText } from 'lucide-react';
import { queryDocuments } from '../services/api';
import toast from 'react-hot-toast';

/**
 * THE INTERACTIVE CONSULTANT:
 * This component handles the chat bubble display and the actual messaging logic.
 * Python analogy: Like a CLI loop that takes input and prints responses, but with a GUI.
 */
const ChatInterface = ({ apiKey, hasDocuments, config }) => {
  // 'messages' is a list (Python list) of all chat history.
  const [messages, setMessages] = useState([]);
  // 'input' is the current text in the typing box.
  const [input, setInput] = useState('');
  // Loading state (spinner).
  const [isLoading, setIsLoading] = useState(false);

  // This helps us automatically scroll to the bottom of the chat.
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  /**
   * This runs when you click 'Send' or hit Enter.
   * It's like the main logic block in a Python script.
   */
  const handleSubmit = async (e) => {
    e.preventDefault(); // Stop the page from refreshing (standard web behavior).
    if (!input.trim() || isLoading) return;

    // Double-check API key with trim to ensure it's not just whitespace
    const trimmedKey = apiKey?.trim();
    if (!trimmedKey || trimmedKey.length < 10) {
      toast.error('Please enter a valid OpenAI API key first (starts with "sk-")');
      return;
    }

    // Additional validation - check if it starts with sk-
    if (!trimmedKey.startsWith('sk-')) {
      toast.error('Invalid API key format. OpenAI keys start with "sk-"');
      return;
    }

    if (!hasDocuments) {
      toast.error('Please upload a document first');
      return;
    }

    const userMessage = input.trim();
    setInput(''); // Clear the text box.

    /**
     * Update the screen with the user's message and a blank space for the AI's reply.
     * We create a new list by adding the new message to the existing list.
     */
    setMessages((prev) => [
      ...prev,
      { role: 'user', content: userMessage },
      { role: 'assistant', content: '', thinking: '', citations: [] }
    ]);
    setIsLoading(true);

    try {
      /**
       * We call our API service. Notice 'onChunk' - this is a "callback".
       * Backend sends in order: thinking -> content -> metadata (citations)
       */
      // Use trimmed key to avoid whitespace issues
      await queryDocuments(userMessage, trimmedKey, {
        history: messages, // Pass conversation history for memory
        useHybridSearch: config.useHybridSearch,
        useReranker: config.useReranker,
        showThinking: config.showThinking,
        onChunk: (chunk) => {
          /**
           * PROCESSING THE RESPONSE:
           * Backend streams in this order:
           * 1. "citations" - all retrieved sources (sent first)
           * 2. "thinking" chunks - AI reasoning process (stream character by character)
           * 3. "content" chunks - final answer (stream character by character)
           * 4. "clear_citations" - clear citations if no answer found
           */
          if (chunk.type === 'citations' || chunk.type === 'metadata') {
            // Citations received FIRST (all retrieved sources)
            setMessages((prev) => {
              const lastIndex = prev.length - 1;
              const lastMessage = prev[lastIndex];
              
              return [
                ...prev.slice(0, lastIndex),
                {
                  ...lastMessage,
                  citations: chunk.citations
                }
              ];
            });
          } else if (chunk.type === 'thinking') {
            // APPEND thinking chunks as they stream in
            setMessages((prev) => {
              const lastIndex = prev.length - 1;
              const lastMessage = prev[lastIndex];
              
              return [
                ...prev.slice(0, lastIndex),
                {
                  ...lastMessage,
                  thinking: (lastMessage.thinking || '') + chunk.content
                }
              ];
            });
          } else if (chunk.type === 'content') {
            // APPEND answer chunks as they stream in
            setMessages((prev) => {
              const lastIndex = prev.length - 1;
              const lastMessage = prev[lastIndex];
              
              return [
                ...prev.slice(0, lastIndex),
                {
                  ...lastMessage,
                  content: (lastMessage.content || '') + chunk.content
                }
              ];
            });
          } else if (chunk.type === 'clear_citations') {
            // Clear citations if LLM said "no information"
            setMessages((prev) => {
              const lastIndex = prev.length - 1;
              const lastMessage = prev[lastIndex];
              
              return [
                ...prev.slice(0, lastIndex),
                {
                  ...lastMessage,
                  citations: []
                }
              ];
            });
          }
        }
      });
    } catch (error) {
      toast.error(error.message || 'Failed to get answer');
      setMessages((prev) => {
        const newMessages = [...prev];
        newMessages[newMessages.length - 1].content = 'Sorry, I encountered an error. Please try again.';
        newMessages[newMessages.length - 1].error = true;
        return newMessages;
      });
    } finally {
      setIsLoading(false);
    }
  };

  /**
   * The actual visual part of the chat window.
   * It loops ('maps') over the 'messages' list and draws each message bubble.
   * Python analogy: Like a 'for message in messages: print(bubble_html)' loop.
   */
  return (
    <div className="card h-[600px] flex flex-col">
      <div className="flex items-center mb-4 pb-4 border-b border-gray-200">
        <Bot className="h-6 w-6 text-primary-600 mr-2" />
        <h2 className="text-xl font-semibold text-gray-800">Ask Questions</h2>
      </div>

      <div className="flex-1 overflow-y-auto space-y-4 mb-4 pr-2">
        {messages.length === 0 ? (
          <div className="text-center text-gray-500 mt-8">
            <Bot className="h-12 w-12 mx-auto mb-4 text-gray-400" />
            <p className="text-lg">Start asking questions about your document</p>
            <p className="text-sm mt-2">Try: "What are the key findings?" or "Explain the treatment protocol"</p>
          </div>
        ) : (
          messages.map((message, index) => (
            <div
              key={index}
              className={`flex gap-3 ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
            >
              {/* If it's the AI, show a bot icon */}
              {message.role === 'assistant' && (
                <div className="flex-shrink-0 w-8 h-8 rounded-full bg-primary-100 flex items-center justify-center">
                  <Bot className="w-5 h-5 text-primary-600" />
                </div>
              )}

              {/* The message bubble */}
              <div
                className={`max-w-[80%] rounded-lg p-4 ${message.role === 'user'
                  ? 'bg-primary-600 text-white'
                  : message.error
                    ? 'bg-red-50 text-red-800 border border-red-200'
                    : 'bg-gray-100 text-gray-900'
                  }`}
              >
                {/* Special blue box for the "Thinking" process */}
                {message.thinking && (
                  <div className="mb-3 p-3 bg-blue-50 rounded border border-blue-200">
                    <p className="text-xs font-semibold text-blue-800 mb-1">AI Thinking Process</p>
                    <p className="text-sm text-blue-700 whitespace-pre-wrap">{message.thinking}</p>
                  </div>
                )}

                {/* The final answer text */}
                <p className="whitespace-pre-wrap">{message.content}</p>

                {/* Citations section with links to PDFs - at the bottom */}
                {message.citations && message.citations.length > 0 && (
                  <div className="mt-3 pt-3 border-t border-gray-300">
                    <p className="text-xs font-semibold mb-1">Sources:</p>
                    <ul className="text-xs space-y-1">
                      {message.citations.map((cite, idx) => {
                        // Logic to turn a citation string into a clickable file link.
                        const parts = cite.split('|');
                        const sourcePart = parts[0].replace('Source:', '').trim();

                        let pageNum = '';
                        parts.forEach(part => {
                          if (part.includes('Page:')) {
                            pageNum = part.split(':')[1].trim();
                          }
                        });

                        let fileUrl = `${window.location.protocol}//${window.location.hostname}:5000/api/files/${encodeURIComponent(sourcePart)}`;
                        if (pageNum && !isNaN(pageNum)) {
                          fileUrl += `#page=${pageNum}`;
                        }

                        return (
                          <li key={idx} className="flex items-start gap-1">
                            <FileText className="w-3 h-3 mt-0.5 flex-shrink-0" />
                            <a
                              href={fileUrl}
                              target="_blank"
                              rel="noopener noreferrer"
                              className="text-primary-600 hover:underline"
                            >
                              {cite}
                            </a>
                          </li>
                        );
                      })}
                    </ul>
                  </div>
                )}
              </div>

              {/* If it's the user, show a user icon */}
              {message.role === 'user' && (
                <div className="flex-shrink-0 w-8 h-8 rounded-full bg-primary-600 flex items-center justify-center">
                  <User className="w-5 h-5 text-white" />
                </div>
              )}
            </div>
          ))
        )}

        {/* Spinner while waiting for the AI */}
        {isLoading && (
          <div className="flex gap-3 justify-start">
            <div className="flex-shrink-0 w-8 h-8 rounded-full bg-primary-100 flex items-center justify-center">
              <Bot className="w-5 h-5 text-primary-600" />
            </div>
            <div className="bg-gray-100 rounded-lg p-4">
              <Loader2 className="w-5 h-5 animate-spin text-primary-600" />
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* The typing box at the bottom */}
      <form onSubmit={handleSubmit} className="flex gap-2">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Ask a question about your document..."
          className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
          disabled={isLoading || !hasDocuments}
        />
        <button
          type="submit"
          disabled={!input.trim() || isLoading || !hasDocuments}
          className="btn-primary flex items-center gap-2 px-6"
        >
          {isLoading ? (
            <Loader2 className="w-5 h-5 animate-spin" />
          ) : (
            <>
              <Send className="w-5 h-5" />
              Send
            </>
          )}
        </button>
      </form>
    </div>
  );
};

export default ChatInterface;


