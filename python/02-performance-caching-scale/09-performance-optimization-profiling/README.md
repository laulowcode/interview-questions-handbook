# Performance Optimization: Profiling & Finding Bottlenecks

## 🐳 Quick Start with Docker

```bash
./run_docker.sh start    # Start container
./run_docker.sh all      # Run all examples
./run_docker.sh help     # See all commands
```

See [QUICKSTART.md](QUICKSTART.md) for all Docker commands and usage.

---

## Overview

Performance profiling is the process of measuring where your program spends its time and resources. This guide covers three powerful Python profiling tools and how to use them to identify and fix bottlenecks.

## Key Profiling Tools

### 1. cProfile (Built-in)
- **Type**: Deterministic profiler (built into Python)
- **Use Case**: General-purpose profiling, production-ready
- **Overhead**: Moderate (~2-5x slower)
- **Output**: Function call statistics

### 2. pyinstrument
- **Type**: Statistical/sampling profiler
- **Use Case**: Finding slow code quickly, easy-to-read output
- **Overhead**: Low (~1.5x slower)
- **Output**: Beautiful call tree visualization

### 3. yappi (Yet Another Python Profiler)
- **Type**: Multi-threaded aware profiler
- **Use Case**: Threading/async code, wall-clock vs CPU time
- **Overhead**: Low to moderate
- **Output**: Thread-aware statistics

---

## 1. cProfile - Built-in Profiler

### Basic Usage

```python
import cProfile
import pstats
from pstats import SortKey

def my_function():
    # Your code here
    pass

# Method 1: Direct profiling
cProfile.run('my_function()')

# Method 2: Programmatic profiling
profiler = cProfile.Profile()
profiler.enable()
my_function()
profiler.disable()

# Print statistics
stats = pstats.Stats(profiler)
stats.sort_stats(SortKey.CUMULATIVE)
stats.print_stats(10)  # Top 10 functions
```

### Command Line Usage

```bash
# Profile a script
python -m cProfile -o output.prof my_script.py

# Analyze the output
python -m pstats output.prof
# Then in the interactive shell:
# sort cumtime
# stats 20
```

### Understanding cProfile Output

```
   ncalls  tottime  percall  cumtime  percall filename:lineno(function)
        1    0.000    0.000    5.000    5.000 example.py:10(slow_function)
   100000    2.500    0.000    2.500    0.000 {built-in method sum}
```

- **ncalls**: Number of calls
- **tottime**: Total time spent in function (excluding sub-calls)
- **percall**: tottime/ncalls
- **cumtime**: Cumulative time (including sub-calls)
- **percall**: cumtime/ncalls

### Pros & Cons

**Pros:**
- Built into Python (no installation needed)
- Deterministic (captures all function calls)
- Production-ready and widely used
- Can save profiles to disk for later analysis

**Cons:**
- Output can be overwhelming for large programs
- Significant overhead (2-5x slower)
- Text-based output is hard to read
- Not great for multi-threaded code

---

## 2. pyinstrument - Statistical Profiler

### Installation

```bash
pip install pyinstrument
```

### Basic Usage

```python
from pyinstrument import Profiler

profiler = Profiler()
profiler.start()

# Your code here
my_function()

profiler.stop()

# Print results
print(profiler.output_text(unicode=True, color=True))

# HTML output
with open('profile.html', 'w') as f:
    f.write(profiler.output_html())
```

### Command Line Usage

```bash
# Profile a script
pyinstrument my_script.py

# Save to HTML
pyinstrument -o profile.html my_script.py

# Profile specific function
pyinstrument -m module_name
```

### Decorator Usage

```python
from pyinstrument import Profiler

def profile_this(func):
    def wrapper(*args, **kwargs):
        profiler = Profiler()
        profiler.start()
        result = func(*args, **kwargs)
        profiler.stop()
        print(profiler.output_text(unicode=True, color=True))
        return result
    return wrapper

@profile_this
def my_slow_function():
    # Your code
    pass
```

### Understanding pyinstrument Output

```
  _     ._   __/__   _ _  _  _ _/_   Recorded: 12:34:56  Samples:  4000
 /_//_/// /_\ / //_// / //_'/ //     Duration: 4.002     CPU time: 3.998
/   _/                      v4.0.0

Program: my_script.py

4.002 my_script  my_script.py:1
└─ 4.002 main  my_script.py:10
   ├─ 2.500 process_data  my_script.py:20
   │  └─ 2.000 expensive_computation  my_script.py:30
   └─ 1.500 load_data  my_script.py:15
      └─ 1.400 json.loads  <built-in>
```

### Pros & Cons

**Pros:**
- Beautiful, easy-to-read output
- Low overhead (~1.5x slower)
- Great for quick profiling during development
- HTML output with interactive visualization
- Focuses on "hot paths" (most time-consuming)

**Cons:**
- Statistical sampling (might miss quick functions)
- Less detailed than cProfile for some use cases
- Not deterministic (results vary slightly)
- Not ideal for production monitoring

