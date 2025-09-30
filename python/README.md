# Python Interview Questions

This directory contains Python-specific interview questions and examples, organized by topic.

## 🐍 Topics Covered

### [Group A: Core Language & API Design](./01-core-language-and-api-design/)
- GIL, async/await, Flask vs FastAPI vs Django
- API versioning, ORM vs raw SQL
- Database transactions (ACID), indexing, migrations
- Schema relationships, pagination

### [Group B: Performance, Caching & Scale](./02-performance-caching-scale/)
- Redis caching patterns, rate limiting
- Background jobs (Celery, Dramatiq, RQ)
- Streaming responses, authentication methods
- Security, logging, monitoring, profiling

### [Group C: Concurrency, Async, IO & Data](./03-concurrency-async-io-data/)
- Threading vs multiprocessing vs async
- I/O optimization, file streaming
- Retry logic, email/notifications
- Data validation, schema changes, API contracts

### [Group D: Deployment, Architecture, Reliability](./04-deployment-architecture-reliability/)
- CI/CD, Docker best practices
- Kubernetes deployment, zero downtime
- Logging, migrations, backup/restore
- Secrets management, environment separation

### [Group E: Scalability, Resilience & Advanced](./05-scalability-resilience-advanced/)
- Traffic scaling, load balancing
- HTTP caching, failure handling
- Microservices consistency, observability
- Cost optimization, security audits, feature flags

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
