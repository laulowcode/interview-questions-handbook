#!/usr/bin/env python3
"""
Synchronous vs Asynchronous Comparison Example

This example demonstrates the performance difference between synchronous 
and asynchronous approaches when dealing with I/O-bound operations.

Key Learning Points:
1. Async/await shines with I/O-bound operations (network requests, file I/O, database queries)
2. For CPU-bound tasks, async/await won't provide performance benefits
3. Async code can handle many concurrent operations efficiently
"""

import asyncio
import time
import aiohttp
import requests
from typing import List


def sync_fetch_url(url: str) -> str:
    """Synchronous HTTP request using requests library."""
    try:
        response = requests.get(url, timeout=5)
        return f"[OK] {url}: {response.status_code} ({len(response.content)} bytes)"
    except requests.RequestException as e:
        return f"[ERR] {url}: Error - {str(e)}"


async def async_fetch_url(session: aiohttp.ClientSession, url: str) -> str:
    """Asynchronous HTTP request using aiohttp."""
    try:
        async with session.get(url, timeout=aiohttp.ClientTimeout(total=5)) as response:
            content = await response.read()
            return f"[OK] {url}: {response.status} ({len(content)} bytes)"
    except Exception as e:
        return f"[ERR] {url}: Error - {str(e)}"


def sync_approach(urls: List[str]) -> None:
    """Synchronous approach - requests are made one after another."""
    print("Synchronous Approach (Sequential)")
    print("=" * 50)
    
    start_time = time.time()
    results = []
    
    for url in urls:
        result = sync_fetch_url(url)
        results.append(result)
        print(result)
    
    end_time = time.time()
    print(f"\nTotal time: {end_time - start_time:.2f} seconds")
    print(f"Processed {len(results)} URLs")


async def async_approach(urls: List[str]) -> None:
    """Asynchronous approach - requests are made concurrently."""
    print("\nAsynchronous Approach (Concurrent)")
    print("=" * 50)
    
    start_time = time.time()
    
    async with aiohttp.ClientSession() as session:
        # Create tasks for all URLs concurrently
        tasks = [async_fetch_url(session, url) for url in urls]
        
        # Wait for all tasks to complete
        results = await asyncio.gather(*tasks)
    
    end_time = time.time()
    
    for result in results:
        print(result)
    
    print(f"\nTotal time: {end_time - start_time:.2f} seconds")
    print(f"Processed {len(results)} URLs")


def cpu_bound_sync(n: int) -> int:
    """CPU-bound synchronous task."""
    total = 0
    for i in range(n):
        total += i * i
    return total


async def cpu_bound_async(n: int) -> int:
    """CPU-bound task wrapped in async (doesn't provide real benefits)."""
    total = 0
    for i in range(n):
        total += i * i
        # Adding occasional yields to demonstrate that this doesn't help CPU-bound tasks
        if i % 100000 == 0:
            await asyncio.sleep(0)
    return total


def demonstrate_cpu_bound():
    """Demonstrate why async/await doesn't help with CPU-bound tasks."""
    print("\nCPU-Bound Task Comparison")
    print("=" * 50)
    
    n = 1000000
    
    # Synchronous CPU-bound task
    start_time = time.time()
    result_sync = cpu_bound_sync(n)
    sync_time = time.time() - start_time
    print(f"Sync CPU-bound task: {sync_time:.4f} seconds (result: {result_sync})")
    
    # Asynchronous CPU-bound task (won't be faster)
    async def run_async_cpu():
        start_time = time.time()
        result_async = await cpu_bound_async(n)
        async_time = time.time() - start_time
        print(f"Async CPU-bound task: {async_time:.4f} seconds (result: {result_async})")
        return async_time
    
    asyncio.run(run_async_cpu())
    
    print("\nKey Insight: Async/await doesn't improve CPU-bound task performance!")
    print("   Use multiprocessing for CPU-bound parallelism instead.")


async def demonstrate_async_benefits():
    """Demonstrate scenarios where async/await provides clear benefits."""
    print("\nAsync/Await Benefits Demonstration")
    print("=" * 50)
    
    # Simulate database queries with sleep
    async def simulate_db_query(query_id: int, delay: float) -> str:
        print(f"  Starting query {query_id}...")
        await asyncio.sleep(delay)  # Simulates I/O wait time
        return f"Query {query_id} completed in {delay}s"
    
    # Multiple concurrent "database queries"
    start_time = time.time()
    
    tasks = [
        simulate_db_query(1, 0.5),
        simulate_db_query(2, 0.3),
        simulate_db_query(3, 0.7),
        simulate_db_query(4, 0.2),
        simulate_db_query(5, 0.4),
    ]
    
    results = await asyncio.gather(*tasks)
    total_time = time.time() - start_time
    
    print("\nResults:")
    for result in results:
        print(f"  [OK] {result}")
    
    print(f"\nTotal time: {total_time:.2f} seconds")
    print(f"If done synchronously, would take: {sum([0.5, 0.3, 0.7, 0.2, 0.4]):.1f} seconds")
    print(f"Speedup: {sum([0.5, 0.3, 0.7, 0.2, 0.4])/total_time:.1f}x faster!")


def main():
    """Main function to run all demonstrations."""
    print("Python Async/Await vs Synchronous Comparison")
    print("=" * 60)
    
    # Test URLs (using httpbin.org for reliable testing)
    test_urls = [
        "https://httpbin.org/delay/1",  # 1 second delay
        "https://httpbin.org/delay/2",  # 2 second delay
        "https://httpbin.org/status/200",  # Immediate response
        "https://httpbin.org/json",  # JSON response
        "https://httpbin.org/headers",  # Headers response
    ]
    
    # 1. HTTP Requests Comparison
    sync_approach(test_urls)
    asyncio.run(async_approach(test_urls))
    
    # 2. CPU-bound task comparison
    demonstrate_cpu_bound()
    
    # 3. Async benefits demonstration
    asyncio.run(demonstrate_async_benefits())

if __name__ == "__main__":
    main()
