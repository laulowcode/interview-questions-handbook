"""
Line-by-Line Profiling Example

This demonstrates line_profiler for granular performance analysis.

Usage:
    # Method 1: With kernprof
    kernprof -l -v line_profiling_example.py
    
    # Method 2: Programmatically
    python line_profiling_example.py

Line profiler shows exactly which lines are slow, unlike function-level profilers.
"""

import random
import time
from typing import List, Dict


# ===========================
# Example 1: Identifying Slow Lines
# ===========================

def process_data_slow(data: List[int]) -> Dict[str, int]:
    """
    Function with multiple operations - which line is slowest?
    
    To profile with kernprof:
        Add @profile decorator, then run:
        kernprof -l -v line_profiling_example.py
    """
    # Line 1: List comprehension
    squared = [x ** 2 for x in data]
    
    # Line 2: Sum operation
    total = sum(squared)
    
    # Line 3: Sorting (typically slow)
    sorted_data = sorted(data, reverse=True)
    
    # Line 4: Finding max (after already sorting - inefficient!)
    max_value = max(sorted_data)
    
    # Line 5: Dictionary comprehension
    value_map = {i: x for i, x in enumerate(data)}
    
    # Line 6: Nested loop (O(n²) - very slow!)
    duplicates = []
    for i, val in enumerate(data):
        for j, other in enumerate(data):
            if i != j and val == other:
                duplicates.append(val)
    
    # Line 7: Set operations (fast)
    unique_values = len(set(data))
    
    return {
        'total': total,
        'max': max_value,
        'unique': unique_values,
        'duplicates': len(duplicates)
    }


def process_data_optimized(data: List[int]) -> Dict[str, int]:
    """Optimized version after line profiling"""
    # Combine operations where possible
    squared = [x ** 2 for x in data]
    total = sum(squared)
    
    # Don't sort just to find max - use max() directly on original data
    max_value = max(data)
    
    # Use set for O(1) lookups instead of O(n²) nested loops
    seen = set()
    duplicates = set()
    for val in data:
        if val in seen:
            duplicates.add(val)
        seen.add(val)
    
    unique_values = len(seen)
    
    return {
        'total': total,
        'max': max_value,
        'unique': unique_values,
        'duplicates': len(duplicates)
    }


# ===========================
# Example 2: I/O Operations
# ===========================

def process_with_io(items: List[str]) -> List[str]:
    """
    Function with I/O operations - line profiler helps identify I/O bottlenecks
    """
    results = []
    
    for item in items:
        # Simulate I/O operation (e.g., database query)
        time.sleep(0.001)  # This line will show high time%
        
        # Processing
        processed = item.upper().strip()
        
        # Another I/O operation
        time.sleep(0.001)  # This too
        
        results.append(processed)
    
    return results


def process_with_io_optimized(items: List[str]) -> List[str]:
    """Optimized - batch I/O operations"""
    # Process all items first
    processed = [item.upper().strip() for item in items]
    
    # Simulate batched I/O (instead of per-item)
    time.sleep(0.001 * len(items))  # Same total I/O time, but batched
    
    return processed


# ===========================
# Example 3: String Operations
# ===========================

def string_concatenation_slow(n: int) -> str:
    """Slow string concatenation - line profiler shows which approach is slow"""
    # Method 1: String concatenation with + (slow for large n)
    result = ""
    for i in range(n):
        result = result + str(i) + ","  # This line will be slow
    return result


def string_concatenation_fast(n: int) -> str:
    """Optimized string building"""
    # Method 2: Join with list (fast)
    parts = [str(i) for i in range(n)]
    return ",".join(parts)


# ===========================
# Example 4: List Operations
# ===========================

def list_operations_comparison(data: List[int]):
    """Compare different list operations line-by-line"""
    # Operation 1: List comprehension (fast)
    result1 = [x * 2 for x in data]
    
    # Operation 2: Map (similar speed)
    result2 = list(map(lambda x: x * 2, data))
    
    # Operation 3: For loop with append (slightly slower)
    result3 = []
    for x in data:
        result3.append(x * 2)
    
    # Operation 4: Extending in loop (slower)
    result4 = []
    for x in data:
        result4 = result4 + [x * 2]  # Creates new list each time!
    
    return result1, result2, result3, result4


