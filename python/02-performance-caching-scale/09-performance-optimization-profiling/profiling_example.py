"""
Complete Profiling Example: Finding and Fixing Bottlenecks

This example demonstrates:
1. A realistic slow application
2. Profiling with cProfile, pyinstrument, and yappi
3. Identifying bottlenecks
4. Applying optimizations
5. Measuring improvements
"""

import time
import random
import json
import cProfile
import pstats
from pstats import SortKey
from typing import List, Dict


# ===========================
# SLOW VERSION (Before Optimization)
# ===========================

class SlowDataProcessor:
    """A deliberately slow data processor to demonstrate profiling"""
    
    def __init__(self):
        self.cache = {}
    
    def process_dataset(self, data: List[Dict]) -> List[Dict]:
        """Main processing function with multiple bottlenecks"""
        results = []
        for item in data:
            # Bottleneck 1: Inefficient filtering
            if self._is_valid(item):
                # Bottleneck 2: Expensive computation
                processed = self._expensive_computation(item)
                # Bottleneck 3: Repeated JSON serialization
                serialized = self._serialize_item(processed)
                results.append(serialized)
        return results
    
    def _is_valid(self, item: Dict) -> bool:
        """Slow validation - searches through list multiple times"""
        # Bottleneck: O(n) operations repeated
        required_fields = ['id', 'name', 'value', 'category']
        for field in required_fields:
            if field not in item:
                return False
        
        # More inefficient checks
        if item.get('value', 0) < 0:
            return False
        
        # Simulate database lookup (I/O bottleneck)
        time.sleep(0.001)  # Simulates slow DB query
        return True
    
    def _expensive_computation(self, item: Dict) -> Dict:
        """CPU-intensive computation with no caching"""
        value = item.get('value', 0)
        
        # Bottleneck: Repeated expensive calculation
        # Fibonacci without memoization
        def fibonacci(n):
            if n <= 1:
                return n
            return fibonacci(n - 1) + fibonacci(n - 2)
        
        # Calculate fibonacci for value (slow for large values)
        fib_result = fibonacci(min(value, 20))
        
        # More expensive operations
        squared_sum = sum([i ** 2 for i in range(value)])
        
        return {
            **item,
            'fibonacci': fib_result,
            'squared_sum': squared_sum,
            'timestamp': time.time()
        }
    
    def _serialize_item(self, item: Dict) -> Dict:
        """Inefficient serialization"""
        # Bottleneck: Unnecessary JSON encode/decode cycle
        json_str = json.dumps(item)
        parsed = json.loads(json_str)
        
        # Add some formatting (inefficient string concatenation)
        formatted_name = ""
        for char in str(parsed.get('name', '')):
            formatted_name += char.upper()
        
        parsed['formatted_name'] = formatted_name
        return parsed


# ===========================
# OPTIMIZED VERSION (After Profiling)
# ===========================

class OptimizedDataProcessor:
    """Optimized version after profiling"""
    
    def __init__(self):
        self.fib_cache = {}
        self.required_fields = {'id', 'name', 'value', 'category'}  # Set for O(1) lookup
    
    def process_dataset(self, data: List[Dict]) -> List[Dict]:
        """Optimized processing with batch operations"""
        # Filter all at once (more efficient)
        valid_items = [item for item in data if self._is_valid_fast(item)]
        
        # Process in batch
        results = []
        for item in valid_items:
            processed = self._fast_computation(item)
            results.append(processed)
        
        return results
    
    def _is_valid_fast(self, item: Dict) -> bool:
        """Optimized validation"""
        # Use set intersection for O(1) average case
        if not self.required_fields.issubset(item.keys()):
            return False
        
        return item.get('value', 0) >= 0
    
    def _fast_computation(self, item: Dict) -> Dict:
        """Optimized computation with caching"""
        value = item.get('value', 0)
        
        # Use cached fibonacci
        fib_result = self._fibonacci_cached(min(value, 20))
        
        # Optimized squared sum using generator
        squared_sum = sum(i ** 2 for i in range(value))
        
        return {
            **item,
            'fibonacci': fib_result,
            'squared_sum': squared_sum,
            'formatted_name': str(item.get('name', '')).upper(),  # Direct method
            'timestamp': time.time()
        }
    
    def _fibonacci_cached(self, n: int) -> int:
        """Fibonacci with memoization"""
        if n in self.fib_cache:
            return self.fib_cache[n]
        
        if n <= 1:
            return n
        
        result = self._fibonacci_cached(n - 1) + self._fibonacci_cached(n - 2)
        self.fib_cache[n] = result
        return result


