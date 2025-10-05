#!/usr/bin/env python3
"""
RQ (Redis Queue) Example - Background Task Processing

This example demonstrates how to use RQ for processing background tasks,
including task queuing, job monitoring, retries, and error handling.

Key Learning Points:
1. RQ is simple and lightweight, perfect for small-to-medium projects
2. It uses Redis as both the message broker and result backend
3. Easy to set up with minimal configuration
4. Built-in support for job retries and failed job queue

Prerequisites:
- Redis must be running (see docker-compose.yml)
- Install: pip install rq redis
"""

import time
import redis
from rq import Queue, Worker, Retry
from rq.job import Job
from rq.registry import FailedJobRegistry, FinishedJobRegistry, StartedJobRegistry
import os

# Import task functions from the tasks module
# (RQ requires tasks to be in an importable module, not __main__)
from tasks import (
    send_email,
    process_image,
    generate_report,
    unreliable_task,
    task_with_dependencies
)


# ============================================================================
# PRODUCER - Enqueues tasks
# ============================================================================

def enqueue_tasks():
    """
    Producer function that enqueues various types of tasks to RQ.
    This simulates a web application creating background jobs.
    """
    # Connect to Redis (use 'redis' hostname when running in Docker, 'localhost' otherwise)
    redis_host = os.getenv('REDIS_HOST', 'localhost')
    redis_conn = redis.Redis(host=redis_host, port=6379, db=0, decode_responses=True)
    
    # Create queues with different priorities
    default_queue = Queue('default', connection=redis_conn)
    high_priority_queue = Queue('high', connection=redis_conn)
    low_priority_queue = Queue('low', connection=redis_conn)
    
    print("=" * 70)
    print("RQ TASK PRODUCER - Enqueuing Background Tasks")
    print("=" * 70)
    
    # 1. Enqueue email tasks (high priority)
    print("\n[1] Enqueueing HIGH PRIORITY email tasks...")
    email_job1 = high_priority_queue.enqueue(
        send_email,
        to_email="user1@example.com",
        subject="Welcome to our service",
        body="Thank you for signing up!"
    )
    print(f"   ✓ Enqueued email job: {email_job1.id}")
    
    email_job2 = high_priority_queue.enqueue(
        send_email,
        to_email="user2@example.com",
        subject="Password Reset",
        body="Click here to reset your password"
    )
    print(f"   ✓ Enqueued email job: {email_job2.id}")
    
    # 2. Enqueue image processing tasks (default priority)
    print("\n[2] Enqueueing DEFAULT PRIORITY image processing tasks...")
    image_job1 = default_queue.enqueue(
        process_image,
        image_path="photo_001.jpg",
        operation="resize_thumbnail"
    )
    print(f"   ✓ Enqueued image job: {image_job1.id}")
    
    image_job2 = default_queue.enqueue(
        process_image,
        image_path="photo_002.jpg",
        operation="apply_filter"
    )
    print(f"   ✓ Enqueued image job: {image_job2.id}")
    
    # 3. Enqueue report generation (low priority)
    print("\n[3] Enqueueing LOW PRIORITY report generation...")
    report_job = low_priority_queue.enqueue(
        generate_report,
        report_type="monthly_sales",
        data_source="database"
    )
    print(f"   ✓ Enqueued report job: {report_job.id}")
    
    # 4. Enqueue tasks with retry logic
    print("\n[4] Enqueueing UNRELIABLE tasks (with retry)...")
    retry_job = default_queue.enqueue(
        unreliable_task,
        task_id=101,
        failure_rate=0.7,
        retry=Retry(max=3, interval=[1, 2, 3])  # Retry up to 3 times with backoff
    )
    print(f"   ✓ Enqueued unreliable job with retry: {retry_job.id}")
    
    # 5. Enqueue a workflow of dependent tasks
    print("\n[5] Enqueueing WORKFLOW tasks...")
    workflow_jobs = []
    for i, step in enumerate(["validate_data", "transform_data", "load_data"]):
        job = default_queue.enqueue(
            task_with_dependencies,
            step=step,
            wait_time=1
        )
        workflow_jobs.append(job)
        print(f"   ✓ Enqueued workflow step {i+1}: {job.id}")
    
    # 6. Schedule a delayed task
    print("\n[6] Scheduling DELAYED task (5 seconds from now)...")
    import datetime
    delayed_job = default_queue.enqueue_in(
        datetime.timedelta(seconds=5),
        send_email,
        to_email="scheduled@example.com",
        subject="Scheduled Email",
        body="This email was scheduled 5 seconds ago"
    )
    print(f"   ✓ Scheduled delayed job: {delayed_job.id}")
    
    print("\n" + "=" * 70)
    print("All tasks enqueued successfully!")
    print("=" * 70)
    
    # Return job IDs for monitoring
    return {
        'email_jobs': [email_job1.id, email_job2.id],
        'image_jobs': [image_job1.id, image_job2.id],
        'report_job': report_job.id,
        'retry_job': retry_job.id,
        'workflow_jobs': [j.id for j in workflow_jobs],
        'delayed_job': delayed_job.id
    }


# ============================================================================
# CONSUMER - Worker that processes tasks
# ============================================================================

