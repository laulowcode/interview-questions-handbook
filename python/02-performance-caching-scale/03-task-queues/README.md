# Background jobs/task queues: Celery vs Dramatiq vs RQ — which do you choose and why?

The choice between Celery, Dramatiq, and RQ depends entirely on your project's specific needs for simplicity, features, and reliability.

- **Choose RQ** for simplicity and small-to-medium projects, especially if you're already using Redis.
- **Choose Dramatiq** for a balance of simplicity and high reliability, making it a strong default choice.
- **Choose Celery** for large, complex systems that require an extensive feature set, diverse broker support, and complex task workflows.

---

## Head-to-Head Comparison

| Feature            | Celery                                                                                                                                                           | Dramatiq                                                                                          | RQ (Redis Queue)                                                                                         |
| :----------------- | :--------------------------------------------------------------------------------------------------------------------------------------------------------------- | :------------------------------------------------------------------------------------------------ | :------------------------------------------------------------------------------------------------------- |
| **Primary Goal**   | Feature-rich, highly available, distributed task queue.                                                                                                          | Simplicity and reliability.                                                                       | Simplicity and ease of use.                                                                              |
| **Broker Support** | RabbitMQ, Redis, Amazon SQS, and more.                                                                                                                           | RabbitMQ, Redis.                                                                                  | Redis only.                                                                                              |
| **Complexity**     | **High.** Extensive configuration and a steep learning curve.                                                                                                    | **Low.** Minimal boilerplate and simple setup.                                                    | **Very Low.** Extremely simple to set up and use.                                                        |
| **Reliability**    | **High (if configured correctly).** Supports `at-least-once` delivery but can lose tasks by default with some brokers (e.g., Redis) if not carefully configured. | **Very High.** Designed for `at-least-once` delivery by default. Prioritizes not losing messages. | **Moderate.** Basic reliability. Can lose tasks on worker failure as it moves jobs to a "started" queue. |
| **Dependencies**   | Many external dependencies.                                                                                                                                      | Minimal dependencies (broker client).                                                             | Just `redis`.                                                                                            |
| **Core Features**  | Task chaining, groups, chords, retries, rate limiting, scheduling (`celery beat`), extensive monitoring (`flower`).                                              | Automatic retries, middleware support, dead-letter queues, rate limiting. Simple by design.       | Simple queuing, automatic retries, failed job queue.                                                     |
| **Community**      | Very large, mature, and widely adopted.                                                                                                                          | Smaller but active and growing.                                                                   | Large and popular.                                                                                       |

---

## Deeper Dive

### Celery

Celery is the most established and feature-complete task queue in the Python ecosystem. Its power lies in its flexibility and vast array of features.

- **Why choose Celery?**

  - You need complex task workflows like chains (`task1 -> task2`), groups (parallel execution), or chords (group followed by a callback).
  - You require support for a message broker other than Redis or RabbitMQ.
  - You need built-in periodic task scheduling (`celery beat`).
  - Your project is large-scale and can justify the initial setup and maintenance overhead.
  - A rich ecosystem of monitoring tools like **Flower** is a priority.

- **Why avoid Celery?**
  - The configuration is complex and can be brittle.
  - It's overkill for simple background jobs.
  - Its reliability guarantees depend heavily on correct broker and setting configuration, making it easy to misconfigure and lose tasks.

### Dramatiq

Dramatiq was created to be a simpler, more reliable alternative to Celery. It focuses on doing one thing well: processing background tasks reliably.

- **Why choose Dramatiq?**

  - **Reliability is your top concern.** Dramatiq guarantees at-least-once message delivery by default. It is designed from the ground up to prevent message loss.
  - You want a system that is easy to set up and reason about.
  - Its middleware architecture provides powerful, clean extensibility for things like rate limiting, retries, and monitoring.
  - It offers a great balance of essential features without the overwhelming complexity of Celery.

- **Why avoid Dramatiq?**
  - You need support for a broker other than RabbitMQ or Redis.
  - You require the complex, built-in workflow primitives (like chords) that Celery offers.

### RQ (Redis Queue)

RQ's primary advantage is its simplicity. It is built directly on and for Redis, making it incredibly easy to integrate into projects that already use it.

- **Why choose RQ?**

  - Your primary need is to offload simple, non-critical functions to a background worker (e.g., sending emails, processing images).
  - Your project is already using Redis.
  - You want the lowest possible barrier to entry and minimal configuration.
  - Developer productivity and speed of implementation are more important than advanced features.

- **Why avoid RQ?**
  - **Task loss is a major concern.** A worker's abrupt failure can lead to the loss of the job it was processing. While it has a failed queue, it's not as robust as Dramatiq's guarantees.
  - You need to use a different message broker.
  - Your application requires complex task orchestration.

---

## Practical Example: RQ (Redis Queue)

The `rq_example.py` file provides a hands-on demonstration of RQ with common use cases.

### Quick Start with Docker

1. **Start Redis and RQ Worker:**

   ```bash
   cd python
   docker compose up -d
   ```

   This will start:

   - Redis server (port 6379)
   - RQ worker (automatically processing tasks)

2. **Verify services are running:**

   ```bash
   docker compose ps
   ```

3. **Enqueue tasks (from host machine):**

   ```bash
   # Install dependencies locally
   pip install redis rq

   # Enqueue sample tasks (REDIS_HOST defaults to localhost)
   cd python/02-performance-caching-scale/03-task-queues
   python rq_example.py producer
   ```

4. **Monitor worker logs:**

   ```bash
   docker compose logs -f rq-worker
   ```

5. **Check queue status:**
   ```bash
   docker exec -it python-interview-rq-worker rq info
   ```

### Alternative: Run Everything in Docker

```bash
# Enqueue tasks from within the container (REDIS_HOST=redis is set automatically)
docker exec -it python-interview-handbook python 02-performance-caching-scale/03-task-queues/rq_example.py producer

# Or start an interactive shell
docker exec -it python-interview-handbook bash
cd 02-performance-caching-scale/03-task-queues
python rq_example.py producer
```

### Local Development (Without Docker)

If you prefer to run everything locally:

```bash
# 1. Start Redis locally
redis-server

# 2. In terminal 1: Start worker
cd python/02-performance-caching-scale/03-task-queues
python rq_example.py worker

# 3. In terminal 2: Enqueue tasks
cd python/02-performance-caching-scale/03-task-queues
python rq_example.py producer
```

### What the Example Demonstrates

1. **Email Tasks (High Priority):** Immediate user-facing operations
2. **Image Processing (Default Priority):** CPU-intensive background work
3. **Report Generation (Low Priority):** Long-running, non-urgent tasks
4. **Retry Logic:** Handling unreliable tasks with automatic retries
5. **Delayed Tasks:** Scheduling tasks to run in the future
6. **Job Monitoring:** Checking job status and results

### Useful RQ Commands

```bash
# Start a worker manually (inside container)
rq worker high default low --url redis://redis:6379/0

# Monitor queues in real-time
rq info --interval 1

# Empty all queues
rq empty high default low

# Requeue failed jobs
rq requeue --all

# Show detailed worker information
rq info --only-workers
```

### Clean Up

```bash
# Stop all services
docker compose down

# Stop and remove volumes (clears Redis data)
docker compose down -v
```
