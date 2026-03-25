"""Universal LLM service supporting multiple providers."""

import time
from typing import List, Dict, Optional, Iterator
from openai import OpenAI
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type


class LLMService:
    """Universal LLM service supporting multiple providers."""

    PROVIDER_BASE_URLS = {
        'openai': 'https://api.openai.com/v1',
        'groq': 'https://api.groq.com/openai/v1',
        'ollama': 'http://localhost:11434/v1',
        'openrouter': 'https://openrouter.ai/api/v1',
        'custom': None
    }

    def __init__(
        self,
        provider: str = 'openai',
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        chat_model: str = 'gpt-3.5-turbo',
        embedding_model: str = 'text-embedding-3-small',
        temperature: float = 0.7,
        max_tokens: int = 1000,
        max_retries: int = 3,
        request_timeout: int = 300,
        verify_ssl: bool = True
    ):
        """Initialize LLM service."""
        self.provider = provider.lower()
        self.chat_model = chat_model
        self.embedding_model = embedding_model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.max_retries = max_retries
        self.request_timeout = request_timeout
        self.verify_ssl = verify_ssl

        if base_url:
            self.base_url = base_url
        elif self.provider in self.PROVIDER_BASE_URLS:
            self.base_url = self.PROVIDER_BASE_URLS[self.provider]
        else:
            self.base_url = self.PROVIDER_BASE_URLS['openai']

        if self.provider == 'ollama':
            self.api_key = 'ollama'
        else:
            self.api_key = api_key or ''

        import httpx
        http_client = httpx.Client(verify=self.verify_ssl)

        self.client = OpenAI(
            api_key=self.api_key,
            base_url=self.base_url,
            timeout=self.request_timeout,
            http_client=http_client
        )

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((Exception,)),
        reraise=True
    )
    def _make_request_with_retry(self, request_func, *args, **kwargs):
        """Make API request with retry logic."""
        return request_func(*args, **kwargs)

    def create_chat_completion(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        stream: bool = False,
        **kwargs
    ):
        """Create chat completion."""
        model = model or self.chat_model
        temperature = temperature if temperature is not None else self.temperature
        max_tokens = max_tokens or self.max_tokens

        return self._make_request_with_retry(
            self.client.chat.completions.create,
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            stream=stream,
            **kwargs
        )

    def create_chat_completion_stream(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> Iterator[str]:
        """Create streaming chat completion."""
        stream = self.create_chat_completion(
            messages=messages,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            stream=True,
            **kwargs
        )

        for chunk in stream:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content

    def create_embeddings(
        self,
        texts: List[str],
        model: Optional[str] = None,
        **kwargs
    ) -> List[List[float]]:
        """Create embeddings for text chunks."""
        model = model or self.embedding_model

        response = self._make_request_with_retry(
            self.client.embeddings.create,
            model=model,
            input=texts,
            **kwargs
        )

        return [data.embedding for data in response.data]

    def create_single_embedding(
        self,
        text: str,
        model: Optional[str] = None,
        **kwargs
    ) -> List[float]:
        """Create embedding for a single text."""
        embeddings = self.create_embeddings([text], model=model, **kwargs)
        return embeddings[0]

    def get_provider_info(self) -> Dict:
        """Get information about current provider configuration."""
        return {
            'provider': self.provider,
            'base_url': self.base_url,
            'chat_model': self.chat_model,
            'embedding_model': self.embedding_model,
            'temperature': self.temperature,
            'max_tokens': self.max_tokens,
            'verify_ssl': self.verify_ssl,
            'has_api_key': bool(self.api_key and self.api_key != 'ollama')
        }


def create_llm_service(
    provider: Optional[str] = None,
    api_key: Optional[str] = None,
    base_url: Optional[str] = None,
    chat_model: Optional[str] = None,
    embedding_model: Optional[str] = None,
    **kwargs
) -> LLMService:
    """Factory function to create LLM service from config."""
    from config import config as app_config

    return LLMService(
        provider=provider or app_config.LLM_PROVIDER,
        api_key=api_key or app_config.get_api_key(),
        base_url=base_url or app_config.LLM_BASE_URL,
        chat_model=chat_model or app_config.LLM_CHAT_MODEL,
        embedding_model=embedding_model or app_config.LLM_EMBEDDING_MODEL,
        temperature=kwargs.get('temperature', app_config.TEMPERATURE),
        max_tokens=kwargs.get('max_tokens', app_config.MAX_TOKENS),
        max_retries=kwargs.get('max_retries', app_config.MAX_RETRIES),
        request_timeout=kwargs.get('request_timeout', app_config.REQUEST_TIMEOUT),
        verify_ssl=kwargs.get('verify_ssl', app_config.VERIFY_SSL)
    )
