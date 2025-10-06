#!/usr/bin/env python3
"""
FastAPI Streaming and Chunked Responses Examples

This example demonstrates various streaming techniques in FastAPI:
1. Large file streaming (downloads)
2. Real-time data feeds (Server-Sent Events)
3. Processing large datasets (CSV/JSON streaming)
4. AI/LLM token streaming (simulated)

Key Learning Points:
- StreamingResponse for efficient data transfer
- Generator functions for memory-efficient processing
- Server-Sent Events (SSE) for real-time updates
- Chunked transfer encoding happens automatically
- Avoids loading entire response in memory

Prerequisites:
- Install: pip install fastapi uvicorn aiofiles
- Run: uvicorn streaming_examples:app --reload
"""

from fastapi import FastAPI, Response
from fastapi.responses import StreamingResponse
import asyncio
import time
import json
import csv
import io
from typing import AsyncGenerator, Generator
from datetime import datetime
import random

app = FastAPI(title="Streaming Examples API")


# ============================================================================
# 1. LARGE FILE STREAMING
# ============================================================================

@app.get("/download/large-file")
async def download_large_file():
    """
    Stream a large file without loading it entirely into memory.
    Use case: Video downloads, database backups, large CSV exports.
    
    In production, replace with actual file reading:
    async with aiofiles.open('large_file.mp4', 'rb') as f:
        while chunk := await f.read(8192):
            yield chunk
    """
    
    async def generate_large_file() -> AsyncGenerator[bytes, None]:
        """Simulate a large file by generating chunks."""
        total_size = 10 * 1024 * 1024  # 10 MB
        chunk_size = 8192  # 8 KB chunks
        bytes_sent = 0
        
        print(f"[FILE STREAM] Starting file transfer: {total_size} bytes")
        
        while bytes_sent < total_size:
            # Simulate reading from disk
            await asyncio.sleep(0.01)  # Simulate I/O delay
            
            chunk = b"X" * min(chunk_size, total_size - bytes_sent)
            bytes_sent += len(chunk)
            
            print(f"[FILE STREAM] Sent {bytes_sent}/{total_size} bytes", end="\r")
            yield chunk
        
        print(f"\n[FILE STREAM] Transfer complete!")
    
    return StreamingResponse(
        generate_large_file(),
        media_type="application/octet-stream",
        headers={
            "Content-Disposition": "attachment; filename=large_file.bin",
            "X-Content-Type-Options": "nosniff"
        }
    )


@app.get("/download/image/{image_id}")
async def stream_image(image_id: int):
    """
    Stream an image file.
    Demonstrates streaming binary content with proper media type.
    """
    
    async def generate_image_data() -> AsyncGenerator[bytes, None]:
        """
        In production, this would read actual image file:
        async with aiofiles.open(f'images/{image_id}.jpg', 'rb') as f:
            while chunk := await f.read(65536):
                yield chunk
        """
        # Simulate image data
        chunk_size = 65536  # 64 KB
        total_chunks = 50  # ~3 MB image
        
        for i in range(total_chunks):
            await asyncio.sleep(0.01)
            yield b"\xFF\xD8\xFF" + b"0" * (chunk_size - 3)  # Fake JPEG data
    
    return StreamingResponse(
        generate_image_data(),
        media_type="image/jpeg",
        headers={"Cache-Control": "max-age=3600"}
    )


# ============================================================================
# 2. REAL-TIME DATA FEEDS (Server-Sent Events)
# ============================================================================

@app.get("/stream/stock-ticker")
async def stock_ticker():
    """
    Real-time stock price updates using Server-Sent Events (SSE).
    Use case: Live dashboards, stock tickers, sports scores.
    
    SSE Format:
    data: {json}\n\n
    
    Client example (JavaScript):
    const evtSource = new EventSource('/stream/stock-ticker');
    evtSource.onmessage = (event) => {
        const data = JSON.parse(event.data);
        console.log(data);
    };
    """
    
    async def generate_stock_updates() -> AsyncGenerator[str, None]:
        """Generate real-time stock price updates."""
        stocks = ["AAPL", "GOOGL", "MSFT", "AMZN", "TSLA"]
        prices = {stock: 100.0 for stock in stocks}
        
        print("[SSE] Client connected to stock ticker")
        
        try:
            for i in range(50):  # Send 50 updates
                # Simulate price changes
                stock = random.choice(stocks)
                change = random.uniform(-2, 2)
                prices[stock] += change
                
                update = {
                    "timestamp": datetime.now().isoformat(),
                    "stock": stock,
                    "price": round(prices[stock], 2),
                    "change": round(change, 2),
                    "update_number": i + 1
                }
                
                # SSE format: "data: {json}\n\n"
                yield f"data: {json.dumps(update)}\n\n"
                
                await asyncio.sleep(0.5)  # Update every 500ms
            
            print("[SSE] Stock ticker stream ended")
        
        except asyncio.CancelledError:
            print("[SSE] Client disconnected from stock ticker")
            raise
    
    return StreamingResponse(
        generate_stock_updates(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"  # Disable proxy buffering
        }
    )


