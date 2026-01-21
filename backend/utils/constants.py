"""
Constants Module

This module defines the AI models used throughout the application.
Centralizing these constants makes it easy to:
1. Update models in one place
2. Experiment with different models
3. Maintain consistency across the codebase

These models are from OpenAI and are used for:
- Chat/Conversation: GPT-3.5-Turbo (for generating answers)
- Embeddings: text-embedding-3-small (for creating vector representations)
"""

# Chat Model: Used for generating answers to user questions
# GPT-3.5-Turbo is OpenAI's efficient and cost-effective chat model
# It's optimized for conversational AI and question-answering tasks
# Alternative: "gpt-4" for better quality but higher cost
CHAT_MODEL = "gpt-3.5-turbo"

# Embedding Model: Used for converting text into vector representations
# text-embedding-3-small is OpenAI's efficient embedding model
# Creates 1536-dimensional vectors optimized for semantic search
# Alternative: "text-embedding-3-large" for better quality but higher cost
EMBEDDING_MODEL = "text-embedding-3-small"