---

## 3. yappi - Multi-threaded Profiler

### Installation

```bash
pip install yappi
```

### Basic Usage

```python
import yappi

# Start profiling
yappi.set_clock_type("wall")  # or "cpu"
yappi.start()

# Your code here
my_function()

yappi.stop()

# Get function statistics
func_stats = yappi.get_func_stats()
func_stats.print_all()

# Get thread statistics
thread_stats = yappi.get_thread_stats()
thread_stats.print_all()

# Save to file
func_stats.save('profile.prof', type='pstat')  # cProfile format

yappi.clear_stats()
```

### Clock Types

```python
# Wall-clock time (real time elapsed)
yappi.set_clock_type("wall")  # Default, best for I/O-bound

# CPU time (actual CPU usage)
yappi.set_clock_type("cpu")   # Best for CPU-bound
```

### Thread Profiling

```python
import yappi
import threading
import time

def worker(n):
    time.sleep(n)
    # Some work
    sum([i**2 for i in range(1000000)])

yappi.start()

threads = [
    threading.Thread(target=worker, args=(0.1,)),
    threading.Thread(target=worker, args=(0.2,))
]

for t in threads:
    t.start()
for t in threads:
    t.join()

yappi.stop()

# Show stats per thread
yappi.get_thread_stats().print_all()
yappi.get_func_stats().print_all()
```

### Filtering and Sorting

```python
# Get stats
stats = yappi.get_func_stats()

# Filter by module
stats.filter(lambda x: 'my_module' in x.module).print_all()

# Sort by total time
stats.sort("totaltime", "desc").print_all()

# Sort options: name, ncall, tsub, ttot, tavg
```

### Pros & Cons

**Pros:**
- Excellent for multi-threaded applications
- Wall-clock vs CPU time profiling
- Can profile long-running applications
- Good performance (low overhead)
- Thread-aware statistics

**Cons:**
- Requires separate installation
- Less intuitive output than pyinstrument
- Overkill for single-threaded apps
- Steeper learning curve

---

## Finding Bottlenecks: Methodology

### 1. Profile First, Optimize Later
```python
# ❌ Don't guess
def process_data(data):
    # I think this is slow?
    return [expensive_op(x) for x in data]

# ✅ Profile to confirm
profiler = Profiler()
profiler.start()
result = process_data(data)
profiler.stop()
print(profiler.output_text())
```

### 2. Focus on Hot Paths
Look for:
- Functions with high **cumtime** (total time including calls)
- Functions called many times with significant **tottime**
- Deep call stacks indicating complex operations

### 3. Identify Bottleneck Types

#### CPU-Bound Bottlenecks
```python
# Symptoms: High CPU usage, tottime ≈ cumtime
def cpu_intensive():
    return sum([i**2 for i in range(10_000_000)])  # Pure computation
```

**Solutions:**
- Algorithm optimization
- Caching/memoization
- Vectorization (NumPy)
- Multiprocessing
- C extensions (Cython, numba)

#### I/O-Bound Bottlenecks
```python
# Symptoms: cumtime >> tottime, waiting on I/O
def io_intensive():
    response = requests.get('https://api.example.com')  # Network wait
    return response.json()
```

**Solutions:**
- Async/await
- Connection pooling
- Caching
- Batch operations
- Threading

#### Memory-Bound Bottlenecks
```python
# Symptoms: Large memory allocations, GC pauses
def memory_intensive():
    return [x**2 for x in range(100_000_000)]  # Large list
```

**Solutions:**
- Generators instead of lists
- Streaming/chunking
- Memory-efficient data structures
- Release references early

### 4. Measure Before and After

```python
import time

def benchmark(func, *args, **kwargs):
    start = time.perf_counter()
    result = func(*args, **kwargs)
    end = time.perf_counter()
    print(f"{func.__name__}: {end - start:.4f}s")
    return result

# Before optimization
benchmark(slow_function)

# After optimization
benchmark(optimized_function)
```

---

## Practical Example: Complete Workflow

See `profiling_example.py` for a complete example that demonstrates:
1. Creating a realistic slow application
2. Profiling with all three tools
3. Identifying bottlenecks
4. Applying optimizations
5. Measuring improvements

### Running the Examples

**With Docker (recommended):**
```bash
./run_docker.sh basic       # Run profiling_example.py
./run_docker.sh advanced    # Run advanced_profiling.py
./run_docker.sh line        # Run line_profiling_example.py
```

**Without Docker:**
```bash
pip install -r requirements.txt
python profiling_example.py
python advanced_profiling.py
python line_profiling_example.py
```

---

## Best Practices

### 1. Use the Right Tool
- **Quick checks during development**: pyinstrument
- **Detailed analysis**: cProfile
- **Multi-threaded/async code**: yappi
- **Production monitoring**: Dedicated APM tools (Datadog, New Relic)