@app.get("/stream/live-logs")
async def live_logs():
    """
    Stream live log updates using SSE.
    Use case: Real-time monitoring dashboards, deployment logs.
    """
    
    async def generate_logs() -> AsyncGenerator[str, None]:
        """Generate simulated log entries."""
        log_levels = ["INFO", "WARNING", "ERROR", "DEBUG"]
        services = ["api-server", "worker", "database", "cache"]
        
        print("[LOGS] Client connected to live logs")
        
        try:
            for i in range(30):
                log_entry = {
                    "timestamp": datetime.now().isoformat(),
                    "level": random.choice(log_levels),
                    "service": random.choice(services),
                    "message": f"Log message #{i+1}",
                    "request_id": f"req-{random.randint(1000, 9999)}"
                }
                
                yield f"data: {json.dumps(log_entry)}\n\n"
                await asyncio.sleep(random.uniform(0.2, 0.8))
            
            print("[LOGS] Log stream ended")
        
        except asyncio.CancelledError:
            print("[LOGS] Client disconnected from logs")
            raise
    
    return StreamingResponse(
        generate_logs(),
        media_type="text/event-stream"
    )


# ============================================================================
# 3. PROCESSING LARGE DATASETS
# ============================================================================

@app.get("/export/users/csv")
async def export_users_csv():
    """
    Stream large CSV export without loading all data into memory.
    Use case: Exporting large database tables, reports.
    """
    
    async def generate_csv() -> AsyncGenerator[str, None]:
        """Generate CSV data row by row."""
        print("[CSV] Starting CSV export")
        
        # CSV header
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(["id", "username", "email", "created_at", "status"])
        yield output.getvalue()
        
        # Simulate fetching and streaming database records
        total_records = 10000
        batch_size = 100
        
        for batch_start in range(0, total_records, batch_size):
            # Simulate database query delay
            await asyncio.sleep(0.05)
            
            output = io.StringIO()
            writer = csv.writer(output)
            
            for i in range(batch_start, min(batch_start + batch_size, total_records)):
                writer.writerow([
                    i + 1,
                    f"user_{i+1}",
                    f"user{i+1}@example.com",
                    datetime.now().isoformat(),
                    random.choice(["active", "inactive"])
                ])
            
            print(f"[CSV] Exported {min(batch_start + batch_size, total_records)}/{total_records} records", end="\r")
            yield output.getvalue()
        
        print(f"\n[CSV] Export complete: {total_records} records")
    
    return StreamingResponse(
        generate_csv(),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=users_export.csv"}
    )


@app.get("/export/data/jsonl")
async def export_data_jsonl():
    """
    Stream JSONL (JSON Lines) format - one JSON object per line.
    Use case: Large dataset exports, data processing pipelines.
    Better than streaming a single large JSON array.
    """
    
    async def generate_jsonl() -> AsyncGenerator[str, None]:
        """Generate JSONL data."""
        print("[JSONL] Starting JSONL export")
        
        total_records = 5000
        
        for i in range(total_records):
            record = {
                "id": i + 1,
                "timestamp": datetime.now().isoformat(),
                "value": random.uniform(0, 100),
                "category": random.choice(["A", "B", "C"]),
                "metadata": {
                    "processed": True,
                    "version": "1.0"
                }
            }
            
            # Each record is a single line of JSON
            yield json.dumps(record) + "\n"
            
            if (i + 1) % 500 == 0:
                print(f"[JSONL] Exported {i+1}/{total_records} records")
                await asyncio.sleep(0.01)
        
        print(f"[JSONL] Export complete: {total_records} records")
    
    return StreamingResponse(
        generate_jsonl(),
        media_type="application/x-ndjson",  # or "application/jsonl"
        headers={"Content-Disposition": "attachment; filename=data_export.jsonl"}
    )


