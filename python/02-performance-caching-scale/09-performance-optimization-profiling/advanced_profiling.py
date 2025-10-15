"""
Advanced Profiling: Real-World Scenarios

This module demonstrates profiling techniques for:
1. API endpoints and web applications
2. Database query optimization
3. Multi-threaded applications
4. Async/await code
5. Memory profiling
"""

import time
import random
import threading
import asyncio
from typing import List, Dict, Optional
from functools import lru_cache, wraps
from dataclasses import dataclass


# ===========================
# 1. API Endpoint Profiling
# ===========================

class APIEndpointProfiler:
    """
    Example: Profiling Flask/FastAPI endpoints
    
    Common bottlenecks in APIs:
    - Database queries (N+1 problem)
    - External API calls
    - JSON serialization
    - Authentication/authorization
    """
    
    def __init__(self):
        self.db_data = self._init_mock_db()
    
    def _init_mock_db(self) -> Dict:
        """Simulate a database"""
        return {
            'users': [{'id': i, 'name': f'User{i}', 'org_id': i % 10} for i in range(1000)],
            'organizations': [{'id': i, 'name': f'Org{i}'} for i in range(100)]
        }
    
    def get_users_slow(self, limit: int = 100) -> List[Dict]:
        """❌ Slow version with N+1 query problem"""
        users = self.db_data['users'][:limit]
        result = []
        
        for user in users:
            # N+1 problem: One query per user to get organization
            time.sleep(0.001)  # Simulate DB query
            org = self._get_organization(user['org_id'])
            
            result.append({
                'id': user['id'],
                'name': user['name'],
                'organization': org
            })
        
        return result
    
    def get_users_optimized(self, limit: int = 100) -> List[Dict]:
        """✅ Optimized version with eager loading"""
        users = self.db_data['users'][:limit]
        
        # Get all org_ids at once
        org_ids = {user['org_id'] for user in users}
        
        # Single query for all organizations
        time.sleep(0.01)  # Simulate one DB query
        orgs = {org['id']: org for org in self.db_data['organizations'] if org['id'] in org_ids}
        
        # Build result
        result = [
            {
                'id': user['id'],
                'name': user['name'],
                'organization': orgs.get(user['org_id'])
            }
            for user in users
        ]
        
        return result
    
    def _get_organization(self, org_id: int) -> Dict:
        """Simulate database query for organization"""
        time.sleep(0.001)
        return next((org for org in self.db_data['organizations'] if org['id'] == org_id), None)


def profile_api_endpoint():
    """Profile and compare API endpoint performance"""
    print("\n" + "="*60)
    print("1. API ENDPOINT PROFILING (N+1 Query Problem)")
    print("="*60 + "\n")
    
    profiler = APIEndpointProfiler()
    
    # Profile slow version
    start = time.perf_counter()
    result_slow = profiler.get_users_slow(50)
    slow_time = time.perf_counter() - start
    
    # Profile optimized version
    start = time.perf_counter()
    result_optimized = profiler.get_users_optimized(50)
    optimized_time = time.perf_counter() - start
    
    print(f"❌ N+1 Queries (Slow):  {slow_time:.4f}s")
    print(f"✅ Eager Loading (Fast): {optimized_time:.4f}s")
    print(f"📊 Speedup: {slow_time / optimized_time:.2f}x faster")
    
    print("\n🔍 Key Issue: N+1 Query Problem")
    print("  • Slow version: 1 query + N queries for organizations")
    print("  • Optimized: 1 query for users + 1 query for all organizations")
    print("\n💡 Solution: Eager loading / JOIN queries")


# ===========================
# 2. CPU-Bound vs I/O-Bound
# ===========================

def cpu_bound_task(n: int) -> int:
    """Simulate CPU-intensive work"""
    return sum(i * i for i in range(n))


def io_bound_task(duration: float) -> str:
    """Simulate I/O wait (network, disk, etc.)"""
    time.sleep(duration)
    return f"Completed after {duration}s"


