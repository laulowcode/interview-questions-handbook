# RQ (Redis Queue) Quick Start Guide

## Quick Start

### 1. Start Services

```bash
cd python
docker compose up -d
```

This starts:

- **Redis** (message broker)
- **RQ Worker** (processes tasks automatically)
- **Python container** (for running examples)

### 2. Enqueue Tasks

```bash
docker exec python-interview-handbook python 02-performance-caching-scale/03-task-queues/rq_example.py producer
```

### 3. Watch Tasks Being Processed

```bash
docker logs -f python-interview-rq-worker
```

### 4. Check Queue Status

```bash
docker exec python-interview-rq-worker rq info
```

---

## Useful Commands

### Queue Management

```bash
# View real-time queue statistics
docker exec python-interview-rq-worker rq info --interval 1

# Empty all queues
docker exec python-interview-rq-worker rq empty high default low

# Requeue failed jobs
docker exec python-interview-rq-worker rq requeue --all

# View worker information
docker exec python-interview-rq-worker rq info --only-workers
```

### Service Management

```bash
# Stop all services
docker compose down

# Restart services
docker compose restart

# View logs
docker compose logs -f rq-worker
docker compose logs -f redis

# Stop and remove all data
docker compose down -v
```

---

## Running Locally (Without Docker)

If you prefer to run without Docker:

```bash
# Terminal 1: Start Redis
redis-server

# Terminal 2: Start RQ Worker
cd python/02-performance-caching-scale/03-task-queues
python rq_example.py worker

# Terminal 3: Enqueue Tasks
cd python/02-performance-caching-scale/03-task-queues
python rq_example.py producer
```

---

## What Gets Demonstrated

1. **Priority Queues**

   - High: Urgent user-facing tasks (emails)
   - Default: Standard background work (image processing)
   - Low: Non-urgent tasks (reports)

2. **Task Types**

   - Simple tasks (email sending)
   - CPU-intensive tasks (image processing)
   - Long-running tasks (report generation)
   - Unreliable tasks with retries
   - Scheduled/delayed tasks
   - Workflow tasks (sequential steps)

3. **Features**
   - Automatic retries with backoff
   - Failed job queue
   - Job status monitoring
   - Result storage
   - Task scheduling

---

## Troubleshooting

### Worker can't import tasks

- **Issue**: `ValueError: Invalid attribute name: tasks.send_email`
- **Solution**: Make sure the worker's working directory is set to `/app/02-performance-caching-scale/03-task-queues`

### Redis connection refused

- **Issue**: `redis.exceptions.ConnectionError`
- **Solution**:
  - Check if Redis is running: `docker ps | grep redis`
  - Restart services: `docker compose restart`

### Tasks not being processed

- **Issue**: Jobs stay in queue
- **Solution**: Check worker logs: `docker logs python-interview-rq-worker`

### Codec errors when monitoring

- **Issue**: `'utf-8' codec can't decode byte`
- **Solution**: Don't use `decode_responses=True` when creating Redis connection for Job.fetch()
