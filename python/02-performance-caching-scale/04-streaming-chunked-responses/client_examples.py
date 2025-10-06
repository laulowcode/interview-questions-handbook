#!/usr/bin/env python3
"""
Streaming API Client Examples

Demonstrates how to consume streaming endpoints from Python clients.
Shows various approaches for different use cases.

Prerequisites:
- Install: pip install httpx aiofiles
- Start the server first: python streaming_examples.py
"""

import httpx
import asyncio
import json
from typing import AsyncIterator
import time


# ============================================================================
# CLIENT FOR FILE STREAMING
# ============================================================================

async def download_file_streaming():
    """
    Download a large file using streaming to avoid memory issues.
    Files are written chunk-by-chunk instead of loading entirely into memory.
    """
    print("\n" + "=" * 70)
    print("DOWNLOADING LARGE FILE (Streaming)")
    print("=" * 70)
    
    url = "http://localhost:8000/download/large-file"
    output_file = "downloaded_file.bin"
    
    async with httpx.AsyncClient() as client:
        async with client.stream("GET", url) as response:
            response.raise_for_status()
            
            print(f"Status: {response.status_code}")
            print(f"Content-Type: {response.headers.get('content-type')}")
            
            total_bytes = 0
            start_time = time.time()
            
            # Write to file chunk by chunk
            with open(output_file, "wb") as f:
                async for chunk in response.aiter_bytes(chunk_size=8192):
                    f.write(chunk)
                    total_bytes += len(chunk)
                    
                    # Show progress
                    if total_bytes % (1024 * 1024) == 0:  # Every 1 MB
                        elapsed = time.time() - start_time
                        speed = total_bytes / elapsed / 1024 / 1024  # MB/s
                        print(f"  Downloaded: {total_bytes / 1024 / 1024:.2f} MB ({speed:.2f} MB/s)")
            
            elapsed = time.time() - start_time
            print(f"\n Download complete!")
            print(f"  Total: {total_bytes / 1024 / 1024:.2f} MB in {elapsed:.2f}s")
            print(f"  File saved: {output_file}")


# ============================================================================
# CLIENT FOR SERVER-SENT EVENTS (SSE)
# ============================================================================

async def consume_sse_stream(url: str, duration: int = 10):
    """
    Consume Server-Sent Events (SSE) stream.
    Use case: Real-time dashboards, live updates, notifications.
    """
    print(f"\n{'=' * 70}")
    print(f"CONSUMING SSE STREAM: {url}")
    print("=" * 70)
    
    async with httpx.AsyncClient(timeout=None) as client:
        async with client.stream("GET", url) as response:
            print(f"Connected! Status: {response.status_code}\n")
            
            start_time = time.time()
            event_count = 0
            
            # Read line by line (SSE format)
            async for line in response.aiter_lines():
                if time.time() - start_time > duration:
                    print(f"\n⏱  Duration limit reached ({duration}s)")
                    break
                
                if line.startswith("data: "):
                    data = line[6:]  # Remove "data: " prefix
                    
                    try:
                        event = json.loads(data)
                        event_count += 1
                        
                        # Pretty print the event
                        timestamp = event.get('timestamp', '')[:19]  # Trim milliseconds
                        print(f"[Event #{event_count}] {timestamp}")
                        for key, value in event.items():
                            if key != 'timestamp':
                                print(f"  {key}: {value}")
                        print()
                    
                    except json.JSONDecodeError:
                        print(f"[Event #{event_count}] {data}")
            
            print(f" Received {event_count} events")


async def stock_ticker_client():
    """Client for real-time stock ticker."""
    await consume_sse_stream(
        "http://localhost:8000/stream/stock-ticker",
        duration=10
    )


async def live_logs_client():
    """Client for live log streaming."""
    await consume_sse_stream(
        "http://localhost:8000/stream/live-logs",
        duration=8
    )


# ============================================================================
# CLIENT FOR DATA EXPORT STREAMING
# ============================================================================

async def download_csv_export():
    """
    Download and process CSV export stream.
    Process rows as they arrive instead of waiting for entire file.
    """
    print("\n" + "=" * 70)
    print("DOWNLOADING CSV EXPORT (Streaming)")
    print("=" * 70)
    
    url = "http://localhost:8000/export/users/csv"
    
    async with httpx.AsyncClient(timeout=60.0) as client:
        async with client.stream("GET", url) as response:
            response.raise_for_status()
            
            row_count = 0
            sample_rows = []
            
            # Process line by line as it arrives
            async for line in response.aiter_lines():
                row_count += 1
                
                # Save first few rows as samples
                if row_count <= 5:
                    sample_rows.append(line)
                
                # Show progress
                if row_count % 1000 == 0:
                    print(f"  Processed {row_count} rows...")
            
            print(f"\n CSV download complete!")
            print(f"  Total rows: {row_count}")
            print(f"\n  Sample rows:")
            for i, row in enumerate(sample_rows[:3], 1):
                print(f"    {i}. {row}")