def profile_cpu_vs_io():
    """Demonstrate difference between CPU and I/O bound profiling"""
    print("\n" + "="*60)
    print("2. CPU-BOUND vs I/O-BOUND PROFILING")
    print("="*60 + "\n")
    
    try:
        import yappi
    except ImportError:
        print("❌ yappi not installed. Skipping this example.")
        return
    
    # CPU-bound profiling
    print("CPU-Bound Task (use CPU clock):")
    yappi.set_clock_type("cpu")
    yappi.start()
    
    for _ in range(5):
        cpu_bound_task(1000000)
    
    yappi.stop()
    stats = yappi.get_func_stats()
    stats.filter(lambda x: 'cpu_bound_task' in x.name).print_all()
    yappi.clear_stats()
    
    print("\n" + "-"*60 + "\n")
    
    # I/O-bound profiling
    print("I/O-Bound Task (use wall clock):")
    yappi.set_clock_type("wall")
    yappi.start()
    
    for _ in range(5):
        io_bound_task(0.01)
    
    yappi.stop()
    stats = yappi.get_func_stats()
    stats.filter(lambda x: 'io_bound_task' in x.name).print_all()
    yappi.clear_stats()
    
    print("\n💡 Key Difference:")
    print("  • CPU-bound: CPU time ≈ Wall time (actively computing)")
    print("  • I/O-bound: CPU time << Wall time (waiting for I/O)")


# ===========================
# 3. Multi-threaded Profiling
# ===========================

class WorkerThread:
    """Example multi-threaded application"""
    
    @staticmethod
    def process_chunk(chunk_id: int, data: List[int]) -> int:
        """Process a chunk of data"""
        # Simulate work
        result = sum(i ** 2 for i in data)
        time.sleep(0.01)  # Simulate I/O
        return result


def profile_multithreaded():
    """Profile multi-threaded application"""
    print("\n" + "="*60)
    print("3. MULTI-THREADED PROFILING")
    print("="*60 + "\n")
    
    try:
        import yappi
    except ImportError:
        print("❌ yappi not installed. Skipping this example.")
        return
    
    # Generate data
    data_chunks = [[random.randint(1, 100) for _ in range(1000)] for _ in range(4)]
    
    # Profile multi-threaded execution
    yappi.set_clock_type("wall")
    yappi.start()
    
    threads = []
    results = []
    
    def worker(chunk_id, data):
        result = WorkerThread.process_chunk(chunk_id, data)
        results.append(result)
    
    for i, chunk in enumerate(data_chunks):
        t = threading.Thread(target=worker, args=(i, chunk))
        threads.append(t)
        t.start()
    
    for t in threads:
        t.join()
    
    yappi.stop()
    
    # Show thread statistics
    print("Thread Statistics:")
    yappi.get_thread_stats().print_all()
    
    print("\nFunction Statistics (filtered):")
    stats = yappi.get_func_stats()
    stats.filter(lambda x: 'process_chunk' in x.name).print_all()
    
    yappi.clear_stats()
    
    print("\n💡 Key Insight:")
    print("  • yappi shows per-thread statistics")
    print("  • Can identify thread contention and GIL bottlenecks")


# ===========================
# 4. Async/Await Profiling
# ===========================

async def async_fetch(url: str, delay: float) -> str:
    """Simulate async HTTP request"""
    await asyncio.sleep(delay)
    return f"Data from {url}"


async def async_process_urls(urls: List[str]) -> List[str]:
    """Process multiple URLs concurrently"""
    tasks = [async_fetch(url, random.uniform(0.01, 0.05)) for url in urls]
    results = await asyncio.gather(*tasks)
    return results


def profile_async():
    """Profile async/await code"""
    print("\n" + "="*60)
    print("4. ASYNC/AWAIT PROFILING")
    print("="*60 + "\n")
    
    try:
        from pyinstrument import Profiler
    except ImportError:
        print("❌ pyinstrument not installed. Skipping this example.")
        return
    
    urls = [f"https://api.example.com/data/{i}" for i in range(10)]
    
    profiler = Profiler(async_mode='enabled')
    profiler.start()
    
    # Run async code
    results = asyncio.run(async_process_urls(urls))
    
    profiler.stop()
    
    print(profiler.output_text(unicode=True, color=True, show_all=True))
    
    print("\n💡 Key Insight:")
    print("  • Use pyinstrument with async_mode='enabled'")
    print("  • Shows time spent in async operations")
    print("  • Identifies slow async calls")


