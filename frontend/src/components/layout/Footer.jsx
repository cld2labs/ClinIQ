export const Footer = () => {
  return (
    <footer className="bg-white border-t border-gray-200 mt-auto">
      <div className="container mx-auto px-4 sm:px-6 lg:px-8 py-6">
        <div className="flex flex-col md:flex-row justify-between items-center">
          <div className="flex items-center gap-2 mb-4 md:mb-0">
            <img
              src="/cloud2labs-logo.png"
              alt="ClinIQ"
              className="h-6 w-6 object-contain"
            />
            <span className="text-sm text-gray-600">ClinIQ - Clinical Knowledge Assistant</span>
          </div>
          <p className="text-sm text-gray-500">
            Powered by OpenAI GPT-3.5-Turbo
          </p>
        </div>
      </div>
    </footer>
  );
};

export default Footer;


