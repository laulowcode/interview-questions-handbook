# Streaming/Chunked Responses - Quick Start Guide

Get up and running with FastAPI streaming examples in 5 minutes!

##  Quick Setup (Docker - Recommended)

### Option A: Using Docker (Easiest)

**This example has its own lightweight Dockerfile and requirements.txt** - no need to install the entire project dependencies!

**1. Start the FastAPI streaming server:**

```bash
# From the python/ directory
cd python/

# Build and start the streaming API service (first time may take a minute)
docker compose up streaming-api

# Or run in background:
docker compose up -d streaming-api
```

The server will start on `http://localhost:8000`

**2. Test the API:**

Open a new terminal and test with curl:
```bash
# Test health endpoint
curl http://localhost:8000/health

# Watch real-time stock ticker
curl -N http://localhost:8000/stream/stock-ticker

# Try AI streaming
curl "http://localhost:8000/ai/chat-stream?prompt=Hello"
```

Or visit in browser:
- **Interactive Docs**: http://localhost:8000/docs
- **Stock Ticker**: http://localhost:8000/stream/stock-ticker

**3. Run client examples:**

```bash
# From the streaming examples directory
cd 02-performance-caching-scale/04-streaming-chunked-responses/

# Use the helper script (easiest)
./run_docker.sh client

# Or run directly with Docker
docker compose exec streaming-api python client_examples.py
```

**4. Stop the server:**

```bash
# Stop streaming service
docker compose stop streaming-api

# Or stop everything
docker compose down
```

**Quick Helper Script:**

Use the included helper script for common tasks:

```bash
cd 02-performance-caching-scale/04-streaming-chunked-responses/

./run_docker.sh start      # Start server
./run_docker.sh test       # Run quick tests
./run_docker.sh client     # Run client examples
./run_docker.sh logs       # View logs
./run_docker.sh stop       # Stop server
./run_docker.sh help       # Show all commands
```

---

##  Alternative: Local Setup (Without Docker)

### Option B: Running Locally

**1. Install Dependencies:**

```bash
cd python/
pip install -r requirements.txt
```

Or install just what's needed:
```bash
pip install fastapi uvicorn httpx aiofiles
```

**2. Start the Server:**

```bash
cd 02-performance-caching-scale/04-streaming-chunked-responses/
python streaming_examples.py
```

You should see:
```

            FastAPI Streaming Examples Server                         


Starting server...

Test endpoints:
  • http://localhost:8000/docs - Interactive API docs
  • http://localhost:8000/stream/stock-ticker - Real-time stock updates
  ...
```

**3. Test the Examples:**

Open a new terminal and run:

```bash
python client_examples.py
```

Select an example from the menu or press Enter to run all examples.

---

##  Quick Tests

### Test 1: Real-time Stock Ticker (SSE)

**Terminal 1** - Server is running

**Terminal 2** - Test with curl:
```bash
curl -N http://localhost:8000/stream/stock-ticker
```

You'll see live stock updates streaming in real-time!

### Test 2: AI Chat Streaming

**Browser** - Visit:
```
http://localhost:8000/ai/chat-stream?prompt=Tell%20me%20about%20Python
```

Watch the response appear word-by-word, like ChatGPT!

### Test 3: Interactive API Docs

**Browser** - Visit:
```
http://localhost:8000/docs
```

Try any endpoint directly from the interactive Swagger UI.

##  What's Included

### Server (`streaming_examples.py`)

13 different streaming endpoints covering:

1. **Large File Streaming** - Download files without memory issues
   - `GET /download/large-file`
   - `GET /download/image/{image_id}`

2. **Real-time Data Feeds** - Server-Sent Events (SSE)
   - `GET /stream/stock-ticker` - Live stock prices
   - `GET /stream/live-logs` - Real-time logs

3. **Data Export Streaming** - Export large datasets
   - `GET /export/users/csv` - CSV export
   - `GET /export/data/jsonl` - JSONL format
   - `GET /stream/database-results` - JSON array streaming

4. **AI/LLM Streaming** - Token-by-token responses
   - `GET /ai/chat-stream?prompt=<text>` - Plain text streaming
   - `GET /ai/chat-stream-sse?prompt=<text>` - SSE with metadata

5. **Progress Tracking** - Monitor long-running tasks
   - `GET /process/long-task` - Progress updates via SSE

6. **Performance Comparison** - See the difference!
   - `GET /demo/comparison/buffered` - Traditional response
   - `GET /demo/comparison/streamed` - Streaming response

### Client (`client_examples.py`)

9 client examples showing how to consume streaming APIs:
- Download large files efficiently
- Consume SSE streams
- Process CSV/JSONL exports
- Stream AI responses
- Track progress

##  Testing Different Ways

### Browser JavaScript (for SSE)

Open browser console at `http://localhost:8000` and run:

```javascript
// Stock ticker
const evtSource = new EventSource('/stream/stock-ticker');
evtSource.onmessage = (event) => {
    const data = JSON.parse(event.data);
    console.log(`${data.stock}: $${data.price} (${data.change > 0 ? '+' : ''}${data.change})`);
};

// Stop receiving
// evtSource.close();
```

### curl Commands

