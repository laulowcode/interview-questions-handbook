"""
Example demonstrating how GIL doesn't affect I/O-bound tasks.

This example shows how threading is effective for I/O operations because
the GIL is released during I/O operations, allowing true concurrency.
"""

import threading
import time
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
import asyncio
import aiohttp


def simulate_io_operation(duration):
    """Simulate an I/O operation (like database query, API call)."""
    time.sleep(duration)  # Simulate waiting for I/O
    return f"Completed I/O operation after {duration}s"


def run_sequential_io(n_tasks, io_duration):
    """Run I/O tasks sequentially."""
    start_time = time.time()
    results = []
    
    for i in range(n_tasks):
        result = simulate_io_operation(io_duration)
        results.append(result)
    
    end_time = time.time()
    return end_time - start_time, results


def run_with_threads_io(n_tasks, io_duration):
    """Run I/O tasks using threads (GIL released during I/O)."""
    start_time = time.time()
    results = []
    threads = []
    
    def worker():
        result = simulate_io_operation(io_duration)
        results.append(result)
    
    # Create and start threads
    for _ in range(n_tasks):
        thread = threading.Thread(target=worker)
        threads.append(thread)
        thread.start()
    
    # Wait for all threads to complete
    for thread in threads:
        thread.join()
    
    end_time = time.time()
    return end_time - start_time, results


def run_with_thread_pool_io(n_tasks, io_duration):
    """Run I/O tasks using ThreadPoolExecutor."""
    start_time = time.time()
    
    with ThreadPoolExecutor(max_workers=n_tasks) as executor:
        futures = [executor.submit(simulate_io_operation, io_duration) for _ in range(n_tasks)]
        results = [future.result() for future in futures]
    
    end_time = time.time()
    return end_time - start_time, results


def fetch_url(url):
    """Fetch a URL (real I/O operation)."""
    try:
        response = requests.get(url, timeout=5)
        return f"Status: {response.status_code}, URL: {url}"
    except requests.RequestException as e:
        return f"Error: {e}, URL: {url}"


def run_real_io_example():
    """Example with real HTTP requests."""
    urls = [
        "https://httpbin.org/delay/1",
        "https://httpbin.org/delay/1", 
        "https://httpbin.org/delay/1",
        "https://httpbin.org/delay/1"
    ]
    
    print("Real I/O Example (HTTP requests):")
    print("-" * 40)
    
    # Sequential
    start_time = time.time()
    sequential_results = []
    for url in urls:
        result = fetch_url(url)
        sequential_results.append(result)
    seq_time = time.time() - start_time
    print(f"Sequential: {seq_time:.2f}s")
    
    # Threaded
    start_time = time.time()
    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = [executor.submit(fetch_url, url) for url in urls]
        threaded_results = [future.result() for future in futures]
    thread_time = time.time() - start_time
    print(f"Threaded: {thread_time:.2f}s")
    print(f"Speedup: {seq_time/thread_time:.2f}x")
    print()


async def async_io_operation(duration):
    """Async version of I/O operation."""
    await asyncio.sleep(duration)
    return f"Completed async I/O operation after {duration}s"


async def run_async_io(n_tasks, io_duration):
    """Run I/O tasks using asyncio."""
    start_time = time.time()
    
    tasks = [async_io_operation(io_duration) for _ in range(n_tasks)]
    results = await asyncio.gather(*tasks)
    
    end_time = time.time()
    return end_time - start_time, results


def main():
    """Compare different approaches for I/O-bound tasks."""
    n_tasks = 4
    io_duration = 1  # seconds
    
    print("=" * 60)
    print("I/O-BOUND TASK COMPARISON (GIL doesn't limit)")
    print("=" * 60)
    print(f"Tasks: {n_tasks}, I/O duration: {io_duration}s each")
    print()
    
    # Sequential execution
    print("1. Sequential execution (baseline):")
    seq_time, _ = run_sequential_io(n_tasks, io_duration)
    print(f"   Time: {seq_time:.4f} seconds")
    print()
    
    # Threading (effective for I/O)
    print("2. Threading (GIL released during I/O):")
    thread_time, _ = run_with_threads_io(n_tasks, io_duration)
    print(f"   Time: {thread_time:.4f} seconds")
    print(f"   Speedup: {seq_time/thread_time:.2f}x")
    print()
    
    # ThreadPoolExecutor
    print("3. ThreadPoolExecutor (also effective for I/O):")
    pool_time, _ = run_with_thread_pool_io(n_tasks, io_duration)
    print(f"   Time: {pool_time:.4f} seconds")
    print(f"   Speedup: {seq_time/pool_time:.2f}x")
    print()
    
    # Asyncio
    print("4. Asyncio (single-threaded async):")
    async_time, _ = asyncio.run(run_async_io(n_tasks, io_duration))
    print(f"   Time: {async_time:.4f} seconds")
    print(f"   Speedup: {seq_time/async_time:.2f}x")
    print()
    
    # Real I/O example
    run_real_io_example()
    
    print("=" * 60)
    print("CONCLUSION:")
    print("- Threading is effective for I/O-bound tasks (GIL released during I/O)")
    print("- Asyncio provides similar benefits with lower overhead")
    print("- Both approaches can handle many concurrent I/O operations")
    print("- This is why web servers and APIs work well with Python threading")
    print("=" * 60)


if __name__ == "__main__":
    main()
