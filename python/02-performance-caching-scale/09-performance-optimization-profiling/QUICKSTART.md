# Quick Start Guide - Performance Profiling

## 🐳 Docker (Recommended)

```bash
# First time: make script executable
chmod +x run_docker.sh

# Start container
./run_docker.sh start

# Run examples
./run_docker.sh all      # Run all examples
./run_docker.sh basic    # Basic profiling
./run_docker.sh advanced # Real-world scenarios
./run_docker.sh line     # Line profiling

# Profile your script
./run_docker.sh profile my_script.py

# Interactive shell
./run_docker.sh shell

# Clean up
./run_docker.sh stop
```

---

## Manual Installation

```bash
# Install all profiling tools
pip install -r requirements.txt

# Or install individually
pip install pyinstrument yappi line-profiler memory-profiler snakeviz
```

## Quick Examples

### 1. Profile a Script (Fastest Way)

```bash
# Using pyinstrument (easiest, beautiful output)
pyinstrument your_script.py

# Using cProfile (built-in, more detailed)
python -m cProfile -o output.prof your_script.py
python -m pstats output.prof
```

### 2. Profile from Within Code

```python
# Quick profiling with pyinstrument
from pyinstrument import Profiler

profiler = Profiler()
profiler.start()

# Your code here
slow_function()

profiler.stop()
print(profiler.output_text(unicode=True, color=True))
```

### 3. Run the Examples

```bash
# Basic profiling demonstration
python profiling_example.py

# Advanced scenarios
python advanced_profiling.py

# Line-by-line profiling
python line_profiling_example.py
```

## Common Commands

### cProfile

```bash
# Profile and save
python -m cProfile -o profile.prof my_script.py

# View interactively
python -m pstats profile.prof
>>> sort cumtime
>>> stats 20

# View in browser (with snakeviz)
snakeviz profile.prof
```

### pyinstrument

```bash
# Profile with output
pyinstrument my_script.py

# Save to HTML
pyinstrument -o profile.html my_script.py

# Profile specific module
pyinstrument -m mypackage.mymodule
```

### yappi

```python
# In your code
import yappi

yappi.set_clock_type("wall")  # or "cpu"
yappi.start()

# Your code

yappi.stop()
yappi.get_func_stats().print_all()
yappi.clear_stats()
```

### line_profiler

```bash
# Add @profile decorator to functions, then:
kernprof -l -v my_script.py

# Or profile specific functions
python -m line_profiler script.py.lprof
```

### memory_profiler

```bash
# Add @profile decorator, then:
python -m memory_profiler my_script.py

# Or in code:
from memory_profiler import profile

@profile
def my_function():
    # Your code
    pass
```

## Decision Tree

```
Which profiler should I use?

├─ Need to profile multi-threaded code?
│  └─ Use yappi
│
├─ Want quick overview with beautiful output?
│  └─ Use pyinstrument
│
├─ Need detailed function-by-function analysis?
│  └─ Use cProfile
│
├─ Want line-by-line time analysis?
│  └─ Use line_profiler
│
└─ Need to profile memory usage?
   └─ Use memory_profiler or tracemalloc
```

## Docker Commands Reference

| Command | Description |
|---------|-------------|
| `./run_docker.sh start` | Start container |
| `./run_docker.sh stop` | Stop container |
| `./run_docker.sh all` | Run all examples |
| `./run_docker.sh basic` | Basic profiling demo |
| `./run_docker.sh advanced` | Real-world scenarios |
| `./run_docker.sh line` | Line profiling |
| `./run_docker.sh profile <file>` | Profile with pyinstrument |
| `./run_docker.sh cprofile <file>` | Profile with cProfile |
| `./run_docker.sh shell` | Open bash shell |
| `./run_docker.sh test` | Quick test |
| `./run_docker.sh help` | Show all commands |

---

## Workflow

1. **Profile** - Run profiler to collect data
2. **Analyze** - Identify bottlenecks (highest cumtime)
3. **Categorize** - CPU-bound? I/O-bound? Memory-bound?
4. **Optimize** - Apply appropriate technique
5. **Measure** - Benchmark before/after
6. **Verify** - Ensure correctness

## Common Bottleneck Patterns

### N+1 Query Problem
```python
# ❌ Bad: One query per item
for user in users:
    org = db.query(Organization).get(user.org_id)  # N queries

# ✅ Good: One query total
org_ids = [u.org_id for u in users]
orgs = db.query(Organization).filter(Organization.id.in_(org_ids)).all()
```

### Missing Memoization
```python
# ❌ Bad: Recalculate every time
def fibonacci(n):
    if n <= 1: return n
    return fibonacci(n-1) + fibonacci(n-2)

# ✅ Good: Cache results
from functools import lru_cache

@lru_cache(maxsize=None)
def fibonacci(n):
    if n <= 1: return n
    return fibonacci(n-1) + fibonacci(n-2)
```

### Inefficient Data Structures
```python
# ❌ Bad: O(n) lookup
items_list = [1, 2, 3, 4, 5]
if item in items_list:  # O(n)
    pass

# ✅ Good: O(1) lookup
items_set = {1, 2, 3, 4, 5}
if item in items_set:  # O(1)
    pass
```

## Output Examples

### cProfile Output
```
   ncalls  tottime  percall  cumtime  percall filename:lineno(function)
        1    0.000    0.000    5.000    5.000 script.py:10(main)
     1000    2.500    0.003    4.500    0.005 script.py:20(process)
```

### pyinstrument Output
```
4.002 script.py:1
└─ 4.002 main  script.py:10
   ├─ 2.500 process_data  script.py:20
   └─ 1.500 load_data  script.py:15
```

### yappi Output (Thread-aware)
```
Clock type: WALL
Ordered by: totaltime, desc

name                    ncall  tsub   ttot   tavg
script.py:20 process     1000  2.500  4.500  0.005
Thread #1                   1  0.000  5.000  5.000
Thread #2                   1  0.000  3.000  3.000
```

## Tips

1. **Start Simple**: Use pyinstrument first for quick feedback
2. **Profile Production-like Data**: Don't profile toy datasets
3. **Focus on Hot Paths**: Optimize the 20% causing 80% of time
4. **Measure Impact**: Always benchmark before/after
5. **Consider Trade-offs**: Sometimes readability > performance
6. **Profile Regularly**: Make it part of your workflow

## Troubleshooting

### "Profiler shows nothing"
- Make sure your code actually runs
- Check if profiler overhead is too high
- Try different profiler (pyinstrument vs cProfile)

### "Results vary between runs"
- Statistical profilers (pyinstrument) sample periodically
- Run multiple times and average results
- Use cProfile for deterministic results

### "Can't profile multi-threaded code"
- Use yappi instead of cProfile/pyinstrument
- Set clock type appropriately (wall vs cpu)

### "Too much output"
- Filter results: `stats.print_stats(10)` for top 10
- Focus on specific modules
- Use pyinstrument's call tree view

## Next Steps

```bash
# 1. Start Docker
./run_docker.sh start

# 2. Run examples
./run_docker.sh all

# 3. Profile your code
./run_docker.sh profile your_script.py

# 4. Read full guide
cat README.md
```

