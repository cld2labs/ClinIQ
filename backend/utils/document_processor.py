"""
Document Processor Module

This module handles all document-related operations:
1. Extracting text from different file formats (PDF, DOCX, TXT)
2. Breaking text into smaller chunks for processing
3. Creating embeddings (vector representations) of text

These functions are the foundation of the RAG system - they prepare documents
so they can be searched and queried by the AI.
"""

import PyPDF2
import docx
import tiktoken
import openai
from openai import OpenAI

def extract_text_from_pdf(file):
    """
    Extracts text from a PDF file, page by page.
    
    This function reads a PDF document and extracts all text content while
    preserving page numbers. Page numbers are crucial for citations - they
    allow users to see exactly where information came from in the original document.
    
    How it works:
    1. Uses PyPDF2 to read the PDF file
    2. Iterates through each page
    3. Extracts text from each page
    4. Returns a list of (text, page_number) tuples
    
    Args:
        file: File object or file path of the PDF to process
        
    Returns:
        list: List of tuples, where each tuple contains:
            - text (str): The extracted text from a page
            - page_number (int): The page number (1-indexed)
            
    Example:
        Input: PDF with 3 pages
        Output: [
            ("Page 1 text content...", 1),
            ("Page 2 text content...", 2),
            ("Page 3 text content...", 3)
        ]
        
    Note:
        - Only extracts text, not images or tables
        - Skips empty pages
        - Page numbers start at 1 (not 0)
    """
    reader = PyPDF2.PdfReader(file)
    pages_text = []
    
    # Iterate through each page in the PDF
    for i, page in enumerate(reader.pages):
        # Extract text from the current page
        extracted = page.extract_text()
        
        # Only add non-empty pages to the results
        if extracted:
            # Store text with page number (1-indexed for user-friendly citations)
            pages_text.append((extracted, i + 1))
    
    return pages_text

def extract_text_from_docx(file):
    """
    Extracts text from a Microsoft Word document (.docx file).
    
    This function reads a Word document and extracts all text content from
    paragraphs. Word documents don't have explicit page numbers like PDFs,
    so we treat the entire document as a single unit.
    
    How it works:
    1. Uses python-docx library to open the document
    2. Iterates through all paragraphs
    3. Concatenates paragraph text with newlines
    4. Returns the complete text as a string
    
    Args:
        file: File object or file path of the .docx file to process
        
    Returns:
        str: All text content from the document, with paragraphs separated by newlines
        
    Example:
        Input: Word document with paragraphs
        Output: "First paragraph text...\nSecond paragraph text...\n..."
        
    Note:
        - Extracts text from paragraphs only
        - Tables and images are not extracted
        - Preserves paragraph structure with newlines
    """
    # Open the Word document
    doc = docx.Document(file)
    
    # Initialize empty string to store all text
    text = ""
    
    # Iterate through all paragraphs in the document
    for para in doc.paragraphs:
        # Add paragraph text followed by a newline
        # This preserves the paragraph structure
        text += para.text + "\n"
    
    return text