# ===========================
# 5. Caching Impact Analysis
# ===========================

class CachingExample:
    """Demonstrate profiling with and without caching"""
    
    def __init__(self):
        self.call_count_no_cache = 0
        self.call_count_with_cache = 0
    
    def expensive_computation_no_cache(self, n: int) -> int:
        """No caching - every call is expensive"""
        self.call_count_no_cache += 1
        time.sleep(0.01)  # Simulate expensive operation
        return n ** 2
    
    @lru_cache(maxsize=128)
    def expensive_computation_cached(self, n: int) -> int:
        """With LRU cache"""
        self.call_count_with_cache += 1
        time.sleep(0.01)  # Simulate expensive operation
        return n ** 2


def profile_caching_impact():
    """Profile the impact of caching"""
    print("\n" + "="*60)
    print("5. CACHING IMPACT ANALYSIS")
    print("="*60 + "\n")
    
    example = CachingExample()
    
    # Test data with repetition (cache-friendly)
    test_values = [random.randint(1, 20) for _ in range(100)]
    
    # Without cache
    start = time.perf_counter()
    results_no_cache = [example.expensive_computation_no_cache(v) for v in test_values]
    time_no_cache = time.perf_counter() - start
    
    # With cache
    start = time.perf_counter()
    results_cached = [example.expensive_computation_cached(v) for v in test_values]
    time_cached = time.perf_counter() - start
    
    print(f"❌ Without Cache:")
    print(f"   Time: {time_no_cache:.4f}s")
    print(f"   Function calls: {example.call_count_no_cache}")
    
    print(f"\n✅ With LRU Cache:")
    print(f"   Time: {time_cached:.4f}s")
    print(f"   Function calls: {example.call_count_with_cache}")
    
    print(f"\n📊 Results:")
    print(f"   Speedup: {time_no_cache / time_cached:.2f}x faster")
    print(f"   Calls reduced: {example.call_count_no_cache} → {example.call_count_with_cache}")
    print(f"   Cache hit rate: {(1 - example.call_count_with_cache/100)*100:.1f}%")
    
    print("\n💡 Key Insight:")
    print("  • Caching can dramatically improve performance for repeated operations")
    print("  • Profile to identify cacheable operations")
    print("  • Monitor cache hit rates")


# ===========================
# 6. Memory Profiling Integration
# ===========================

def memory_intensive_operation():
    """Operation that uses significant memory"""
    # Create large data structures
    large_list = [i ** 2 for i in range(1_000_000)]
    large_dict = {i: str(i) * 100 for i in range(100_000)}
    
    # Process data
    result = sum(large_list)
    
    return result


def profile_memory():
    """Demonstrate memory profiling"""
    print("\n" + "="*60)
    print("6. MEMORY PROFILING")
    print("="*60 + "\n")
    
    try:
        from memory_profiler import profile
        print("✅ memory_profiler is installed")
        print("\nTo profile memory usage, run:")
        print("  python -m memory_profiler advanced_profiling.py")
        print("\nOr use the @profile decorator:")
        print("""
  from memory_profiler import profile
  
  @profile
  def my_function():
      large_list = [i**2 for i in range(1000000)]
      return sum(large_list)
        """)
    except ImportError:
        print("❌ memory_profiler not installed")
        print("   Install with: pip install memory_profiler")
        print("\nAlternatives:")
        print("  • tracemalloc (built-in to Python 3.4+)")
        print("  • pympler")
        print("  • guppy3")
    
    # Demonstrate tracemalloc (built-in)
    print("\n" + "-"*60)
    print("Using tracemalloc (built-in):")
    print("-"*60 + "\n")
    
    import tracemalloc
    
    tracemalloc.start()
    
    # Take snapshot before
    snapshot1 = tracemalloc.take_snapshot()
    
    # Run memory-intensive operation
    result = memory_intensive_operation()
    
    # Take snapshot after
    snapshot2 = tracemalloc.take_snapshot()
    
    # Compare snapshots
    top_stats = snapshot2.compare_to(snapshot1, 'lineno')
    
    print("Top 5 memory allocations:")
    for stat in top_stats[:5]:
        print(stat)
    
    current, peak = tracemalloc.get_traced_memory()
    print(f"\nCurrent memory: {current / 1024 / 1024:.2f} MB")
    print(f"Peak memory: {peak / 1024 / 1024:.2f} MB")
    
    tracemalloc.stop()
    
    print("\n💡 Key Insight:")
    print("  • Use tracemalloc for built-in memory profiling")
    print("  • memory_profiler for line-by-line analysis")
    print("  • Profile memory alongside time for complete picture")