async def download_jsonl_export():
    """
    Download and process JSONL (JSON Lines) export.
    Each line is a separate JSON object - process incrementally.
    """
    print("\n" + "=" * 70)
    print("DOWNLOADING JSONL EXPORT (Streaming)")
    print("=" * 70)
    
    url = "http://localhost:8000/export/data/jsonl"
    
    async with httpx.AsyncClient(timeout=60.0) as client:
        async with client.stream("GET", url) as response:
            response.raise_for_status()
            
            record_count = 0
            category_counts = {"A": 0, "B": 0, "C": 0}
            
            # Process each JSON line as it arrives
            async for line in response.aiter_lines():
                try:
                    record = json.loads(line)
                    record_count += 1
                    
                    # Process record (e.g., count by category)
                    category = record.get("category")
                    if category in category_counts:
                        category_counts[category] += 1
                    
                    # Show progress
                    if record_count % 500 == 0:
                        print(f"  Processed {record_count} records...")
                
                except json.JSONDecodeError:
                    continue
            
            print(f"\n JSONL download complete!")
            print(f"  Total records: {record_count}")
            print(f"  Category distribution:")
            for category, count in sorted(category_counts.items()):
                print(f"    {category}: {count} ({count/record_count*100:.1f}%)")


# ============================================================================
# CLIENT FOR AI/LLM STREAMING
# ============================================================================

async def ai_chat_streaming():
    """
    Stream AI/LLM responses token by token.
    Shows response as it's being generated (ChatGPT-style).
    """
    print("\n" + "=" * 70)
    print("AI CHAT STREAMING (Token-by-token)")
    print("=" * 70)
    
    prompt = "Tell me about Python"
    url = f"http://localhost:8000/ai/chat-stream?prompt={prompt}"
    
    print(f"Prompt: {prompt}\n")
    print("Response: ", end="", flush=True)
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        async with client.stream("GET", url) as response:
            response.raise_for_status()
            
            # Stream and print each token as it arrives
            async for chunk in response.aiter_text():
                print(chunk, end="", flush=True)
    
    print("\n\n Response complete!")


async def ai_chat_sse():
    """
    Stream AI responses with structured SSE events.
    Includes metadata like token count, completion status.
    """
    print("\n" + "=" * 70)
    print("AI CHAT STREAMING (SSE with metadata)")
    print("=" * 70)
    
    prompt = "What is FastAPI?"
    url = f"http://localhost:8000/ai/chat-stream-sse?prompt={prompt}"
    
    print(f"Prompt: {prompt}\n")
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        async with client.stream("GET", url) as response:
            response.raise_for_status()
            
            full_response = ""
            
            async for line in response.aiter_lines():
                if line.startswith("data: "):
                    data = json.loads(line[6:])
                    event_type = data.get("type")
                    
                    if event_type == "start":
                        print(f" Started generating response...")
                        print(f"Response: ", end="", flush=True)
                    
                    elif event_type == "token":
                        content = data.get("content", "")
                        full_response += content
                        print(content, end="", flush=True)
                    
                    elif event_type == "complete":
                        print(f"\n\n Generation complete!")
                        print(f"  Total tokens: {data.get('total_tokens')}")
                        print(f"  Finish reason: {data.get('finish_reason')}")


# ============================================================================
# CLIENT FOR PROGRESS TRACKING
# ============================================================================

async def track_long_running_task():
    """
    Monitor progress of long-running task.
    Use case: File uploads, batch processing, report generation.
    """
    print("\n" + "=" * 70)
    print("TRACKING LONG-RUNNING TASK")
    print("=" * 70 + "\n")
    
    url = "http://localhost:8000/process/long-task"
    
    async with httpx.AsyncClient(timeout=None) as client:
        async with client.stream("GET", url) as response:
            response.raise_for_status()
            
            async for line in response.aiter_lines():
                if line.startswith("data: "):
                    progress = json.loads(line[6:])
                    
                    step = progress['step']
                    total = progress['total_steps']
                    message = progress['message']
                    percent = progress['progress_percent']
                    
                    # Progress bar
                    bar_length = 30
                    filled = int(bar_length * percent / 100)
                    bar = "" * filled + "" * (bar_length - filled)
                    
                    print(f"[{step}/{total}] {bar} {percent}% - {message}")
            
            print("\n Task completed successfully!")