@app.get("/stream/database-results")
async def stream_database_results():
    """
    Stream database query results as JSON array.
    Use case: Large query results that don't fit in memory.
    """
    
    async def generate_results() -> AsyncGenerator[str, None]:
        """
        Simulate streaming database results.
        In production, use cursor-based iteration over query results.
        """
        print("[DB STREAM] Starting database query")
        
        # Start JSON array
        yield "["
        
        total_results = 1000
        
        for i in range(total_results):
            # Simulate fetching from database
            if i % 100 == 0:
                await asyncio.sleep(0.05)  # Simulate query batch
            
            result = {
                "id": i + 1,
                "data": f"Record {i+1}",
                "value": random.randint(1, 1000)
            }
            
            # Add comma separator between items (but not after last item)
            if i > 0:
                yield ","
            
            yield json.dumps(result)
        
        # Close JSON array
        yield "]"
        
        print(f"[DB STREAM] Query complete: {total_results} results")
    
    return StreamingResponse(
        generate_results(),
        media_type="application/json"
    )


# ============================================================================
# 4. AI/LLM TOKEN STREAMING
# ============================================================================

@app.get("/ai/chat-stream")
async def chat_stream(prompt: str = "Tell me about Python"):
    """
    Stream AI/LLM responses token by token.
    Use case: ChatGPT-like interfaces, AI assistants.
    Provides immediate feedback instead of waiting for full response.
    
    Client example:
    fetch('/ai/chat-stream?prompt=hello')
      .then(response => response.body)
      .then(body => {
        const reader = body.getReader();
        const decoder = new TextDecoder();
        // Read stream chunk by chunk
      });
    """
    
    async def generate_ai_response() -> AsyncGenerator[str, None]:
        """
        Simulate streaming LLM token generation.
        In production, integrate with OpenAI API streaming:
        
        async for chunk in await openai.ChatCompletion.acreate(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            stream=True
        ):
            if content := chunk.choices[0].delta.content:
                yield content
        """
        
        # Simulated AI response
        response = f"""Here's my response to your prompt: "{prompt}"

Python is a high-level, interpreted programming language known for its simplicity and readability. 
It was created by Guido van Rossum and first released in 1991. Python supports multiple programming 
paradigms including procedural, object-oriented, and functional programming. It has become one of 
the most popular languages for web development, data science, machine learning, and automation."""
        
        print(f"[AI] Streaming response for prompt: '{prompt}'")
        
        # Stream token by token (word by word in this simulation)
        words = response.split()
        for i, word in enumerate(words):
            # Add space before words (except first)
            token = word if i == 0 else " " + word
            
            yield token
            
            # Simulate token generation delay (LLMs don't produce tokens instantly)
            await asyncio.sleep(random.uniform(0.02, 0.08))
        
        print(f"[AI] Response streaming complete")
    
    return StreamingResponse(
        generate_ai_response(),
        media_type="text/plain"
    )


@app.get("/ai/chat-stream-sse")
async def chat_stream_sse(prompt: str = "What is FastAPI?"):
    """
    Stream AI responses using SSE with structured events.
    Use case: More structured AI streaming with metadata.
    """
    
    async def generate_ai_events() -> AsyncGenerator[str, None]:
        """Generate AI response as SSE events with metadata."""
        
        # Send initial metadata
        yield f"data: {json.dumps({'type': 'start', 'prompt': prompt})}\n\n"
        
        # Simulated response tokens
        response_tokens = [
            "FastAPI", " is", " a", " modern", ",", " fast", " web", " framework",
            " for", " building", " APIs", " with", " Python", ".", " It", " uses",
            " type", " hints", " and", " async", " support", "."
        ]
        
        token_count = 0
        for token in response_tokens:
            token_count += 1
            
            # Send token event
            event = {
                "type": "token",
                "content": token,
                "token_number": token_count
            }
            yield f"data: {json.dumps(event)}\n\n"
            
            await asyncio.sleep(0.05)
        
        # Send completion event
        completion_event = {
            "type": "complete",
            "total_tokens": token_count,
            "finish_reason": "stop"
        }
        yield f"data: {json.dumps(completion_event)}\n\n"
        
        print(f"[AI SSE] Streamed {token_count} tokens")
    
    return StreamingResponse(
        generate_ai_events(),
        media_type="text/event-stream"
    )


# ============================================================================
# 5. PROGRESS UPDATES FOR LONG-RUNNING TASKS
# ============================================================================