```bash
# Stream real-time stock data
curl -N http://localhost:8000/stream/stock-ticker

# Download a large file
curl http://localhost:8000/download/large-file -o test.bin

# AI chat streaming
curl "http://localhost:8000/ai/chat-stream?prompt=Hello"

# Export CSV
curl http://localhost:8000/export/users/csv -o users.csv

# Watch long task progress
curl -N http://localhost:8000/process/long-task
```

### Python Scripts

**Download File with Streaming:**
```python
import httpx
import asyncio

async def download_file():
    async with httpx.AsyncClient() as client:
        async with client.stream("GET", "http://localhost:8000/download/large-file") as response:
            with open("output.bin", "wb") as f:
                async for chunk in response.aiter_bytes(chunk_size=8192):
                    f.write(chunk)
                    print(f"Downloaded {f.tell()} bytes...")

asyncio.run(download_file())
```

**Consume SSE Stream:**
```python
import httpx
import asyncio
import json

async def watch_stocks():
    async with httpx.AsyncClient(timeout=None) as client:
        async with client.stream("GET", "http://localhost:8000/stream/stock-ticker") as response:
            async for line in response.aiter_lines():
                if line.startswith("data: "):
                    data = json.loads(line[6:])
                    print(f"{data['stock']}: ${data['price']}")

asyncio.run(watch_stocks())
```

**Stream AI Response:**
```python
import httpx
import asyncio

async def chat():
    async with httpx.AsyncClient() as client:
        async with client.stream("GET", "http://localhost:8000/ai/chat-stream?prompt=Python") as response:
            async for chunk in response.aiter_text():
                print(chunk, end="", flush=True)
    print()

asyncio.run(chat())
```

##  Key Concepts

### What is Streaming?

Instead of:
1. Server generates entire response
2. Loads it all in memory
3. Sends everything at once
4. Client waits for complete response

Streaming does:
1. Server generates data incrementally
2. Sends chunks as soon as ready
3. Client receives and processes immediately
4. Low memory usage, instant feedback

### When to Use Streaming?

 **Use streaming when:**
- Response size > 10 MB
- Want immediate feedback (UX)
- Memory is limited
- Real-time updates needed
- Processing takes time

 **Don't use streaming when:**
- Response < 1 MB
- Need to modify entire response
- Simple CRUD operations
- Caching the full response

### Server-Sent Events (SSE)

SSE is perfect for:
- Real-time dashboards
- Live notifications
- Progress updates
- Chat applications
- Monitoring systems

**Format:**
```
data: {"message": "Hello"}\n\n
```

**Headers:**
```python
{
    "Content-Type": "text/event-stream",
    "Cache-Control": "no-cache",
    "Connection": "keep-alive",
}
```

##  Troubleshooting

**Port already in use:**
```bash
# Change port in streaming_examples.py
uvicorn.run(app, host="0.0.0.0", port=8001)  # Use 8001 instead
```

**Dependencies missing:**
```bash
pip install fastapi uvicorn httpx aiofiles
```

**Client can't connect:**
- Make sure server is running first
- Check firewall settings
- Verify port 8000 is accessible

**SSE not working in browser:**
- Check browser console for errors
- Ensure CORS is configured if needed
- Try curl to verify server is working

**Streaming seems buffered:**
- Use `-N` flag with curl
- Check for proxy buffering (nginx, apache)
- Disable browser buffering in dev tools

##  Next Steps

1. **Explore the Code**
   - Read `streaming_examples.py` to understand implementation
   - Check `client_examples.py` for consumption patterns

2. **Modify Examples**
   - Change chunk sizes
   - Add authentication
   - Integrate with real databases

3. **Build Something Real**
   - File upload with progress
   - Live dashboard
   - CSV export from database
   - Chat interface with AI

4. **Read Full README**
   - See `README.md` for detailed explanations
   - Learn about different streaming techniques
   - Understand trade-offs

##  Interview Tips

**Common Questions:**

**Q: When would you use streaming responses?**
> A: For large files, real-time data, long-running processes, or when you want to show progress immediately. Examples: video downloads, live dashboards, AI chat, large exports.

**Q: What's the difference between SSE and WebSockets?**
> A: SSE is uni-directional (server → client), simpler, HTTP-based. WebSockets are bi-directional, more complex, but allow client → server push too. Use SSE for notifications/updates, WebSocket for chat.

**Q: How does streaming reduce memory usage?**
> A: Instead of loading the entire response (e.g., 1 GB file) into memory, streaming processes and sends small chunks (e.g., 8 KB). Server only holds current chunk in memory.

**Q: What are the downsides of streaming?**
> A: Can't modify response after streaming starts, harder to cache, requires special client handling, and you can't set Content-Length header upfront.

**Q: How do you handle errors mid-stream?**
> A: Use try-except in generator, send error as SSE event, or use chunked encoding with error markers. Client should handle partial responses gracefully.

##  Success!

You now have a complete understanding of streaming in FastAPI! You've learned:

-  How to implement streaming responses
-  Different streaming techniques (files, SSE, data export)
-  How to consume streams from clients
-  When to use streaming vs buffered responses
-  Real-world patterns for production use

Ready to ace your Python backend interview! 

