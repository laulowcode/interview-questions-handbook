# Docker Setup for Streaming Examples

This example has its own **isolated Docker setup** to keep things lightweight and fast!

##  Why Separate Docker Setup?

Instead of using the main project's Dockerfile (which includes Redis, RQ, and many other dependencies), this example has:

- **`Dockerfile`** - Lightweight image with only streaming dependencies
- **`requirements.txt`** - Minimal requirements (FastAPI, uvicorn, httpx, aiofiles)
- **`.dockerignore`** - Optimized build context

### Benefits

| Main Project | Streaming Example |
|-------------|-------------------|
| ~500 MB image | ~200 MB image |
| 15+ dependencies | 4 dependencies |
| Needs Redis | No external services |
| Slower builds | Fast builds (~30s) |

##  What's Included

```
04-streaming-chunked-responses/
 Dockerfile              # Lightweight Python 3.11 image
 requirements.txt        # Only FastAPI + uvicorn + httpx + aiofiles
 .dockerignore          # Excludes unnecessary files
 docker-compose.yml     # Service definition (in parent directory)
 run_docker.sh          # Helper script for common tasks
 streaming_examples.py  # FastAPI server
 client_examples.py     # Client examples
```

##  Quick Start

### Start the Server

```bash
# From python/ directory
cd python/

# Build and start (first time takes ~1 minute)
docker compose up streaming-api

# Or run in background
docker compose up -d streaming-api
```

### Access the API

- **API**: http://localhost:8000
- **Interactive Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

### Run Client Examples

```bash
# Use helper script (easiest)
cd 02-performance-caching-scale/04-streaming-chunked-responses/
./run_docker.sh client

# Or run directly
docker compose exec streaming-api python client_examples.py
```

### Stop the Server

```bash
docker compose stop streaming-api

# Remove container
docker compose down streaming-api
```

##  Helper Script

The `run_docker.sh` script provides convenient commands:

```bash
./run_docker.sh start      # Start server
./run_docker.sh stop       # Stop server
./run_docker.sh restart    # Restart server
./run_docker.sh logs       # View logs (follow mode)
./run_docker.sh client     # Run client examples
./run_docker.sh test       # Quick API tests
./run_docker.sh status     # Check if running
./run_docker.sh shell      # Open bash shell in container
./run_docker.sh build      # Rebuild image
./run_docker.sh help       # Show help
```

**Make it executable:**
```bash
chmod +x run_docker.sh
```

##  Docker Configuration Details

### Dockerfile Breakdown

```dockerfile
FROM python:3.11-slim           # Minimal Python image
WORKDIR /app                     # Working directory
COPY requirements.txt .          # Copy dependencies first (layer caching)
RUN pip install -r requirements.txt  # Install only what's needed
COPY *.py .                      # Copy Python files
USER app                         # Run as non-root user
EXPOSE 8000                      # API port
CMD ["uvicorn", "streaming_examples:app", "--host", "0.0.0.0", "--port", "8000"]
```

### docker-compose.yml Entry

```yaml
streaming-api:
  build:
    context: ./02-performance-caching-scale/04-streaming-chunked-responses
    dockerfile: Dockerfile
  container_name: python-interview-streaming-api
  volumes:
    - ./02-performance-caching-scale/04-streaming-chunked-responses:/app
  ports:
    - "8000:8000"
  command: uvicorn streaming_examples:app --host 0.0.0.0 --port 8000 --reload
```

**Key Features:**
-  Hot reload enabled for development
-  Only mounts streaming examples directory
-  No dependencies on other services (Redis, etc.)
-  Standalone service

##  Testing

### Test with curl

```bash
# Health check
curl http://localhost:8000/health

# Real-time stock ticker (Ctrl+C to stop)
curl -N http://localhost:8000/stream/stock-ticker

# AI streaming
curl "http://localhost:8000/ai/chat-stream?prompt=Tell%20me%20about%20Python"

# Download file
curl http://localhost:8000/download/large-file -o test.bin

# CSV export
curl http://localhost:8000/export/users/csv -o users.csv
```

### Test with Browser

Visit http://localhost:8000/docs for interactive Swagger UI where you can test all endpoints.

### Test with Python Client

```bash
# Run all client examples
./run_docker.sh client

# Or manually
docker compose exec streaming-api python client_examples.py
```

##  Container Management

### View Logs

```bash
# Follow logs
docker compose logs -f streaming-api

# Last 100 lines
docker compose logs --tail=100 streaming-api
```

### Check Status

```bash
# Using helper script
./run_docker.sh status

# Or manually
docker compose ps streaming-api
```

### Shell Access

```bash
# Using helper script
./run_docker.sh shell

# Or manually
docker compose exec streaming-api /bin/bash
```

### Resource Usage

```bash
# Check resource usage
docker stats python-interview-streaming-api
```

##  Customization

### Change Port

Edit `docker-compose.yml`:
```yaml
ports:
  - "8080:8000"  # Use port 8080 on host
```

### Add Environment Variables

Edit `docker-compose.yml`:
```yaml
environment:
  - PYTHONUNBUFFERED=1
  - API_KEY=your_key_here
  - LOG_LEVEL=debug
```

### Mount Additional Files

Edit `docker-compose.yml`:
```yaml
volumes:
  - ./02-performance-caching-scale/04-streaming-chunked-responses:/app
  - ./data:/app/data  # Mount external data directory
```

##  Troubleshooting

### Port Already in Use

```bash
# Check what's using port 8000
lsof -i :8000

# Change port in docker-compose.yml
ports:
  - "8001:8000"
```

### Container Won't Start

```bash
# Check logs
docker compose logs streaming-api

# Rebuild image
docker compose build --no-cache streaming-api

# Remove and recreate
docker compose down
docker compose up streaming-api
```

### Hot Reload Not Working

Make sure the volume is mounted correctly:
```yaml
volumes:
  - ./02-performance-caching-scale/04-streaming-chunked-responses:/app
```

Changes to `.py` files should automatically reload the server.

### Health Check Fails

```bash
# Test health endpoint manually
docker compose exec streaming-api python -c "import urllib.request; print(urllib.request.urlopen('http://localhost:8000/health').read())"

# Check if uvicorn is running
docker compose exec streaming-api ps aux
```

##  Building for Production

### Build Optimized Image

```bash
# Build without cache
docker compose build --no-cache streaming-api

# Build with specific tag
docker build -t streaming-api:v1.0 ./02-performance-caching-scale/04-streaming-chunked-responses/
```

### Run in Production Mode

Remove `--reload` flag from command:
```yaml
command: uvicorn streaming_examples:app --host 0.0.0.0 --port 8000 --workers 4
```

### Multi-stage Build (Advanced)

For even smaller images, you can use multi-stage builds:
```dockerfile
# Build stage
FROM python:3.11-slim as builder
WORKDIR /app
COPY requirements.txt .
RUN pip wheel --no-cache-dir --wheel-dir /wheels -r requirements.txt

# Runtime stage
FROM python:3.11-slim
WORKDIR /app
COPY --from=builder /wheels /wheels
RUN pip install --no-cache /wheels/*
COPY *.py .
CMD ["uvicorn", "streaming_examples:app", "--host", "0.0.0.0", "--port", "8000"]
```