def chunk_text(text, chunk_size=800, overlap=150):
    """
    Breaks long text into smaller, manageable chunks.
    
    This is a critical function for RAG (Retrieval-Augmented Generation) systems.
    Large documents are split into smaller pieces because:
    1. AI models have token limits (can't process entire books at once)
    2. Smaller chunks allow more precise search and retrieval
    3. Overlapping chunks ensure no important context is lost at boundaries
    
    How it works:
    1. Encodes text into tokens (AI-readable units)
    2. Creates chunks of specified size (800 tokens)
    3. Overlaps chunks by 150 tokens to preserve context
    4. Decodes tokens back to text for each chunk
    
    Args:
        text (str): The text to chunk (can be very long)
        chunk_size (int): Number of tokens per chunk (default: 800)
                         - Larger chunks = more context but fewer chunks
                         - Smaller chunks = less context but more precise search
        overlap (int): Number of overlapping tokens between chunks (default: 150)
                      - Prevents losing context at chunk boundaries
                      - Example: If a sentence spans two chunks, overlap ensures
                        it's captured in both
    
    Returns:
        list: List of text chunks, each as a string
        
    Example:
        Input: "Very long document text..." (5000 tokens)
        Output: [
            "Chunk 1 text (tokens 0-800)...",
            "Chunk 2 text (tokens 650-1450)...",  # Overlaps with chunk 1
            "Chunk 3 text (tokens 1300-2100)...",  # Overlaps with chunk 2
            ...
        ]
        
    Why Overlap Matters:
        Without overlap, a sentence like "The patient's condition improved
        significantly" might be split as:
        - Chunk 1: "...condition improved"
        - Chunk 2: "significantly..."
        
        With overlap, both chunks contain the full sentence, ensuring
        the AI can understand the complete context.
    """
    # Get the tokenizer for the model we're using
    # "cl100k_base" is the encoding used by GPT-3.5 and GPT-4
    enc = tiktoken.get_encoding("cl100k_base")
    
    # Convert text into tokens (numbers that represent words/subwords)
    # This is how AI models understand text
    tokens = enc.encode(text)
    
    chunks = []  # List to store the resulting text chunks
    start = 0  # Starting position in the token array
    
    # Continue chunking until we've processed all tokens
    while start < len(tokens):
        # Calculate end position for this chunk
        end = start + chunk_size
        
        # Extract tokens for this chunk
        chunk_tokens = tokens[start:end]
        
        # Convert tokens back to readable text
        chunk_text = enc.decode(chunk_tokens)
        chunks.append(chunk_text)
        
        # Move start position forward, accounting for overlap
        # Example: chunk_size=800, overlap=150
        # Chunk 1: tokens 0-800
        # Chunk 2: tokens 650-1450 (starts at 800-150=650, overlaps by 150)
        start += (chunk_size - overlap)
        
    return chunks

def create_embeddings(chunks, api_key):
    """
    Converts text chunks into embeddings (vector representations).
    
    Embeddings are the "digital fingerprints" of text. They convert words
    into numbers (vectors) that capture the meaning of the text. This allows
    the system to:
    1. Search documents by meaning, not just keywords
    2. Find similar content even if different words are used
    3. Perform fast similarity calculations
    
    How it works:
    1. Sends text chunks to OpenAI's embedding API
    2. OpenAI's model converts each chunk into a vector (list of numbers)
    3. Returns embeddings that can be stored and searched
    
    What are Embeddings?
        - A vector (list of numbers) that represents text meaning
        - Similar texts have similar vectors
        - Example: "heart attack" and "myocardial infarction" have similar embeddings
        - Dimensions: text-embedding-3-small creates 1536-dimensional vectors
        
    Args:
        chunks (list): List of text strings to convert to embeddings
        api_key (str): OpenAI API key for authentication
        
    Returns:
        list: List of embedding vectors, one for each input chunk
              Each embedding is a list of 1536 numbers (floats)
              
    Example:
        Input: ["Patient has diabetes", "Medication dosage is 10mg"]
        Output: [
            [0.123, -0.456, 0.789, ...],  # 1536 numbers for first chunk
            [0.234, -0.567, 0.890, ...]  # 1536 numbers for second chunk
        ]
        
    API Details:
        - Model: text-embedding-3-small (OpenAI's efficient embedding model)
        - Cost: Very cheap compared to chat models
        - Speed: Fast batch processing
        - Quality: Optimized for semantic similarity search
        
    Note:
        - This function makes an API call to OpenAI
        - All chunks are processed in a single API call (batch processing)
        - The API key is used only in memory and not persisted
    """
    # Create OpenAI client instance
    # API key is passed directly to the client and not stored in environment
    client = OpenAI(api_key=api_key)
    
    # Call OpenAI's embedding API
    # This converts all text chunks into vector representations in one call
    response = client.embeddings.create(
        input=chunks,  # List of text chunks to embed
        model="text-embedding-3-small"  # OpenAI's efficient embedding model
    )
    
    # Extract embeddings from the response
    # Each data object contains one embedding vector
    return [data.embedding for data in response.data]