# ===========================
# Programmatic Line Profiling
# ===========================

def profile_function_line_by_line():
    """
    Demonstrate programmatic line profiling without kernprof
    """
    try:
        from line_profiler import LineProfiler
    except ImportError:
        print("❌ line_profiler not installed")
        print("   Install with: pip install line_profiler")
        return
    
    print("\n" + "="*60)
    print("LINE-BY-LINE PROFILING")
    print("="*60 + "\n")
    
    # Create test data
    data = [random.randint(1, 100) for _ in range(1000)]
    
    # Profile the slow version
    print("Profiling SLOW version:\n")
    profiler = LineProfiler()
    profiler.add_function(process_data_slow)
    profiler.enable()
    
    result_slow = process_data_slow(data)
    
    profiler.disable()
    profiler.print_stats()
    
    # Profile the optimized version
    print("\n" + "="*60)
    print("Profiling OPTIMIZED version:\n")
    
    profiler = LineProfiler()
    profiler.add_function(process_data_optimized)
    profiler.enable()
    
    result_optimized = process_data_optimized(data)
    
    profiler.disable()
    profiler.print_stats()
    
    print("\n" + "="*60)
    print("ANALYSIS")
    print("="*60)
    print("""
Key Findings from Line Profiling:

1. Nested loops (O(n²)) are the biggest bottleneck
   • Replaced with set-based approach (O(n))

2. Sorting just to find max is wasteful
   • Use max() directly instead

3. Creating new lists in loop is slow
   • Use list comprehension or append

Line profiler shows:
• Time per line (not just per function)
• Hit count (how many times each line executed)
• % of total time
    """)


# ===========================
# String Profiling Example
# ===========================

def profile_string_operations():
    """Profile string concatenation approaches"""
    try:
        from line_profiler import LineProfiler
    except ImportError:
        print("❌ line_profiler not installed")
        return
    
    print("\n" + "="*60)
    print("STRING CONCATENATION PROFILING")
    print("="*60 + "\n")
    
    n = 5000
    
    # Profile slow version
    print("Profiling SLOW string concatenation:\n")
    profiler = LineProfiler()
    profiler.add_function(string_concatenation_slow)
    profiler.enable()
    
    result_slow = string_concatenation_slow(n)
    
    profiler.disable()
    profiler.print_stats()
    
    # Profile fast version
    print("\n" + "="*60)
    print("Profiling FAST string concatenation:\n")
    
    profiler = LineProfiler()
    profiler.add_function(string_concatenation_fast)
    profiler.enable()
    
    result_fast = string_concatenation_fast(n)
    
    profiler.disable()
    profiler.print_stats()
    
    # Benchmark
    start = time.perf_counter()
    string_concatenation_slow(n)
    slow_time = time.perf_counter() - start
    
    start = time.perf_counter()
    string_concatenation_fast(n)
    fast_time = time.perf_counter() - start
    
    print("\n" + "="*60)
    print("BENCHMARK RESULTS")
    print("="*60)
    print(f"\nSlow version (+ concatenation): {slow_time:.4f}s")
    print(f"Fast version (str.join):        {fast_time:.4f}s")
    print(f"Speedup: {slow_time / fast_time:.2f}x faster")
    
    print("\n💡 Key Insight:")
    print("   String concatenation with + creates new string each time (O(n²))")
    print("   Using str.join() is O(n) - much faster for large n")


# ===========================
# Understanding Line Profiler Output
# ===========================

