## What is Structured Logging?

Traditional logging writes plain text strings, which are easy for humans to read but difficult for machines to parse. Structured logging, on the other hand, writes logs in a consistent, machine-readable format like JSON.

- **Traditional Log:** `ERROR: User 123 failed to update profile from IP 192.168.1.10.`
- **Structured Log (JSON):**
  ```json
  {
    "timestamp": "2025-10-09T16:25:18Z",
    "level": "ERROR",
    "message": "User profile update failed",
    "service": "user-api",
    "details": {
      "user_id": 123,
      "source_ip": "192.168.1.10",
      "reason": "Database connection timeout"
    }
  }
  ```

The key advantage is that you can easily **filter, search, and visualize** your logs. For example, you can query for all `ERROR` level logs for `user_id: 123` or create a dashboard showing the rate of database timeouts.

---

## Key Principles for Effective Logging

### 1\. Use Log Levels Wisely

Log levels categorize the severity of an event. They are the primary mechanism for controlling log verbosity between environments.

- **`DEBUG`**: Detailed diagnostic information for developers. Use it to trace variables and code paths. **Enable in development, disable in production.**
- **`INFO`**: High-level events that mark the normal flow of the application (e.g., "Service started," "User logged in"). **Enable in both dev and production.**
- **`WARN`**: Unexpected events that are not critical but should be monitored (e.g., "API response is slow," "Retrying database connection"). **Enable in both dev and production.**
- **`ERROR`**: Serious issues where an operation failed, but the application can continue running (e.g., "Failed to process payment for order 456"). **Always log these.**
- **`FATAL` / `CRITICAL`**: A critical error that will likely cause the application to terminate. **Always log these.**

### 2\. Log the Right Context

A log message without context is useless. Every log entry should be a self-contained event with enough information to understand what happened.

**Always include:**

- **Timestamp**: When the event occurred (use UTC).
- **Log Level**: The severity (`INFO`, `ERROR`, etc.).
- **Service Name**: Which application or microservice produced the log.
- **A clear `message`**: A human-readable description of the event.

**Often include:**

- **Correlation ID** (or Trace ID): A unique ID that tracks a single request as it travels through multiple services. This is **critical** in microservice architectures.
- Relevant business data like `user_id`, `order_id`, or `request_id`.
- Technical context like `hostname`, `source_ip`, or `function_name`.

### 3\. Centralize Your Logs

In production, applications run on multiple servers or containers. Don't log to files on the local disk where they are hard to access. Instead, write logs to standard output (`stdout`) and use a log collector to forward them to a central aggregation service.

Popular log aggregation platforms include the **ELK Stack** (Elasticsearch, Logstash, Kibana), **Splunk**, **Datadog**, and **Grafana Loki**.

### 4\. Never Log Sensitive Information

**NEVER** log sensitive data in plain text. This includes:

- Passwords, API keys, and tokens
- Personally Identifiable Information (PII) like credit card numbers, social security numbers, or home addresses.

Scrub or redact this data before it is logged.

---

## Implementing for Debugging vs. Production

Your logging configuration should be controlled by environment variables, not hardcoded.

### Development & Debugging Environment

- **Goal**: Maximize developer productivity and ease of debugging.
- **Log Level**: `DEBUG`. You want to see everything.
- **Format**: Human-readable, often with colors and indentation ("pretty-printed").
- **Output**: Console (`stdout`).

### Production Environment

- **Goal**: Performance, cost-efficiency, and robust monitoring & alerting.
- **Log Level**: `INFO` or `WARN`. Logging at the `DEBUG` level in production is too noisy and can be a significant performance and cost drag. You can temporarily change the log level to `DEBUG` to diagnose a live issue if your system supports dynamic configuration.
- **Format**: Machine-readable, single-line JSON.
- **Output**: Console (`stdout`), where it's collected by an agent and shipped to a central log aggregator.
