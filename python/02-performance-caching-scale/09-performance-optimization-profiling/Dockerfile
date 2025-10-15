# Lightweight Dockerfile for Performance Profiling Examples
# This is a standalone setup optimized for profiling demonstrations

FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Set work directory
WORKDIR /app

# Install system dependencies needed for profiling tools
RUN apt-get update && apt-get install -y \
    build-essential \
    graphviz \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better layer caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# Copy all Python files
COPY *.py .
COPY *.md .

# Create directories for profiling output
RUN mkdir -p /app/profiles /app/reports

# Create a non-root user for security
RUN useradd --create-home --shell /bin/bash app && \
    chown -R app:app /app

USER app

# Default command - show help
CMD ["python", "-c", "print('\\n=== Performance Profiling Examples ===\\n\\nAvailable examples:\\n  python profiling_example.py\\n  python advanced_profiling.py\\n  python line_profiling_example.py\\n\\nOr use the run_docker.sh helper script\\n')"]