def explain_line_profiler_output():
    """Explain how to read line_profiler output"""
    print("\n" + "="*60)
    print("UNDERSTANDING LINE PROFILER OUTPUT")
    print("="*60 + "\n")
    
    print("""
Line profiler output format:

Timer unit: 1e-06 s  (microseconds)

Total time: 0.123456 s
File: script.py
Function: my_function at line 10

Line #      Hits         Time  Per Hit   % Time  Line Contents
==============================================================
    10                                           def my_function():
    11         1        100.0    100.0      1.0      x = [1, 2, 3]
    12      1000       5000.0      5.0     50.0      for i in range(1000):
    13      1000       4900.0      4.9     49.0          y = i ** 2

Columns explained:

• Line #:    Line number in source file
• Hits:      How many times this line was executed
• Time:      Total time spent on this line (in microseconds)
• Per Hit:   Average time per execution (Time / Hits)
• % Time:    Percentage of total function time
• Line Contents: The actual source code

What to look for:

1. High % Time: Lines that take most of the function's time
2. High Hits: Lines executed many times (loop bodies)
3. High Per Hit: Individual expensive operations
4. Unexpected hits: Loops running more than expected

Example Analysis:

Line 12: 50% of time, 1000 hits
  → Loop overhead is significant

Line 13: 49% of time, 1000 hits, 4.9μs per hit
  → The actual work (squaring) takes most time
  → Optimization target: Can we reduce hits or per-hit cost?
    """)


# ===========================
# Best Practices
# ===========================

def line_profiling_best_practices():
    """Best practices for line profiling"""
    print("\n" + "="*60)
    print("LINE PROFILING BEST PRACTICES")
    print("="*60 + "\n")
    
    print("""
1. When to Use Line Profiler:
   ✅ Function-level profiler shows function is slow, but not why
   ✅ Multiple operations in one function
   ✅ Loops with multiple operations per iteration
   ✅ Want to compare different implementation approaches
   
   ❌ Very simple functions (overhead not worth it)
   ❌ Need whole-program overview (use cProfile/pyinstrument first)

2. Workflow:
   Step 1: Use pyinstrument to find slow functions
   Step 2: Use line_profiler on those specific functions
   Step 3: Optimize the slowest lines
   Step 4: Re-profile to verify improvement

3. Common Patterns to Watch For:
   
   • Nested loops (O(n²))
     for i in data:
         for j in data:  # ← This line will show high % Time
             ...
   
   • Repeated operations in loops
     for item in items:
         expensive_function()  # ← Called many times
   
   • Inefficient string building
     result = ""
     for s in strings:
         result += s  # ← O(n²) behavior
   
   • Unnecessary I/O in loops
     for item in items:
         db.query(...)  # ← N queries instead of 1

4. Profiling Multiple Functions:
   
   profiler = LineProfiler()
   profiler.add_function(func1)
   profiler.add_function(func2)
   profiler.add_function(func3)
   profiler.enable()
   # ... run code ...
   profiler.disable()
   profiler.print_stats()

5. Interpreting Results:
   
   • Focus on lines with highest % Time
   • Check if Hits count is expected
   • Look for opportunities to:
     - Move operations out of loops
     - Cache repeated calculations
     - Use better algorithms/data structures
     - Batch I/O operations

6. Combining with Other Profilers:
   
   pyinstrument  → Identify slow functions
        ↓
   line_profiler → Find slow lines in those functions
        ↓
   Optimization
        ↓
   Benchmark     → Verify improvement
    """)


# ===========================
# Main Execution
# ===========================

def main():
    """Run all line profiling examples"""
    print("\n" + "="*70)
    print(" "*20 + "LINE PROFILING EXAMPLES")
    print("="*70)
    
    # Explain output format
    explain_line_profiler_output()
    
    # Run profiling examples
    profile_function_line_by_line()
    
    # String operations example
    profile_string_operations()
    
    # Best practices
    line_profiling_best_practices()
    
    print("\n" + "="*70)
    print("SUMMARY - LINE PROFILING")
    print("="*70)
    print("""
Line profiling is the microscope of performance optimization.

Use it when you need to:
• Identify exactly which lines are slow
• Understand loop performance
• Compare different implementations
• Find hidden bottlenecks in complex functions

Commands to remember:

1. With decorator:
   kernprof -l -v script.py

2. Programmatically:
   from line_profiler import LineProfiler
   profiler = LineProfiler()
   profiler.add_function(my_function)
   profiler.enable()
   # ... run code ...
   profiler.disable()
   profiler.print_stats()

3. View saved profile:
   python -m line_profiler script.py.lprof

Next: Try profiling your own code to find line-level bottlenecks!
    """)


if __name__ == '__main__':
    main()

