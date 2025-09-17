# MCP Documentation Server Docker Image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY ../requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy model download script
COPY docker/download_models.py .

# Create cache directory for HuggingFace models
RUN mkdir -p /root/.cache/huggingface

# Pre-download embedding models
RUN python download_models.py

# Copy application source files
COPY ../models.py .
COPY ../server.py .
COPY ../search_engine_faiss.py .

# Create docs directory for documentation
RUN mkdir -p /app/docs

# Copy pre-built embeddings
COPY ../embeddings /app/embeddings

# Expose port 8008 (as specified in the command)
EXPOSE 8008

# Set environment variables
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Default command (can be overridden in docker-compose)
CMD ["python", "server.py", "--transport", "http", "--host", "0.0.0.0", "--port", "8008", "--server-name", "logzilla-docs-server", "--description", "logzilla documentation", "--embedding-path", "/app/embeddings", "--embedding-name", "logzilla_md_docs"]