@app.get("/process/long-task")
async def long_running_task():
    """
    Stream progress updates for long-running background tasks.
    Use case: File uploads, batch processing, report generation.
    """
    
    async def generate_progress_updates() -> AsyncGenerator[str, None]:
        """Generate progress updates."""
        
        steps = [
            "Initializing...",
            "Loading data...",
            "Processing records...",
            "Applying transformations...",
            "Validating results...",
            "Saving output...",
            "Cleanup...",
            "Complete!"
        ]
        
        for i, step in enumerate(steps):
            progress = {
                "step": i + 1,
                "total_steps": len(steps),
                "message": step,
                "progress_percent": int((i + 1) / len(steps) * 100),
                "timestamp": datetime.now().isoformat()
            }
            
            yield f"data: {json.dumps(progress)}\n\n"
            
            # Simulate work
            await asyncio.sleep(1)
        
        print("[PROGRESS] Task completed")
    
    return StreamingResponse(
        generate_progress_updates(),
        media_type="text/event-stream"
    )


# ============================================================================
# UTILITY ENDPOINTS
# ============================================================================

@app.get("/")
async def root():
    """API documentation."""
    return {
        "message": "FastAPI Streaming Examples",
        "endpoints": {
            "file_streaming": [
                "GET /download/large-file - Stream large file",
                "GET /download/image/{image_id} - Stream image"
            ],
            "real_time_feeds": [
                "GET /stream/stock-ticker - Real-time stock updates (SSE)",
                "GET /stream/live-logs - Live log streaming (SSE)"
            ],
            "data_export": [
                "GET /export/users/csv - Export CSV",
                "GET /export/data/jsonl - Export JSONL",
                "GET /stream/database-results - Stream DB results"
            ],
            "ai_streaming": [
                "GET /ai/chat-stream?prompt=<text> - Stream AI response",
                "GET /ai/chat-stream-sse?prompt=<text> - Stream AI with SSE"
            ],
            "progress_tracking": [
                "GET /process/long-task - Long task with progress"
            ]
        },
        "tips": {
            "testing_sse": "Use browser or: curl -N http://localhost:8000/stream/stock-ticker",
            "testing_download": "curl http://localhost:8000/download/large-file -o output.bin",
            "client_libraries": [
                "JavaScript: EventSource API for SSE",
                "Python: requests with stream=True, httpx with async",
                "curl: Use -N flag to disable buffering"
            ]
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat()
    }


# ============================================================================
# PERFORMANCE COMPARISON
# ============================================================================

@app.get("/demo/comparison/buffered")
async def buffered_response():
    """
    NON-STREAMING: Load everything into memory first (BAD for large data).
    This is what happens when you DON'T use streaming.
    """
    print("[BUFFERED] Loading all data into memory...")
    
    # Build entire response in memory
    data = []
    for i in range(1000):
        data.append({
            "id": i + 1,
            "data": f"Record {i+1}",
            "timestamp": datetime.now().isoformat()
        })
    
    print(f"[BUFFERED] Loaded {len(data)} records in memory")
    
    # Return everything at once
    return {"records": data}


@app.get("/demo/comparison/streamed")
async def streamed_response():
    """
    STREAMING: Generate data on-the-fly (GOOD for large data).
    Memory efficient and starts sending immediately.
    """
    
    async def generate_data() -> AsyncGenerator[str, None]:
        print("[STREAMED] Starting to generate data...")
        
        yield '{"records":['
        
        for i in range(1000):
            if i > 0:
                yield ","
            
            record = {
                "id": i + 1,
                "data": f"Record {i+1}",
                "timestamp": datetime.now().isoformat()
            }
            
            yield json.dumps(record)
            
            if i % 100 == 0:
                print(f"[STREAMED] Generated {i} records (memory efficient)")
        
        yield ']}'
        print("[STREAMED] Complete - low memory usage throughout")
    
    return StreamingResponse(
        generate_data(),
        media_type="application/json"
    )


if __name__ == "__main__":
    import uvicorn
    
    print("""

            FastAPI Streaming Examples Server                         


Starting server...

Test endpoints:
  • http://localhost:8000/docs - Interactive API docs
  • http://localhost:8000/stream/stock-ticker - Real-time stock updates
  • http://localhost:8000/ai/chat-stream?prompt=hello - AI streaming
  • http://localhost:8000/export/users/csv - CSV export

Testing with curl:
  curl -N http://localhost:8000/stream/stock-ticker
  curl http://localhost:8000/download/large-file -o test.bin
  curl http://localhost:8000/ai/chat-stream?prompt=Python

Testing SSE with JavaScript (browser console):
  const evtSource = new EventSource('/stream/stock-ticker');
  evtSource.onmessage = (e) => console.log(JSON.parse(e.data));
    """)
    
    uvicorn.run(app, host="0.0.0.0", port=8000)