# ============================================================================
# COMPARISON: BUFFERED vs STREAMED
# ============================================================================

async def compare_buffered_vs_streamed():
    """
    Compare memory and time efficiency of buffered vs streamed responses.
    """
    print("\n" + "=" * 70)
    print("COMPARISON: Buffered vs Streamed Responses")
    print("=" * 70)
    
    async with httpx.AsyncClient(timeout=60.0) as client:
        # Test buffered response
        print("\n[1] Testing BUFFERED response (loads all data in memory)...")
        start = time.time()
        
        response = await client.get("http://localhost:8000/demo/comparison/buffered")
        data = response.json()
        
        buffered_time = time.time() - start
        buffered_size = len(response.content)
        
        print(f"  ⏱  Time: {buffered_time:.3f}s")
        print(f"   Response size: {buffered_size / 1024:.2f} KB")
        print(f"   Records: {len(data['records'])}")
        
        # Test streamed response
        print("\n[2] Testing STREAMED response (processes on-the-fly)...")
        start = time.time()
        
        first_byte_time = None
        chunk_count = 0
        total_size = 0
        
        async with client.stream("GET", "http://localhost:8000/demo/comparison/streamed") as response:
            async for chunk in response.aiter_bytes():
                if first_byte_time is None:
                    first_byte_time = time.time() - start
                
                chunk_count += 1
                total_size += len(chunk)
        
        streamed_time = time.time() - start
        
        print(f"  ⏱  Total time: {streamed_time:.3f}s")
        print(f"   Time to first byte: {first_byte_time:.3f}s (starts immediately!)")
        print(f"   Response size: {total_size / 1024:.2f} KB")
        print(f"   Chunks received: {chunk_count}")
        
        # Comparison
        print("\n COMPARISON RESULTS:")
        print(f"  Time to first byte:")
        print(f"    Buffered: Must wait {buffered_time:.3f}s for complete response")
        print(f"    Streamed: Only {first_byte_time:.3f}s to start receiving data")
        print(f"  Memory efficiency:")
        print(f"    Buffered: Requires {buffered_size / 1024:.2f} KB in memory")
        print(f"    Streamed: Only needs memory for current chunk (~few KB)")
        print(f"\n   Winner: Streaming (better UX and memory efficiency!)")


# ============================================================================
# MAIN MENU
# ============================================================================

async def main():
    """Main menu to run different examples."""
    
    examples = {
        "1": ("Download large file", download_file_streaming),
        "2": ("Stock ticker (SSE)", stock_ticker_client),
        "3": ("Live logs (SSE)", live_logs_client),
        "4": ("CSV export", download_csv_export),
        "5": ("JSONL export", download_jsonl_export),
        "6": ("AI chat streaming", ai_chat_streaming),
        "7": ("AI chat SSE", ai_chat_sse),
        "8": ("Track long task", track_long_running_task),
        "9": ("Compare buffered vs streamed", compare_buffered_vs_streamed),
        "all": ("Run all examples", None),
    }
    
    print("""

              Streaming API Client Examples                           


Prerequisites:
  1. Start the server: python streaming_examples.py
  2. Ensure it's running on http://localhost:8000

Choose an example to run:
""")
    
    for key, (desc, _) in examples.items():
        print(f"  {key}. {desc}")
    
    print("\n  0. Exit")
    
    choice = input("\nEnter your choice (or press Enter for all): ").strip()
    
    if not choice or choice == "all":
        print("\n Running all examples...\n")
        for key, (_, func) in examples.items():
            if func and key != "all":
                try:
                    await func()
                    await asyncio.sleep(1)  # Brief pause between examples
                except Exception as e:
                    print(f"\n Error in example: {e}")
                    print("Make sure the server is running!\n")
    
    elif choice == "0":
        print("Goodbye!")
        return
    
    elif choice in examples and examples[choice][1]:
        try:
            await examples[choice][1]()
        except Exception as e:
            print(f"\n Error: {e}")
            print("Make sure the server is running!")
    
    else:
        print("Invalid choice!")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n  Interrupted by user")
    except Exception as e:
        print(f"\n Error: {e}")
        print("\nMake sure:")
        print("  1. The server is running: python streaming_examples.py")
        print("  2. Dependencies are installed: pip install httpx aiofiles")

