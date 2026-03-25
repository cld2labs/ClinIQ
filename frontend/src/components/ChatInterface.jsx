import { useState, useRef, useEffect } from 'react';
import { Send, Loader2, Bot, User, FileText } from 'lucide-react';
import { queryDocuments } from '../services/api';
import toast from 'react-hot-toast';

const ChatInterface = ({ hasDocuments, config }) => {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!input.trim() || isLoading) return;

    if (!hasDocuments) {
      toast.error('Please upload a document first');
      return;
    }

    const userMessage = input.trim();
    setInput('');

    setMessages((prev) => [
      ...prev,
      { role: 'user', content: userMessage },
      { role: 'assistant', content: '', thinking: '', citations: [] }
    ]);
    setIsLoading(true);

    try {
      await queryDocuments(userMessage, {
        history: messages,
        useHybridSearch: config.useHybridSearch,
        useReranker: config.useReranker,
        showThinking: config.showThinking,
        onChunk: (chunk) => {
          if (chunk.type === 'citations' || chunk.type === 'metadata') {
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
              {message.role === 'assistant' && (
                <div className="flex-shrink-0 w-8 h-8 rounded-full bg-primary-100 flex items-center justify-center">
                  <Bot className="w-5 h-5 text-primary-600" />
                </div>
              )}

              <div
                className={`max-w-[80%] rounded-lg p-4 ${message.role === 'user'
                  ? 'bg-primary-600 text-white'
                  : message.error
                    ? 'bg-red-50 text-red-800 border border-red-200'
                    : 'bg-gray-100 text-gray-900'
                  }`}
              >
                {message.thinking && (
                  <div className="mb-3 p-3 bg-blue-50 rounded border border-blue-200">
                    <p className="text-xs font-semibold text-blue-800 mb-1">AI Thinking Process</p>
                    <p className="text-sm text-blue-700 whitespace-pre-wrap">{message.thinking}</p>
                  </div>
                )}

                <p className="whitespace-pre-wrap">{message.content}</p>

                {message.citations && message.citations.length > 0 && (
                  <div className="mt-3 pt-3 border-t border-gray-300">
                    <p className="text-xs font-semibold mb-1">Sources:</p>
                    <ul className="text-xs space-y-1">
                      {message.citations.map((cite, idx) => {
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

              {message.role === 'user' && (
                <div className="flex-shrink-0 w-8 h-8 rounded-full bg-primary-600 flex items-center justify-center">
                  <User className="w-5 h-5 text-white" />
                </div>
              )}
            </div>
          ))
        )}

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