# ===========================
# 7. Profiling Decorator
# ===========================

def profile_decorator(profiler_type='pyinstrument'):
    """Decorator to profile any function"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if profiler_type == 'cprofile':
                import cProfile
                import pstats
                profiler = cProfile.Profile()
                profiler.enable()
                result = func(*args, **kwargs)
                profiler.disable()
                stats = pstats.Stats(profiler)
                stats.sort_stats('cumulative')
                stats.print_stats(10)
            
            elif profiler_type == 'pyinstrument':
                try:
                    from pyinstrument import Profiler
                    profiler = Profiler()
                    profiler.start()
                    result = func(*args, **kwargs)
                    profiler.stop()
                    print(profiler.output_text(unicode=True, color=True))
                except ImportError:
                    print("pyinstrument not installed, running without profiling")
                    result = func(*args, **kwargs)
            
            else:
                result = func(*args, **kwargs)
            
            return result
        return wrapper
    return decorator


@profile_decorator('pyinstrument')
def example_function_to_profile():
    """Example function with profiling decorator"""
    data = [random.randint(1, 100) for _ in range(10000)]
    result = sorted(data)
    return result


def demonstrate_decorator():
    """Demonstrate profiling decorator"""
    print("\n" + "="*60)
    print("7. PROFILING DECORATOR")
    print("="*60 + "\n")
    
    print("Using @profile_decorator on a function:\n")
    try:
        result = example_function_to_profile()
        print("\n✅ Decorator makes it easy to profile any function")
    except:
        print("❌ Install pyinstrument to see the decorator in action")


# ===========================
# Main Execution
# ===========================

def main():
    """Run all advanced profiling examples"""
    print("\n" + "="*60)
    print("ADVANCED PROFILING TECHNIQUES")
    print("="*60)
    
    # 1. API endpoint profiling (N+1 problem)
    profile_api_endpoint()
    
    # 2. CPU vs I/O bound
    profile_cpu_vs_io()
    
    # 3. Multi-threaded profiling
    profile_multithreaded()
    
    # 4. Async/await profiling
    profile_async()
    
    # 5. Caching impact
    profile_caching_impact()
    
    # 6. Memory profiling
    profile_memory()
    
    # 7. Profiling decorator
    demonstrate_decorator()
    
    print("\n" + "="*60)
    print("SUMMARY - ADVANCED PROFILING")
    print("="*60)
    print("""
Real-World Profiling Scenarios:

1. API Endpoints: Watch for N+1 query problems
   → Solution: Eager loading, JOIN queries

2. CPU vs I/O: Choose the right clock type
   → CPU-bound: Use CPU clock
   → I/O-bound: Use wall clock

3. Multi-threading: Use yappi for thread-aware profiling
   → Identifies thread contention and GIL bottlenecks

4. Async/await: Use pyinstrument with async_mode='enabled'
   → Shows time in async operations

5. Caching: Profile before/after to measure impact
   → Monitor cache hit rates

6. Memory: Combine time and memory profiling
   → Use tracemalloc or memory_profiler

7. Decorators: Make profiling easy and reusable
   → Profile only when needed

Next Steps:
• Profile your own applications
• Focus on the largest bottlenecks first
• Measure before and after optimization
• Consider trade-offs (complexity vs performance)
    """)


if __name__ == '__main__':
    main()