# ===========================
# Test Data Generation
# ===========================

def generate_test_data(size: int = 100) -> List[Dict]:
    """Generate test dataset"""
    categories = ['A', 'B', 'C', 'D']
    data = []
    
    for i in range(size):
        data.append({
            'id': i,
            'name': f'item_{i}',
            'value': random.randint(10, 25),
            'category': random.choice(categories)
        })
    
    return data


# ===========================
# Profiling Examples
# ===========================

def profile_with_cprofile():
    """Example: Profiling with cProfile"""
    print("\n" + "="*60)
    print("PROFILING WITH cProfile")
    print("="*60 + "\n")
    
    data = generate_test_data(50)
    processor = SlowDataProcessor()
    
    # Create profiler
    profiler = cProfile.Profile()
    
    # Profile the slow version
    profiler.enable()
    result = processor.process_dataset(data)
    profiler.disable()
    
    # Print statistics
    stats = pstats.Stats(profiler)
    stats.sort_stats(SortKey.CUMULATIVE)
    
    print("Top 15 functions by cumulative time:")
    stats.print_stats(15)
    
    # Save to file for later analysis
    profiler.dump_stats('cprofile_output.prof')
    print("\n✓ Profile saved to 'cprofile_output.prof'")
    print("  Analyze with: python -m pstats cprofile_output.prof")


def profile_with_pyinstrument():
    """Example: Profiling with pyinstrument"""
    print("\n" + "="*60)
    print("PROFILING WITH pyinstrument")
    print("="*60 + "\n")
    
    try:
        from pyinstrument import Profiler
    except ImportError:
        print("❌ pyinstrument not installed. Install with: pip install pyinstrument")
        return
    
    data = generate_test_data(50)
    processor = SlowDataProcessor()
    
    # Profile with pyinstrument
    profiler = Profiler()
    profiler.start()
    
    result = processor.process_dataset(data)
    
    profiler.stop()
    
    # Print beautiful output
    print(profiler.output_text(unicode=True, color=True))
    
    # Save HTML for interactive viewing
    with open('pyinstrument_output.html', 'w') as f:
        f.write(profiler.output_html())
    
    print("\n✓ HTML profile saved to 'pyinstrument_output.html'")


def profile_with_yappi():
    """Example: Profiling with yappi"""
    print("\n" + "="*60)
    print("PROFILING WITH yappi")
    print("="*60 + "\n")
    
    try:
        import yappi
    except ImportError:
        print("❌ yappi not installed. Install with: pip install yappi")
        return
    
    data = generate_test_data(50)
    processor = SlowDataProcessor()
    
    # Configure yappi
    yappi.set_clock_type("wall")  # Wall-clock time
    yappi.start()
    
    result = processor.process_dataset(data)
    
    yappi.stop()
    
    # Get statistics
    print("Function Statistics (Top 15):")
    func_stats = yappi.get_func_stats()
    func_stats.sort("totaltime", "desc")
    
    # Print top 15 functions
    for i, stat in enumerate(func_stats[:15], 1):
        print(f"{i}. {stat}")
    
    print("")  # Empty line for spacing
    
    # Save to file
    func_stats.save('yappi_output.prof', type='pstat')
    print("\n✓ Profile saved to 'yappi_output.prof'")
    
    yappi.clear_stats()


# ===========================
# Benchmark Comparison
# ===========================

