# Use Python 3.11
FROM python:3.11-slim

# Set environment variables for UTF-8 encoding
# This ensures Python handles Unicode characters (emojis) correctly
ENV PYTHONIOENCODING=utf-8
ENV LANG=C.UTF-8
ENV LC_ALL=C.UTF-8

# Set working directory
WORKDIR /app

# Install system dependencies (including curl for healthcheck)
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY backend/requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY backend/ .

# Create necessary directories
RUN mkdir -p uploads .chromadb \
    && useradd --create-home --uid 10001 appuser \
    && chown -R appuser:appuser /app

# Expose port
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --retries=3 --start-period=40s \
    CMD curl -f http://localhost:5000/api/health || exit 1

# Run the application as non-root
USER appuser
CMD ["python", "api.py"]
