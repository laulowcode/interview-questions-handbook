# Python Interview Questions

This directory contains Python-specific interview questions and examples, organized by topic.

## 🐍 Topics Covered

### Core Language and API Design

- [GIL (Global Interpreter Lock)](./01-core-language-and-api-design/01-GIL/) - Understanding Python's threading limitations
- [Async/Await](./01-core-language-and-api-design/02-async-await/) - When to use async/await and when not to

## 🚀 Getting Started

### Using Docker (Recommended)

1. **Build and run the container:**

   ```bash
   cd python
   docker compose up -d python-interview
   ```

2. **Execute examples:**

   ```bash
   # Run GIL CPU-bound example
   docker compose exec python-interview python 01-core-language-and-api-design/01-GIL/cpu_bound_example.py

   # Run GIL I/O-bound example
   docker compose exec python-interview python 01-core-language-and-api-design/01-GIL/io_bound_example.py

   # Run interactive GIL demonstration
   docker compose exec python-interview python 01-core-language-and-api-design/01-GIL/gil_demonstration.py
   ```

3. **Access the container shell:**
   ```bash
   docker compose exec python-interview bash
   ```

### Using Local Python Environment

1. **Create virtual environment:**

   ```bash
   cd python
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

3. **Run examples:**
   ```bash
   python 01-core-language-and-api-design/01-GIL/cpu_bound_example.py
   python 01-core-language-and-api-design/01-GIL/io_bound_example.py
   python 01-core-language-and-api-design/01-GIL/gil_demonstration.py
   ```

## 📚 Available Examples

### GIL (Global Interpreter Lock)

- **`cpu_bound_example.py`** - Demonstrates how GIL limits CPU-bound task parallelism
- **`io_bound_example.py`** - Shows how GIL doesn't affect I/O-bound tasks
- **`gil_demonstration.py`** - Interactive demonstration of GIL behavior
