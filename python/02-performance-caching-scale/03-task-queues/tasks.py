#!/usr/bin/env python3
"""
Task definitions for RQ example.

These tasks need to be in a separate importable module (not __main__)
so that RQ workers can properly import and execute them.
"""

import time
import random


def send_email(to_email: str, subject: str, body: str) -> dict:
    """
    Simulates sending an email.
    This is a typical use case for background tasks.
    """
    print(f"[EMAIL] Sending email to {to_email}")
    print(f"[EMAIL] Subject: {subject}")
    
    # Simulate network delay
    time.sleep(2)
    
    print(f"[EMAIL] Email sent successfully to {to_email}")
    return {
        "status": "sent",
        "to": to_email,
        "subject": subject,
        "timestamp": time.time()
    }


def process_image(image_path: str, operation: str) -> dict:
    """
    Simulates image processing (resize, crop, filter, etc.).
    This represents a CPU-intensive background task.
    """
    print(f"[IMAGE] Processing image: {image_path}")
    print(f"[IMAGE] Operation: {operation}")
    
    # Simulate processing time
    time.sleep(3)
    
    result_path = f"processed_{image_path}"
    print(f"[IMAGE] Image processed: {result_path}")
    
    return {
        "status": "success",
        "original": image_path,
        "processed": result_path,
        "operation": operation,
        "size_kb": random.randint(100, 500)
    }


def generate_report(report_type: str, data_source: str) -> dict:
    """
    Simulates generating a complex report.
    May take significant time and should run in background.
    """
    print(f"[REPORT] Generating {report_type} report from {data_source}")
    
    # Simulate report generation
    time.sleep(4)
    
    print(f"[REPORT] Report generated successfully")
    
    return {
        "report_type": report_type,
        "data_source": data_source,
        "status": "completed",
        "rows_processed": random.randint(1000, 10000),
        "download_url": f"/reports/{report_type}_{int(time.time())}.pdf"
    }


def unreliable_task(task_id: int, failure_rate: float = 0.5) -> str:
    """
    Simulates an unreliable task that may fail.
    Used to demonstrate retry mechanism.
    """
    print(f"[UNRELIABLE] Starting task {task_id}")
    time.sleep(1)
    
    if random.random() < failure_rate:
        error_msg = f"Task {task_id} failed randomly (simulated failure)"
        print(f"[UNRELIABLE] ❌ {error_msg}")
        raise Exception(error_msg)
    
    print(f"[UNRELIABLE] ✓ Task {task_id} succeeded")
    return f"Task {task_id} completed successfully"


def task_with_dependencies(step: str, wait_time: int = 2) -> str:
    """
    Simulates a task that could be part of a workflow.
    """
    print(f"[WORKFLOW] Executing step: {step}")
    time.sleep(wait_time)
    print(f"[WORKFLOW] Completed step: {step}")
    return f"Step '{step}' completed"

