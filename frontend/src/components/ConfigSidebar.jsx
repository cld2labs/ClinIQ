import { useState } from 'react';
import { Settings, Key, Search, Sparkles } from 'lucide-react';

/**
 * THE SETTINGS DASHBOARD:
 * This component allows you to securely enter your AI access key (API Key)
 * and shows you exactly which AI models are powering your clinical assistant.
 * Python analogy: Like a 'Config' class or a sidebar menu in a desktop app.
 */
const ConfigSidebar = ({ apiKey, onApiKeyChange, config, onConfigChange, models }) => {
  /**
   * PROPS (Arguments):
   * The list above (apiKey, onApiKeyChange, etc.) are like arguments passed to a Python class.
   * 'apiKey' is the data. 'onApiKeyChange' is a function we call to update that data.
   */

  // Local state to hide or show the API key text (Like a local variable).
  const [showApiKey, setShowApiKey] = useState(false);

  return (
    <div className="card animate-fadeIn">
      {/* Configuration Header */}
      <div className="flex items-center mb-4">
        <Settings className="h-6 w-6 text-primary-600 mr-2" />
        <h2 className="text-xl font-semibold text-gray-800">Configuration</h2>
      </div>

      <div className="space-y-6">
        {/* API Key Box */}
        <div>
          <label className="flex items-center text-sm font-medium text-gray-700 mb-2">
            <Key className="w-4 h-4 mr-2" />
            OpenAI API Key
          </label>
          <div className="relative">
            <input
              type={showApiKey ? 'text' : 'password'}
              value={apiKey}
              // This 'onChange' is like a keyboard event listener.
              onChange={(e) => onApiKeyChange(e.target.value)}
              placeholder="sk-proj-..."
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 pr-10"
            />
            {/* Toggle 'Show/Hide' Button */}
            <button
              type="button"
              onClick={() => setShowApiKey(!showApiKey)}
              className="absolute right-2 top-1/2 -translate-y-1/2 text-gray-500 hover:text-gray-700"
            >
              {showApiKey ? 'Hide' : 'Show'}
            </button>
          </div>
          <p className="text-xs text-gray-500 mt-1">
            Your API key is kept in memory only and is never saved or shared
          </p>
        </div>

        {/* Model Info Section (Display only) */}
        <div className="pt-4 border-t border-gray-200">
          <div className="flex items-center text-sm font-medium text-gray-700 mb-2">
            <Sparkles className="w-4 h-4 mr-2" />
            AI Models
          </div>
          <div className="text-xs text-gray-600 space-y-1">
            {/* These 'models' values come from the Python backend status check. */}
            <p>• Embedding: {models?.embedding || 'text-embedding-3-small'}</p>
            <p>• Chat: {models?.chat || 'gpt-3.5-turbo'}</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ConfigSidebar;