### 2. Profile Realistic Scenarios
```python
# ❌ Don't profile toy data
profile(process_data([1, 2, 3]))

# ✅ Profile production-like workloads
profile(process_data(load_real_dataset()))
```

### 3. Profile Multiple Times
```python
import statistics

times = []
for _ in range(10):
    start = time.perf_counter()
    my_function()
    times.append(time.perf_counter() - start)

print(f"Mean: {statistics.mean(times):.4f}s")
print(f"Stdev: {statistics.stdev(times):.4f}s")
```

### 4. Consider the Profiler Overhead
```python
# For very fast functions, overhead matters
def fast_function():
    return sum(range(100))

# Profile the overall operation, not individual calls
profiler.start()
for _ in range(10000):
    fast_function()
profiler.stop()
```

### 5. Combine with Other Tools

#### Memory profiling
```bash
pip install memory_profiler
python -m memory_profiler my_script.py
```

#### Line profiling
```bash
pip install line_profiler
kernprof -l -v my_script.py
```

---

## Common Pitfalls

### 1. Premature Optimization
- Profile first, optimize later
- Focus on actual bottlenecks, not perceived ones

### 2. Optimizing the Wrong Thing
- 80/20 rule: 80% of time is spent in 20% of code
- Optimizing non-bottleneck code wastes time

### 3. Ignoring Algorithmic Complexity
```python
# ❌ Optimizing O(n²) algorithm
for i in data:
    for j in data:
        if i == j: ...  # Micro-optimizations won't help

# ✅ Change to O(n) algorithm
seen = set()
for i in data:
    if i in seen: ...
```

### 4. Not Testing After Optimization
```python
# Always verify correctness
assert optimized_function(test_input) == original_function(test_input)
```

---

## Interview Tips

### What to Discuss
1. **Understanding the problem**: CPU vs I/O vs memory bound
2. **Tool selection**: Why choose one profiler over another
3. **Methodology**: Profile → Identify → Optimize → Measure
4. **Trade-offs**: Performance vs readability vs maintainability
5. **Real-world experience**: Examples from past projects

### Sample Questions & Answers

**Q: How would you find performance bottlenecks in a Python application?**

**A:** I'd follow a systematic approach:
1. Start with pyinstrument for quick overview of hot paths
2. Use cProfile for detailed function-level analysis
3. If threading is involved, use yappi to see thread-specific stats
4. Focus on functions with highest cumulative time
5. Determine if bottleneck is CPU, I/O, or memory bound
6. Apply appropriate optimization (caching, async, algorithms)
7. Measure improvement with benchmarks

**Q: What's the difference between cProfile and pyinstrument?**

**A:** 
- **cProfile**: Deterministic profiler (tracks every call), higher overhead (~2-5x), detailed but verbose output, built-in
- **pyinstrument**: Statistical profiler (samples periodically), lower overhead (~1.5x), focuses on hot paths, beautiful visualization

Choose cProfile for comprehensive analysis and production; pyinstrument for quick development feedback.

**Q: When would you use yappi over cProfile?**

**A:** Yappi is superior when:
1. Profiling multi-threaded applications (thread-aware)
2. Need to distinguish wall-clock time vs CPU time
3. Profiling async code with concurrent operations
4. Long-running applications that need runtime profiling

cProfile doesn't handle threads well and can't distinguish wall vs CPU time.

---

## Additional Resources

### Tools
- **cProfile**: Built-in, no installation needed
- **pyinstrument**: `pip install pyinstrument`
- **yappi**: `pip install yappi`
- **line_profiler**: `pip install line_profiler` (line-by-line)
- **memory_profiler**: `pip install memory_profiler` (memory usage)
- **py-spy**: `pip install py-spy` (sampling profiler, no code changes)

### Visualization
- **SnakeViz**: Interactive cProfile viewer (`pip install snakeviz`)
- **gprof2dot**: Convert profiles to graphs (`pip install gprof2dot`)
- **FlameGraph**: Flame graph visualization

### Further Reading
- Python Performance Tips: https://wiki.python.org/moin/PythonSpeed
- High Performance Python (Book)
- Python's official profiling docs

---

## Summary

| Tool | Best For | Overhead | Multi-thread |
|------|----------|----------|--------------|
| **cProfile** | Detailed analysis | Moderate (2-5x) | ❌ |
| **pyinstrument** | Quick profiling | Low (1.5x) | ❌ |
| **yappi** | Threading, async | Low-Moderate | ✅ |
| **line_profiler** | Line-by-line | High (10-100x) | ❌ |

### Quick Decision

- Multi-threaded/async? → **yappi**
- Quick overview? → **pyinstrument**  
- Detailed analysis? → **cProfile**
- Line-by-line? → **line_profiler**

### Run Examples

```bash
./run_docker.sh all              # Run all examples
python profiling_example.py      # Basic examples
python advanced_profiling.py     # Real-world scenarios
python line_profiling_example.py # Line profiling
```

