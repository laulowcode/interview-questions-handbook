"""
Example demonstrating GIL impact on CPU-bound tasks.

This example shows how the GIL prevents true parallelism for CPU-intensive tasks,
making multithreading ineffective for CPU-bound operations.
"""

import threading
import time
import multiprocessing
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor


def cpu_intensive_task(n):
    """Simulate a CPU-intensive task (calculating factorial)."""
    result = 1
    for i in range(1, n + 1):
        result *= i
    return result


def run_sequential(n_tasks, task_size):
    """Run tasks sequentially (baseline)."""
    start_time = time.time()
    results = []
    for _ in range(n_tasks):
        result = cpu_intensive_task(task_size)
        results.append(result)
    end_time = time.time()
    return end_time - start_time, results


def run_with_threads(n_tasks, task_size):
    """Run tasks using threads (GIL limits parallelism)."""
    start_time = time.time()
    results = []
    threads = []
    
    def worker():
        result = cpu_intensive_task(task_size)
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


def run_with_thread_pool(n_tasks, task_size):
    """Run tasks using ThreadPoolExecutor."""
    start_time = time.time()
    
    with ThreadPoolExecutor(max_workers=n_tasks) as executor:
        futures = [executor.submit(cpu_intensive_task, task_size) for _ in range(n_tasks)]
        results = [future.result() for future in futures]
    
    end_time = time.time()
    return end_time - start_time, results


def run_with_processes(n_tasks, task_size):
    """Run tasks using processes (bypasses GIL)."""
    start_time = time.time()
    
    with ProcessPoolExecutor(max_workers=n_tasks) as executor:
        futures = [executor.submit(cpu_intensive_task, task_size) for _ in range(n_tasks)]
        results = [future.result() for future in futures]
    
    end_time = time.time()
    return end_time - start_time, results


def main():
    """Compare different approaches for CPU-bound tasks."""
    n_tasks = 4
    task_size = 10000  # Size of factorial calculation
    
    print("=" * 60)
    print("CPU-BOUND TASK COMPARISON (GIL Impact)")
    print("=" * 60)
    print(f"Tasks: {n_tasks}, Task size: {task_size}")
    print()
    
    # Sequential execution
    print("1. Sequential execution (baseline):")
    seq_time, _ = run_sequential(n_tasks, task_size)
    print(f"   Time: {seq_time:.4f} seconds")
    print()
    
    # Threading (limited by GIL)
    print("2. Threading (GIL limits parallelism):")
    thread_time, _ = run_with_threads(n_tasks, task_size)
    print(f"   Time: {thread_time:.4f} seconds")
    print(f"   Speedup: {seq_time/thread_time:.2f}x")
    print()
    
    # ThreadPoolExecutor
    print("3. ThreadPoolExecutor (also limited by GIL):")
    pool_time, _ = run_with_thread_pool(n_tasks, task_size)
    print(f"   Time: {pool_time:.4f} seconds")
    print(f"   Speedup: {seq_time/pool_time:.2f}x")
    print()
    
    # Multiprocessing (bypasses GIL)
    print("4. Multiprocessing (bypasses GIL):")
    process_time, _ = run_with_processes(n_tasks, task_size)
    print(f"   Time: {process_time:.4f} seconds")
    print(f"   Speedup: {seq_time/process_time:.2f}x")
    print()
    
    print("=" * 60)
    print("CONCLUSION:")
    print("- Threading provides little/no speedup for CPU-bound tasks due to GIL")
    print("- Multiprocessing can provide significant speedup by bypassing GIL")
    print("- The overhead of process creation may outweigh benefits for small tasks")
    print("=" * 60)


if __name__ == "__main__":
    main()
