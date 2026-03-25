"""Document processing utilities for text extraction, chunking, and embedding creation."""

import PyPDF2
import docx
import tiktoken
import openai
from openai import OpenAI

def extract_text_from_pdf(file):
    """Extract text from PDF file, page by page."""
    reader = PyPDF2.PdfReader(file)
    pages_text = []

    for i, page in enumerate(reader.pages):
        extracted = page.extract_text()
        if extracted:
            pages_text.append((extracted, i + 1))

    return pages_text

def extract_text_from_docx(file):
    """Extract text from Word document."""
    doc = docx.Document(file)
    text = ""

    for para in doc.paragraphs:
        text += para.text + "\n"

    return text

def chunk_text(text, chunk_size=800, overlap=150):
    """Break text into smaller chunks with overlap."""
    enc = tiktoken.get_encoding("cl100k_base")
    tokens = enc.encode(text)

    chunks = []
    start = 0

    while start < len(tokens):
        end = start + chunk_size
        chunk_tokens = tokens[start:end]
        chunk_text = enc.decode(chunk_tokens)
        chunks.append(chunk_text)
        start += (chunk_size - overlap)

    return chunks

def create_embeddings(chunks, api_key):
    """Convert text chunks into embeddings using configured LLM provider."""
    from services.llm_service import create_llm_service

    try:
        llm_service = create_llm_service(api_key=api_key)
        embeddings = llm_service.create_embeddings(chunks)
        return embeddings

    except Exception as e:
        error_msg = str(e)
        if '401' in error_msg or 'Unauthorized' in error_msg or 'authentication' in error_msg.lower():
            raise ValueError(f"Invalid API key. Please check your API key and try again.")
        raise Exception(f"LLM API error: {error_msg}")