def start_worker(queue_names=['high', 'default', 'low']):
    """
    Start an RQ worker to process tasks.
    Workers process tasks in the order of queue priority.
    
    In production, you'd run this in a separate process:
    $ rq worker high default low
    """
    redis_host = os.getenv('REDIS_HOST', 'localhost')
    redis_conn = redis.Redis(host=redis_host, port=6379, db=0, decode_responses=True)
    
    print("=" * 70)
    print("RQ WORKER - Starting Background Task Consumer")
    print("=" * 70)
    print(f"Listening on queues: {queue_names}")
    print("Worker is ready to process jobs...")
    print("=" * 70)
    
    # Create worker
    worker = Worker(queue_names, connection=redis_conn)
    
    # Start processing jobs
    worker.work(with_scheduler=True)  # with_scheduler enables delayed jobs


# ============================================================================
# MONITORING - Check job status and results
# ============================================================================

def monitor_jobs(job_ids_dict: dict):
    """
    Monitor the status of enqueued jobs.
    This demonstrates how to check job progress in a web application.
    """
    redis_host = os.getenv('REDIS_HOST', 'localhost')
    # Note: Don't use decode_responses=True when fetching jobs (RQ expects binary data)
    redis_conn = redis.Redis(host=redis_host, port=6379, db=0)
    
    print("\n" + "=" * 70)
    print("JOB MONITORING - Checking Status")
    print("=" * 70)
    
    # Wait a bit for some jobs to start processing
    time.sleep(1)
    
    all_job_ids = []
    for category, ids in job_ids_dict.items():
        if isinstance(ids, list):
            all_job_ids.extend(ids)
        else:
            all_job_ids.append(ids)
    
    for job_id in all_job_ids:
        try:
            job = Job.fetch(job_id, connection=redis_conn)
            
            status_emoji = {
                'queued': '⏳',
                'started': '🔄',
                'finished': '✅',
                'failed': '❌',
                'deferred': '⏸️',
                'scheduled': '📅'
            }
            
            emoji = status_emoji.get(job.get_status(), '❓')
            print(f"\n{emoji} Job ID: {job_id}")
            print(f"   Function: {job.func_name}")
            print(f"   Status: {job.get_status()}")
            print(f"   Enqueued at: {job.enqueued_at}")
            
            if job.is_finished:
                print(f"   Result: {job.result}")
            elif job.is_failed:
                print(f"   Error: {job.exc_info}")
            
        except Exception as e:
            print(f"\n❌ Job ID: {job_id}")
            print(f"   Error fetching job: {e}")
    
    # Show queue statistics
    print("\n" + "=" * 70)
    print("QUEUE STATISTICS")
    print("=" * 70)
    
    for queue_name in ['high', 'default', 'low']:
        queue = Queue(queue_name, connection=redis_conn)
        print(f"\n{queue_name.upper()} Queue:")
        print(f"   Jobs in queue: {len(queue)}")
        print(f"   Failed jobs: {len(FailedJobRegistry(queue=queue))}")
        print(f"   Finished jobs: {len(FinishedJobRegistry(queue=queue))}")
        print(f"   Started jobs: {len(StartedJobRegistry(queue=queue))}")


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def cleanup_redis():
    """Clean up all Redis queues (useful for testing)."""
    redis_host = os.getenv('REDIS_HOST', 'localhost')
    redis_conn = redis.Redis(host=redis_host, port=6379, db=0)
    
    for queue_name in ['high', 'default', 'low']:
        queue = Queue(queue_name, connection=redis_conn)
        queue.empty()
        print(f"Cleared {queue_name} queue")
    
    # Clear registries
    for queue_name in ['high', 'default', 'low']:
        queue = Queue(queue_name, connection=redis_conn)
        FailedJobRegistry(queue=queue).cleanup()
        print(f"Cleaned up {queue_name} failed registry")


# ============================================================================
# MAIN DEMONSTRATION
# ============================================================================

def main():
    """
    Main demonstration function.
    
    To run this example properly:
    1. Start Redis: docker compose up -d
    2. In one terminal, start the worker: python rq_example.py worker
    3. In another terminal, enqueue tasks: python rq_example.py producer
    4. To monitor jobs: python rq_example.py monitor
    """
    import sys
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == 'worker':
            # Start worker to process tasks
            start_worker()
        
        elif command == 'producer':
            # Enqueue tasks
            job_ids = enqueue_tasks()
            print("\nWaiting 2 seconds before monitoring...")
            time.sleep(2)
            monitor_jobs(job_ids)
        
        elif command == 'monitor':
            # Monitor existing jobs (you need to modify this to pass actual job IDs)
            print("Monitoring requires job IDs from a previous producer run.")
            print("Run 'python rq_example.py producer' first.")
        
        elif command == 'cleanup':
            # Clean up queues
            cleanup_redis()
        
        else:
            print(f"Unknown command: {command}")
            print_usage()
    else:
        print_usage()


def print_usage():
    """Print usage instructions."""
    print("""
RQ (Redis Queue) Example Usage:

Prerequisites:
  1. Start Redis:
     docker compose up -dcd

Commands:
  python rq_example.py worker     # Start a worker to process tasks
  python rq_example.py producer   # Enqueue sample tasks
  python rq_example.py cleanup    # Clean up all queues

Typical workflow:
  1. Terminal 1: python rq_example.py worker
  2. Terminal 2: python rq_example.py producer
  
Alternative - Using RQ CLI:
  rq worker high default low      # Start worker using RQ's CLI
  rq info                         # Show queue statistics
  rq info --interval 1            # Live monitoring
  
For more information, see the README.md file.
    """)


if __name__ == "__main__":
    main()