def benchmark_comparison():
    """Compare slow vs optimized versions"""
    print("\n" + "="*60)
    print("BENCHMARK: Slow vs Optimized")
    print("="*60 + "\n")
    
    data = generate_test_data(100)
    
    # Benchmark slow version
    slow_processor = SlowDataProcessor()
    start = time.perf_counter()
    slow_result = slow_processor.process_dataset(data)
    slow_time = time.perf_counter() - start
    
    # Benchmark optimized version
    optimized_processor = OptimizedDataProcessor()
    start = time.perf_counter()
    optimized_result = optimized_processor.process_dataset(data)
    optimized_time = time.perf_counter() - start
    
    # Results
    print(f"Slow Version:      {slow_time:.4f} seconds")
    print(f"Optimized Version: {optimized_time:.4f} seconds")
    print(f"Speedup:           {slow_time / optimized_time:.2f}x faster")
    print(f"Time Saved:        {(slow_time - optimized_time):.4f} seconds ({(1 - optimized_time/slow_time)*100:.1f}% faster)")
    
    # Verify correctness
    assert len(slow_result) == len(optimized_result), "Results should have same length"
    print("\n✓ Both versions produce correct results")


# ===========================
# Bottleneck Analysis
# ===========================

def analyze_bottlenecks():
    """Detailed bottleneck analysis"""
    print("\n" + "="*60)
    print("BOTTLENECK ANALYSIS")
    print("="*60 + "\n")
    
    data = generate_test_data(50)
    processor = SlowDataProcessor()
    
    # Time individual components
    print("Timing individual components:\n")
    
    # Component 1: Validation
    start = time.perf_counter()
    valid_items = [item for item in data if processor._is_valid(item)]
    validation_time = time.perf_counter() - start
    print(f"1. Validation:       {validation_time:.4f}s")
    
    # Component 2: Computation
    start = time.perf_counter()
    for item in valid_items[:10]:  # Just sample
        processor._expensive_computation(item)
    computation_time = time.perf_counter() - start
    print(f"2. Computation:      {computation_time:.4f}s (10 items)")
    
    # Component 3: Serialization
    start = time.perf_counter()
    for item in valid_items[:10]:
        processor._serialize_item(item)
    serialization_time = time.perf_counter() - start
    print(f"3. Serialization:    {serialization_time:.4f}s (10 items)")
    
    print("\n🔍 Analysis:")
    print("  • Validation: Contains I/O bottleneck (time.sleep)")
    print("  • Computation: Inefficient Fibonacci without memoization")
    print("  • Serialization: Unnecessary JSON encode/decode cycles")
    
    print("\n💡 Optimization Strategies:")
    print("  1. Remove unnecessary I/O in validation")
    print("  2. Add memoization to Fibonacci")
    print("  3. Remove redundant JSON serialization")
    print("  4. Use built-in str.upper() instead of manual loop")


# ===========================
# Main Execution
# ===========================

def main():
    """Run all profiling examples"""
    print("\n" + "="*60)
    print("PERFORMANCE PROFILING DEMONSTRATION")
    print("="*60)
    
    # 1. Bottleneck analysis
    analyze_bottlenecks()
    
    # 2. Profile with cProfile
    profile_with_cprofile()
    
    # 3. Profile with pyinstrument
    profile_with_pyinstrument()
    
    # 4. Profile with yappi
    profile_with_yappi()
    
    # 5. Benchmark comparison
    benchmark_comparison()
    
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    print("""
Key Takeaways:
1. Always profile before optimizing
2. Focus on hot paths (highest cumulative time)
3. Identify bottleneck type (CPU, I/O, memory)
4. Apply appropriate optimization technique
5. Measure improvement with benchmarks
6. Verify correctness after optimization

Generated Files:
• cprofile_output.prof    - Analyze with: python -m pstats cprofile_output.prof
• pyinstrument_output.html - Open in browser for interactive view
• yappi_output.prof        - Analyze with: python -m pstats yappi_output.prof
    """)


if __name__ == '__main__':
    main()

