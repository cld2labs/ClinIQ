"""Configuration management for ClinIQ application."""

import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Application configuration loaded from environment variables."""

    LLM_PROVIDER = os.getenv('LLM_PROVIDER', 'openai').lower()
    LLM_API_KEY = os.getenv('LLM_API_KEY') or os.getenv('OPENAI_API_KEY', '')
    LLM_BASE_URL = os.getenv('LLM_BASE_URL', 'https://api.openai.com/v1')
    LLM_CHAT_MODEL = os.getenv('LLM_CHAT_MODEL', 'gpt-3.5-turbo')
    LLM_EMBEDDING_MODEL = os.getenv('LLM_EMBEDDING_MODEL', 'text-embedding-3-small')
    TEMPERATURE = float(os.getenv('TEMPERATURE', '0.7'))
    MAX_TOKENS = int(os.getenv('MAX_TOKENS', '1000'))
    MAX_RETRIES = int(os.getenv('MAX_RETRIES', '3'))
    REQUEST_TIMEOUT = int(os.getenv('REQUEST_TIMEOUT', '300'))
    VERIFY_SSL = os.getenv('VERIFY_SSL', 'true').lower() == 'true'
    FLASK_ENV = os.getenv('FLASK_ENV', 'development')
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', '')

    @classmethod
    def get_api_key(cls, provided_key=None):
        """Get API key with fallback logic."""
        if provided_key:
            return provided_key
        return cls.LLM_API_KEY or cls.OPENAI_API_KEY

    @classmethod
    def validate_config(cls):
        """Validate configuration for current provider."""
        if cls.LLM_PROVIDER == 'ollama':
            if not cls.LLM_BASE_URL:
                return False, "LLM_BASE_URL is required for Ollama"
            return True, None

        if not cls.LLM_API_KEY and not cls.OPENAI_API_KEY:
            return False, f"API key is required for provider: {cls.LLM_PROVIDER}"

        if not cls.LLM_BASE_URL:
            return False, "LLM_BASE_URL is required"

        return True, None

    @classmethod
    def get_provider_info(cls):
        """Get information about current provider configuration."""
        return {
            'provider': cls.LLM_PROVIDER,
            'base_url': cls.LLM_BASE_URL,
            'chat_model': cls.LLM_CHAT_MODEL,
            'embedding_model': cls.LLM_EMBEDDING_MODEL,
            'temperature': cls.TEMPERATURE,
            'max_tokens': cls.MAX_TOKENS,
            'has_api_key': bool(cls.get_api_key()),
            'verify_ssl': cls.VERIFY_SSL
        }


config = Config()
