# Streaming/chunked responses: when does backend need to stream data? How to implement?

## When to Stream Data

- **Large File Transfers**: When a user requests a large file (e.g., video, database backup, large CSV), loading the entire file into memory before sending it is inefficient and can crash your server. Streaming reads and sends the file in small chunks.

- **Real-Time Data Feeds**: For applications that provide continuous updates, like stock tickers, live sports scores, or social media feeds. The connection remains open, and the server pushes new data as it occurs.

- **Processing Large Datasets**: When performing a long-running task that generates output incrementally (e.g., a complex report or a data processing pipeline). You can stream the results back to the client as they are computed instead of waiting for the entire job to finish.

- **AI and LLM Responses**: Large Language Models generate responses token-by-token. Streaming these tokens as they are generated provides a much better user experience, showing the response appearing gradually rather than a long wait followed by a wall of text.

## Code Examples

This directory contains comprehensive FastAPI examples demonstrating different streaming techniques.

### Files

- **`streaming_examples.py`** - FastAPI server with various streaming endpoints
- **`client_examples.py`** - Python client examples showing how to consume streaming APIs
- **`QUICKSTART.md`** - Quick start guide with step-by-step instructions

### Running the Examples

#### Option 1: Using Docker (Recommended) 

**This example has its own lightweight Dockerfile and requirements.txt** to avoid installing the entire project dependencies!

**From the `python/` directory:**

```bash
# Build and start the streaming API service
docker compose up streaming-api

# Or run in background
docker compose up -d streaming-api

# The server will be available at http://localhost:8000
```

**Test the API:**
```bash
# In another terminal
curl http://localhost:8000/health
curl -N http://localhost:8000/stream/stock-ticker
```

**Run client examples:**
```bash
# Option 1: Use the helper script (easiest)
cd 02-performance-caching-scale/04-streaming-chunked-responses/
./run_docker.sh client

# Option 2: Run directly
docker compose exec streaming-api python client_examples.py
```

**Stop the service:**
```bash
docker compose stop streaming-api
```

**Why separate Docker setup?**
-  Lightweight build (only ~50MB vs ~500MB)
-  Fast build time (only installs FastAPI, uvicorn, httpx, aiofiles)
-  No need to install Redis, RQ, or other project dependencies
-  Isolated environment for streaming examples only

#### Option 2: Running Locally

**1. Install dependencies:**
```bash
pip install fastapi uvicorn httpx aiofiles
```

**2. Start the server:**
```bash
python streaming_examples.py
```

The server will start on `http://localhost:8000`. Visit `http://localhost:8000/docs` for interactive API documentation.

**3. In another terminal, run the client examples:**
```bash
python client_examples.py
```

This will show an interactive menu to test different streaming scenarios.

### Streaming Techniques Demonstrated

#### 1. Large File Streaming
- **Endpoint**: `GET /download/large-file`
- **Use case**: Downloading videos, backups, large exports
- **Benefit**: Server doesn't load entire file in memory
- **Test**: `curl http://localhost:8000/download/large-file -o output.bin`

#### 2. Server-Sent Events (SSE)
- **Endpoints**: 
  - `GET /stream/stock-ticker` - Real-time stock prices
  - `GET /stream/live-logs` - Live log streaming
- **Use case**: Live dashboards, real-time updates, notifications
- **Format**: `data: {json}\n\n`
- **Test**: `curl -N http://localhost:8000/stream/stock-ticker`

#### 3. Data Export Streaming
- **Endpoints**:
  - `GET /export/users/csv` - Large CSV export
  - `GET /export/data/jsonl` - JSONL format export
  - `GET /stream/database-results` - Database query results
- **Use case**: Exporting large datasets without memory issues
- **Benefit**: Start sending data immediately, process incrementally

#### 4. AI/LLM Response Streaming
- **Endpoints**:
  - `GET /ai/chat-stream?prompt=<text>` - Plain text streaming
  - `GET /ai/chat-stream-sse?prompt=<text>` - SSE with metadata
- **Use case**: ChatGPT-like interfaces, AI assistants
- **Benefit**: Show response as it's generated, better UX

#### 5. Progress Tracking
- **Endpoint**: `GET /process/long-task`
- **Use case**: Long-running tasks (uploads, batch processing)
- **Benefit**: Keep user informed of progress

### Testing with Different Clients

**Browser (for SSE):**
```javascript
// Open browser console at http://localhost:8000
const evtSource = new EventSource('/stream/stock-ticker');
evtSource.onmessage = (event) => {
    const data = JSON.parse(event.data);
    console.log(data);
};
```

**curl (with streaming):**
```bash
# SSE streaming (-N disables buffering)
curl -N http://localhost:8000/stream/stock-ticker

# Download file
curl http://localhost:8000/download/large-file -o output.bin

# AI streaming
curl "http://localhost:8000/ai/chat-stream?prompt=Hello"
```

**Python with requests:**
```python
import requests

# Stream large file
with requests.get('http://localhost:8000/download/large-file', stream=True) as r:
    with open('output.bin', 'wb') as f:
        for chunk in r.iter_content(chunk_size=8192):
            f.write(chunk)

# Stream SSE events
with requests.get('http://localhost:8000/stream/stock-ticker', stream=True) as r:
    for line in r.iter_lines():
        if line.startswith(b'data: '):
            print(line[6:])
```

**Python with httpx (async):**
```python
import httpx
import asyncio

async def stream_ai_response():
    async with httpx.AsyncClient() as client:
        async with client.stream('GET', 'http://localhost:8000/ai/chat-stream?prompt=Python') as response:
            async for chunk in response.aiter_text():
                print(chunk, end='', flush=True)

asyncio.run(stream_ai_response())
```

### Key Implementation Details

**FastAPI Streaming with `StreamingResponse`:**
```python
from fastapi.responses import StreamingResponse

async def generate_data():
    for i in range(1000):
        yield f"chunk {i}\n"
        await asyncio.sleep(0.1)

@app.get("/stream")
async def stream_endpoint():
    return StreamingResponse(generate_data(), media_type="text/plain")
```

**Server-Sent Events Format:**
```python
async def generate_sse():
    for i in range(10):
        data = {"count": i, "timestamp": datetime.now().isoformat()}
        # SSE format: "data: {json}\n\n"
        yield f"data: {json.dumps(data)}\n\n"
        await asyncio.sleep(1)

@app.get("/sse")
async def sse_endpoint():
    return StreamingResponse(
        generate_sse(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        }
    )
```

### Buffered vs Streamed Comparison

The examples include a comparison endpoint showing the difference:

- **Buffered** (`/demo/comparison/buffered`): Loads all data into memory, then sends
  -  High memory usage
  -  User waits for entire response
  -  Simple to implement

- **Streamed** (`/demo/comparison/streamed`): Generates and sends data on-the-fly
  -  Low, constant memory usage
  -  User receives data immediately
  -  Scales to arbitrary data sizes

**When to use streaming:**
- Data size > 10 MB
- Real-time updates needed
- Memory constraints
- Want to improve perceived performance

**When buffered is okay:**
- Small responses (< 1 MB)
- Need to modify entire response before sending
- Simple CRUD operations
