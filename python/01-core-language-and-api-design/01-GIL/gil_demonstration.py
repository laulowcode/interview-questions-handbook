"""
Interactive demonstration of the GIL in action.

This script shows how the GIL affects thread execution by monitoring
CPU usage and thread behavior in real-time.
"""

import threading
import time
import sys
import os
from threading import Lock


class GILMonitor:
    """Monitor GIL behavior and thread execution."""
    
    def __init__(self):
        self.lock = Lock()
        self.thread_stats = {}
        self.start_time = time.time()
    
    def log_thread_activity(self, thread_id, message):
        """Log thread activity with timestamp."""
        with self.lock:
            current_time = time.time() - self.start_time
            print(f"[{current_time:.3f}s] Thread-{thread_id}: {message}")
    
    def cpu_intensive_work(self, thread_id, duration=2):
        """CPU-intensive work that will be limited by GIL."""
        self.log_thread_activity(thread_id, "Starting CPU-intensive work")
        
        start_time = time.time()
        counter = 0
        
        while time.time() - start_time < duration:
            # CPU-intensive operation
            counter += 1
            if counter % 1000000 == 0:  # Log every million iterations
                self.log_thread_activity(thread_id, f"Processed {counter} iterations")
        
        self.log_thread_activity(thread_id, f"Completed CPU work: {counter} iterations")
        return counter
    
    def io_intensive_work(self, thread_id, duration=2):
        """I/O-intensive work where GIL is released."""
        self.log_thread_activity(thread_id, "Starting I/O-intensive work")
        
        start_time = time.time()
        counter = 0
        
        while time.time() - start_time < duration:
            # I/O operation (sleep releases GIL)
            time.sleep(0.1)
            counter += 1
            if counter % 5 == 0:  # Log every 5 I/O operations
                self.log_thread_activity(thread_id, f"Completed {counter} I/O operations")
        
        self.log_thread_activity(thread_id, f"Completed I/O work: {counter} operations")
        return counter


def demonstrate_cpu_bound_gil():
    """Demonstrate GIL impact on CPU-bound tasks."""
    print("=" * 60)
    print("DEMONSTRATION: GIL Impact on CPU-bound Tasks")
    print("=" * 60)
    print("Notice how threads execute sequentially due to GIL")
    print("Only one thread can execute Python bytecode at a time")
    print()
    
    monitor = GILMonitor()
    threads = []
    
    # Create multiple threads doing CPU-intensive work
    for i in range(3):
        thread = threading.Thread(
            target=monitor.cpu_intensive_work,
            args=(i, 3)  # 3 seconds of work
        )
        threads.append(thread)
    
    # Start all threads
    for thread in threads:
        thread.start()
    
    # Wait for completion
    for thread in threads:
        thread.join()
    
    print("\nCPU-bound demonstration completed!")
    print("Notice: Threads executed sequentially, not in parallel")


def demonstrate_io_bound_gil():
    """Demonstrate GIL behavior with I/O-bound tasks."""
    print("\n" + "=" * 60)
    print("DEMONSTRATION: GIL Behavior with I/O-bound Tasks")
    print("=" * 60)
    print("Notice how threads can run concurrently during I/O operations")
    print("GIL is released during I/O, allowing other threads to run")
    print()
    
    monitor = GILMonitor()
    threads = []
    
    # Create multiple threads doing I/O-intensive work
    for i in range(3):
        thread = threading.Thread(
            target=monitor.io_intensive_work,
            args=(i, 3)  # 3 seconds of work
        )
        threads.append(thread)
    
    # Start all threads
    for thread in threads:
        thread.start()
    
    # Wait for completion
    for thread in threads:
        thread.join()
    
    print("\nI/O-bound demonstration completed!")
    print("Notice: Threads ran concurrently during I/O operations")


def show_gil_info():
    """Display information about the GIL."""
    print("=" * 60)
    print("PYTHON GIL INFORMATION")
    print("=" * 60)
    print(f"Python version: {sys.version}")
    print(f"Platform: {sys.platform}")
    print(f"Thread count: {threading.active_count()}")
    print()
    print("GIL (Global Interpreter Lock) Facts:")
    print("- Only one thread can execute Python bytecode at a time")
    print("- Exists in CPython (most common Python implementation)")
    print("- Released during I/O operations (file, network, etc.)")
    print("- Released during some C extension calls")
    print("- NOT released during pure Python computation")
    print()
    print("Impact:")
    print("- CPU-bound tasks: Threading provides no speedup")
    print("- I/O-bound tasks: Threading works well")
    print("- Solution for CPU-bound: Use multiprocessing")
    print("=" * 60)


def main():
    """Run GIL demonstrations."""
    show_gil_info()
    
    print("\nPress Enter to start CPU-bound demonstration...")
    input()
    demonstrate_cpu_bound_gil()
    
    print("\nPress Enter to start I/O-bound demonstration...")
    input()
    demonstrate_io_bound_gil()
    
    print("\n" + "=" * 60)
    print("DEMONSTRATION COMPLETE")
    print("=" * 60)
    print("Key Takeaways:")
    print("1. GIL prevents true parallelism for CPU-bound tasks")
    print("2. GIL is released during I/O, allowing concurrency")
    print("3. Use multiprocessing for CPU-bound parallel work")
    print("4. Use threading/asyncio for I/O-bound concurrent work")
    print("=" * 60)


if __name__ == "__main__":
    main()
