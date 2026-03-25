"""Model constants configuration."""

import os
from dotenv import load_dotenv

load_dotenv()

CHAT_MODEL = os.getenv('LLM_CHAT_MODEL', 'gpt-3.5-turbo')
EMBEDDING_MODEL = os.getenv('LLM_EMBEDDING_MODEL', 'text-embedding-3-small')

DEFAULT_CHAT_MODEL = CHAT_MODEL
DEFAULT_EMBEDDING_MODEL = EMBEDDING_MODEL
