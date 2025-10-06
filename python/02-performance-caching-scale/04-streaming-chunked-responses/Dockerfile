# Lightweight Dockerfile for FastAPI Streaming Examples
# Optimized for minimal size and fast builds

FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Set work directory
WORKDIR /app

# Install only minimal system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy only the requirements for this example
COPY requirements.txt .

# Install Python dependencies (minimal set)
RUN pip install --no-cache-dir -r requirements.txt

# Copy only the streaming examples
COPY streaming_examples.py .
COPY client_examples.py .
COPY README.md .
COPY QUICKSTART.md .

# Create a non-root user for security
RUN useradd --create-home --shell /bin/bash app && \
    chown -R app:app /app
USER app

# Expose port for FastAPI
EXPOSE 8000

# Health check
HEALTHCHECK --interval=10s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')" || exit 1

# Default: Run the FastAPI server
CMD ["uvicorn", "streaming_examples:app", "--host", "0.0.0.0", "--port", "8000"]

