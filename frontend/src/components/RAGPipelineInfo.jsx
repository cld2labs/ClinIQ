import { Brain, Search, Target, Sparkles, Zap, Network } from 'lucide-react';

const RAGPipelineInfo = ({ compact = false }) => {
  const features = [
    {
      icon: Search,
      title: 'Hybrid Retrieval',
      description: 'Combines Vector (semantic) and BM25 (keyword) search using Reciprocal Rank Fusion',
      color: 'from-blue-500 to-cyan-500',
      badge: 'Dense + Sparse'
    },
    {
      icon: Target,
      title: 'Cosine Reranking',
      description: 'Cosine similarity-based reranking to refine search results for maximum relevance',
      color: 'from-purple-500 to-pink-500',
      badge: 'Similarity Score'
    },
    {
      icon: Brain,
      title: 'Embedding Model',
      description: 'OpenAI text-embedding-3-small for high-quality semantic representations',
      color: 'from-green-500 to-emerald-500',
      badge: 'text-embedding-3-small'
    },
    {
      icon: Sparkles,
      title: 'LLM Generation',
      description: 'GPT-3.5-Turbo for context-aware answer generation with reasoning',
      color: 'from-orange-500 to-red-500',
      badge: 'GPT-3.5-Turbo'
    }
  ];

  if (compact) {
    return (
      <div className="card animate-fadeIn bg-gradient-to-br from-primary-50 to-secondary-50 border-2 border-primary-100">
        <div className="flex items-center mb-4">
          <Network className="h-6 w-6 text-primary-600 mr-2" />
          <h2 className="text-xl font-semibold text-gray-800">RAG Pipeline</h2>
        </div>
        
        <div className="space-y-3">
          {features.map((feature, index) => (
            <div key={index} className="bg-white rounded-lg p-3 border border-gray-100 hover:shadow-md transition-shadow">
              <div className="flex items-center justify-between mb-1">
                <div className="flex items-center gap-2">
                  <div className={`bg-gradient-to-r ${feature.color} p-1.5 rounded-md`}>
                    <feature.icon className="w-4 h-4 text-white" />
                  </div>
                  <h3 className="text-sm font-semibold text-gray-800">{feature.title}</h3>
                </div>
                <span className="text-[10px] px-2 py-0.5 bg-primary-100 text-primary-700 rounded-full font-medium">
                  {feature.badge}
                </span>
              </div>
              <p className="text-xs text-gray-600 ml-8">{feature.description}</p>
            </div>
          ))}
        </div>

        {/* Pipeline Flow Visual */}
        <div className="mt-4 pt-4 border-t border-primary-200">
          <div className="flex items-center justify-between text-xs text-gray-600">
            <div className="flex flex-col items-center">
              <div className="w-8 h-8 rounded-full bg-blue-100 flex items-center justify-center mb-1">
                <Search className="w-4 h-4 text-blue-600" />
              </div>
              <span className="font-medium">Search</span>
            </div>
            <Zap className="w-4 h-4 text-gray-400" />
            <div className="flex flex-col items-center">
              <div className="w-8 h-8 rounded-full bg-purple-100 flex items-center justify-center mb-1">
                <Target className="w-4 h-4 text-purple-600" />
              </div>
              <span className="font-medium">Rerank</span>
            </div>
            <Zap className="w-4 h-4 text-gray-400" />
            <div className="flex flex-col items-center">
              <div className="w-8 h-8 rounded-full bg-orange-100 flex items-center justify-center mb-1">
                <Sparkles className="w-4 h-4 text-orange-600" />
              </div>
              <span className="font-medium">Generate</span>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <section className="py-16 bg-gradient-to-br from-gray-50 to-primary-50">
      <div className="container mx-auto px-4">
        <div className="text-center mb-12">
          <div className="inline-flex items-center gap-2 px-4 py-2 bg-primary-100 rounded-full text-primary-700 font-medium text-sm mb-4">
            <Network className="w-4 h-4" />
            <span>Advanced RAG Architecture</span>
          </div>
          <h2 className="text-4xl font-bold text-gray-900 mb-4">
            Powered by State-of-the-Art AI
          </h2>
          <p className="text-xl text-gray-600 max-w-2xl mx-auto">
            Our retrieval-augmented generation pipeline combines multiple AI techniques
            for unparalleled accuracy and relevance
          </p>
        </div>

        <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6 mb-12">
          {features.map((feature, index) => (
            <div
              key={index}
              className="bg-white rounded-xl p-6 border border-gray-100 shadow-lg hover:shadow-2xl transition-all duration-300 group hover:-translate-y-2"
            >
              <div className={`bg-gradient-to-r ${feature.color} w-12 h-12 rounded-xl flex items-center justify-center mb-4 group-hover:scale-110 transition-transform`}>
                <feature.icon className="w-6 h-6 text-white" />
              </div>
              <h3 className="text-lg font-bold text-gray-900 mb-2">
                {feature.title}
              </h3>
              <p className="text-sm text-gray-600 mb-3 leading-relaxed">
                {feature.description}
              </p>
              <span className="inline-block text-xs px-3 py-1 bg-gradient-to-r from-primary-50 to-secondary-50 text-primary-700 rounded-full font-semibold border border-primary-200">
                {feature.badge}
              </span>
            </div>
          ))}
        </div>

        {/* Pipeline Flow Diagram */}
        <div className="bg-white rounded-2xl p-8 shadow-xl border border-gray-100">
          <h3 className="text-2xl font-bold text-center text-gray-900 mb-8">
            How It Works: Query → Answer Pipeline
          </h3>
          
          <div className="flex flex-col md:flex-row items-center justify-between gap-8">
            {/* Step 1: Query */}
            <div className="flex flex-col items-center flex-1">
              <div className="w-20 h-20 rounded-2xl bg-gradient-to-br from-blue-500 to-cyan-500 flex items-center justify-center mb-3 shadow-lg">
                <Search className="w-10 h-10 text-white" />
              </div>
              <h4 className="font-bold text-gray-900 mb-2">1. Hybrid Search</h4>
              <p className="text-sm text-gray-600 text-center">
                Vector (semantic) + BM25 (keyword) search with RRF fusion
              </p>
              <div className="mt-3 px-3 py-1 bg-blue-50 rounded-full text-xs font-medium text-blue-700">
                Dense + Sparse
              </div>
            </div>

            <div className="hidden md:flex items-center">
              <div className="flex flex-col gap-2">
                <div className="w-12 h-0.5 bg-gradient-to-r from-blue-500 to-purple-500"></div>
                <Zap className="w-6 h-6 text-gray-400 mx-auto" />
                <div className="w-12 h-0.5 bg-gradient-to-r from-blue-500 to-purple-500"></div>
              </div>
            </div>

            {/* Step 2: Rerank */}
            <div className="flex flex-col items-center flex-1">
              <div className="w-20 h-20 rounded-2xl bg-gradient-to-br from-purple-500 to-pink-500 flex items-center justify-center mb-3 shadow-lg">
                <Target className="w-10 h-10 text-white" />
              </div>
              <h4 className="font-bold text-gray-900 mb-2">2. Rerank Results</h4>
              <p className="text-sm text-gray-600 text-center">
                Cosine similarity scoring to refine and prioritize context
              </p>
              <div className="mt-3 px-3 py-1 bg-purple-50 rounded-full text-xs font-medium text-purple-700">
                Similarity Score
              </div>
            </div>

            <div className="hidden md:flex items-center">
              <div className="flex flex-col gap-2">
                <div className="w-12 h-0.5 bg-gradient-to-r from-purple-500 to-green-500"></div>
                <Zap className="w-6 h-6 text-gray-400 mx-auto" />
                <div className="w-12 h-0.5 bg-gradient-to-r from-purple-500 to-green-500"></div>
              </div>
            </div>

            {/* Step 3: Context */}
            <div className="flex flex-col items-center flex-1">
              <div className="w-20 h-20 rounded-2xl bg-gradient-to-br from-green-500 to-emerald-500 flex items-center justify-center mb-3 shadow-lg">
                <Brain className="w-10 h-10 text-white" />
              </div>
              <h4 className="font-bold text-gray-900 mb-2">3. Build Context</h4>
              <p className="text-sm text-gray-600 text-center">
                Use embeddings to create semantic understanding
              </p>
              <div className="mt-3 px-3 py-1 bg-green-50 rounded-full text-xs font-medium text-green-700">
                Embeddings
              </div>
            </div>

            <div className="hidden md:flex items-center">
              <div className="flex flex-col gap-2">
                <div className="w-12 h-0.5 bg-gradient-to-r from-green-500 to-orange-500"></div>
                <Zap className="w-6 h-6 text-gray-400 mx-auto" />
                <div className="w-12 h-0.5 bg-gradient-to-r from-green-500 to-orange-500"></div>
              </div>
            </div>

            {/* Step 4: Generate */}
            <div className="flex flex-col items-center flex-1">
              <div className="w-20 h-20 rounded-2xl bg-gradient-to-br from-orange-500 to-red-500 flex items-center justify-center mb-3 shadow-lg">
                <Sparkles className="w-10 h-10 text-white" />
              </div>
              <h4 className="font-bold text-gray-900 mb-2">4. Generate Answer</h4>
              <p className="text-sm text-gray-600 text-center">
                GPT-3.5-Turbo generates contextual answers with citations
              </p>
              <div className="mt-3 px-3 py-1 bg-orange-50 rounded-full text-xs font-medium text-orange-700">
                LLM
              </div>
            </div>
          </div>
        </div>

        {/* Technical Specs */}
        <div className="mt-8 grid md:grid-cols-2 gap-6">
          <div className="bg-gradient-to-br from-blue-50 to-cyan-50 rounded-xl p-6 border border-blue-100">
            <h4 className="font-bold text-gray-900 mb-3 flex items-center gap-2">
              <Brain className="w-5 h-5 text-blue-600" />
              Embedding Model
            </h4>
            <ul className="space-y-2 text-sm text-gray-700">
              <li className="flex items-start gap-2">
                <span className="text-blue-600 font-bold">•</span>
                <span><strong>Model:</strong> text-embedding-3-small</span>
              </li>
              <li className="flex items-start gap-2">
                <span className="text-blue-600 font-bold">•</span>
                <span><strong>Dimensions:</strong> 1536-dimensional vectors</span>
              </li>
              <li className="flex items-start gap-2">
                <span className="text-blue-600 font-bold">•</span>
                <span><strong>Purpose:</strong> Semantic understanding of queries and documents</span>
              </li>
            </ul>
          </div>

          <div className="bg-gradient-to-br from-orange-50 to-red-50 rounded-xl p-6 border border-orange-100">
            <h4 className="font-bold text-gray-900 mb-3 flex items-center gap-2">
              <Sparkles className="w-5 h-5 text-orange-600" />
              Language Model
            </h4>
            <ul className="space-y-2 text-sm text-gray-700">
              <li className="flex items-start gap-2">
                <span className="text-orange-600 font-bold">•</span>
                <span><strong>Model:</strong> GPT-3.5-Turbo</span>
              </li>
              <li className="flex items-start gap-2">
                <span className="text-orange-600 font-bold">•</span>
                <span><strong>Features:</strong> Streaming, reasoning, citations</span>
              </li>
              <li className="flex items-start gap-2">
                <span className="text-orange-600 font-bold">•</span>
                <span><strong>Purpose:</strong> Generate accurate, contextual answers</span>
              </li>
            </ul>
          </div>
        </div>
      </div>
    </section>
  );
};

export default RAGPipelineInfo;

