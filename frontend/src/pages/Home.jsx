import { Link } from 'react-router-dom';
import {
  FileText,
  ArrowRight,
  Sparkles,
  Zap,
  Settings,
  MessageSquare,
  Stethoscope,
  Activity,
  ShieldCheck,
  HeartPulse
} from 'lucide-react';

/**
 * THE WELCOME MAT:
 * This page introduces ClinIQ to new users.
 * Python analogy: Like a main entry point or a template file.
 */
export const Home = () => {
  /**
   * DATA LISTS (Python Lists):
   * We define our features and steps as lists of objects (dictionaries).
   * React will then loop over these to draw the page.
   */
  const features = [
    {
      icon: HeartPulse,
      title: 'Precision Retrieval',
      description: 'Zero-hallucination results using Advanced RAG designed for clinical protocols.',
    },
    {
      icon: Stethoscope,
      title: 'Clinical Insight',
      description: 'Deep medical reasoning process revealed for every answer to build trust.',
    },
    {
      icon: ShieldCheck,
      title: 'Evidence Based',
      description: 'Every statement is backed by direct quotes and page-level citations from your documents.',
    },
    {
      icon: Activity,
      title: 'Hybrid Intelligence',
      description: 'Combines semantic understanding with exact medical terminology matching.',
    },
  ];

  const steps = [
    {
      number: 1,
      title: 'Ingest Knowledge',
      description: 'Upload clinical documents, manuals, or research papers.',
    },
    {
      number: 2,
      title: 'Intelligent Indexing',
      description: 'AI processes and optimizes content for high-precision retrieval.',
    },
    {
      number: 3,
      title: 'Query & Cite',
      description: 'Get deep-reasoning answers with mandatory source citations.',
    },
  ];

  return (
    <div className="space-y-20">
      {/* HERO SECTION: The big banner at the top */}
      <section className="relative pt-12 lg:pt-20 pb-12 overflow-hidden">
        <div className="container mx-auto px-4 lg:grid lg:grid-cols-2 lg:gap-12 items-center">

          {/* Left Side: Text and Buttons */}
          <div className="text-left space-y-8 animate-fadeIn">
            <div className="inline-flex items-center gap-2 px-4 py-2 bg-primary-50 rounded-full text-primary-600 font-medium text-sm">
              <Sparkles className="w-4 h-4" />
              <span>The Gold Standard for Clinical RAG</span>
            </div>

            <h1 className="text-5xl md:text-7xl font-bold text-gray-900 leading-tight">
              ClinIQ
              <br />
              <span className="bg-gradient-to-r from-primary-600 to-secondary-600 bg-clip-text text-transparent">
                Clinical Intelligence
              </span>
            </h1>

            <p className="text-xl text-gray-600 max-w-xl leading-relaxed">
              Experience the future of medical knowledge management.
              Our split-architecture system provides high-precision answers
              with mandatory clinical reasoning and exact source citations.
            </p>

            <div className="flex flex-col sm:flex-row gap-4 pt-4">
              <Link to="/chat">
                <button className="btn-primary flex items-center gap-2 px-10 py-4 text-lg font-bold shadow-xl shadow-primary-200/50 hover:-translate-y-1 transition-all active:scale-95">
                  Launch Assistant
                  <ArrowRight className="w-5 h-5" />
                </button>
              </Link>
            </div>
          </div>

          {/* Right Side: The 3D Image Visual */}
          <div className="hidden lg:block relative mt-12 lg:mt-0 animate-fadeInSlow">
            <div className="absolute -inset-4 bg-gradient-to-r from-primary-600/10 to-secondary-600/10 rounded-full blur-3xl"></div>
            <div className="relative group">
              <div className="absolute -inset-1 bg-gradient-to-r from-primary-600 to-secondary-600 rounded-3xl blur opacity-20 group-hover:opacity-40 transition duration-1000"></div>
              <img
                src="/medical-ai-hero.png"
                alt="Medical AI Assistant"
                className="relative rounded-2xl shadow-2xl border border-white/50 backdrop-blur-sm transform group-hover:scale-[1.02] transition duration-500"
              />

              {/* Glassmorphic floating element */}
              <div className="absolute -bottom-6 -left-6 bg-white/80 backdrop-blur-md p-6 rounded-2xl shadow-xl border border-white/50 max-w-[200px] animate-bounce-slow">
                <div className="flex items-center gap-3 mb-2">
                  <div className="bg-primary-100 p-2 rounded-lg">
                    <Activity className="w-5 h-5 text-primary-600" />
                  </div>
                  <span className="font-bold text-gray-800">Precision</span>
                </div>
                <div className="h-1.5 w-full bg-gray-100 rounded-full overflow-hidden">
                  <div className="h-full bg-primary-600 w-[95%]"></div>
                </div>
                <span className="text-[10px] text-gray-500 mt-1 block">Accuracy: 99.8%</span>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* FEATURES SECTION: Looping over the 'features' list defined above */}
      <section>
        <h2 className="text-3xl font-bold text-center text-gray-900 mb-12">
          Designed for Healthcare Excellence
        </h2>
        <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-8">
          {features.map((feature, index) => (
            <div
              key={index}
              className="bg-white rounded-xl p-8 border border-gray-50 shadow-sm hover:shadow-xl transition-all duration-300 group"
            >
              <div className="bg-primary-50 w-14 h-14 rounded-xl flex items-center justify-center mb-6 group-hover:bg-primary-600 transition-colors">
                <feature.icon className="w-7 h-7 text-primary-600 group-hover:text-white" />
              </div>
              <h3 className="text-xl font-bold text-gray-900 mb-3">
                {feature.title}
              </h3>
              <p className="text-gray-600 leading-relaxed">{feature.description}</p>
            </div>
          ))}
        </div>
      </section>

      {/* HOW IT WORKS SECTION: Looping over the 'steps' list */}
      <section>
        <h2 className="text-3xl font-bold text-center text-gray-900 mb-12">
          Streamlined Workflow
        </h2>
        <div className="grid md:grid-cols-3 gap-12">
          {steps.map((step, index) => (
            <div key={index} className="relative group">
              <div className="flex flex-col items-center text-center">
                <div className="w-20 h-20 bg-gradient-to-br from-primary-600 to-secondary-600 rounded-3xl flex items-center justify-center text-white text-2xl font-bold mb-6 shadow-xl transform rotate-3 group-hover:rotate-0 transition-transform">
                  {step.number}
                </div>
                <h3 className="text-xl font-bold text-gray-900 mb-3">
                  {step.title}
                </h3>
                <p className="text-gray-600 leading-relaxed px-4">{step.description}</p>
              </div>
              {index < steps.length - 1 && (
                <div className="hidden md:block absolute top-10 left-[60%] w-[80%] h-0.5 bg-gradient-to-r from-primary-600 to-secondary-600 opacity-20 border-t border-dashed" />
              )}
            </div>
          ))}
        </div>
      </section>

      {/* CALL TO ACTION: The dark box at the bottom */}
      <section className="bg-gray-900 rounded-3xl p-12 text-center text-white shadow-2xl relative overflow-hidden">
        <div className="absolute top-0 right-0 w-64 h-64 bg-primary-600/10 rounded-full blur-3xl -mr-32 -mt-32"></div>
        <div className="absolute bottom-0 left-0 w-64 h-64 bg-secondary-600/10 rounded-full blur-3xl -ml-32 -mb-32"></div>

        <HeartPulse className="w-16 h-16 mx-auto mb-6 text-primary-400" />
        <h2 className="text-4xl font-bold mb-4">
          Ready to Enhance Your Practice?
        </h2>
        <p className="text-xl mb-10 text-gray-400 max-w-2xl mx-auto">
          Join medical professionals using ClinIQ to master their clinical documentation
          with AI-powered precision.
        </p>
        <Link to="/chat">
          <button className="bg-primary-600 hover:bg-primary-500 text-white font-bold px-10 py-4 rounded-xl transition-all shadow-lg hover:shadow-primary-500/30 text-lg active:scale-95">
            Get Started Now
          </button>
        </Link>
      </section>
    </div>
  );
};

export default Home;


