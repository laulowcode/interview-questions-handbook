Monitoring and observability are related but distinct concepts for understanding a system's health and performance. **Monitoring** is about collecting and analyzing predefined sets of data (metrics) to see if a system is working as expected. **Observability**, on the other hand, is about being able to understand the internal state of a system just by observing its external outputs, allowing you to ask new questions about its behavior without needing to ship new code.

---
## Metrics (Prometheus) 📊

Metrics are numerical measurements of a system's behavior over time. They are excellent for dashboards, alerting, and understanding trends. **Prometheus** is a leading open-source tool for collecting and storing these time-series metrics.

* **How it Works**: Prometheus operates on a **pull model**. The central Prometheus server periodically scrapes (fetches) metrics from specified endpoints on your applications, called `/metrics` endpoints. Applications expose their current metrics on this endpoint using a specific format.
* **Key Metric Types**:
    * **Counter**: A cumulative metric that only ever increases or resets to zero (e.g., number of HTTP requests served).
    * **Gauge**: A value that can go up or down (e.g., current memory usage, number of active connections).
    * **Histogram**: Samples observations (like request durations) and counts them in configurable buckets. It also provides a sum of all observed values. This is great for calculating quantiles (e.g., the 95th percentile latency).
    * **Summary**: Similar to a histogram, it also samples observations but calculates configurable quantiles on the client side before exposing them to Prometheus.



---
## Tracing (OpenTelemetry) 🔍

While metrics tell you *what* is happening, distributed **tracing** tells you *why*. It tracks the journey of a single request as it travels through multiple services in a microservices architecture. This is crucial for pinpointing bottlenecks and errors in complex systems.

**OpenTelemetry (OTel)** is an open-source observability framework that standardizes how you collect and export telemetry data (traces, metrics, and logs). It provides APIs and SDKs for instrumenting your code.

* **Core Concepts**:
    * **Span**: The basic building block of a trace. It represents a single unit of work within a service, like an API call or a database query. It includes a name, start/end timestamps, and other metadata (attributes).
    * **Trace**: A collection of spans that represent the entire lifecycle of a request as it moves through the system. Spans are linked together in a parent-child relationship, forming a tree-like structure that visualizes the request flow.

When a request starts, a unique trace ID is generated. This ID is passed along in the request headers to every service it touches, allowing each service to add its own spans to the overall trace.



---
## Health Checks 🩺

Health checks are simple endpoints that report the status of an application or service. They are essential for automated systems, like orchestrators (e.g., Kubernetes) or load balancers, to know whether to send traffic to an instance or restart it.

* **Liveness Probe**: Answers the question, "Is the application running?" If this check fails, the orchestrator assumes the application is deadlocked or frozen and will restart it to attempt recovery.
* **Readiness Probe**: Answers the question, "Is the application ready to serve traffic?" An application might be running (live) but not yet ready, perhaps because it's still initializing or connecting to a database. If the readiness probe fails, the orchestrator will stop sending traffic to it until it becomes ready.

---
## Understanding the Setup

In a modern, observable system, these three components work together to provide a complete picture of system health.

1.  **Instrumentation**: Your application code is instrumented using an OpenTelemetry SDK. This code creates spans for important operations (e.g., incoming HTTP requests, database queries) to generate trace data. The same SDK can also be used to expose custom business metrics. Many libraries and frameworks also expose default metrics (like CPU or memory usage) automatically.

2.  **Data Collection & Exposure**:
    * **Metrics**: The application exposes a `/metrics` endpoint. The Prometheus server is configured to periodically scrape this endpoint to collect the latest metric values.
    * **Traces**: The OpenTelemetry SDK sends trace data (spans) from the application to an **OpenTelemetry Collector**. The collector can process and then forward this data to a tracing backend like Jaeger or Zipkin for storage and visualization.
    * **Health Checks**: The application exposes simple HTTP endpoints like `/health/live` and `/health/ready`.

3.  **Analysis & Action**:
    * **Orchestrator (e.g., Kubernetes)**: It continuously pings the health check endpoints. If a liveness probe fails, it restarts the container. If a readiness probe fails, it removes the container from the service's load balancing pool.
    * **Monitoring System (e.g., Prometheus + Grafana)**: Prometheus stores the metrics and uses them to power dashboards in Grafana, a visualization tool. Alerting rules are set up in Prometheus to notify engineers when a metric crosses a critical threshold (e.g., error rate is too high).
    * **Tracing Backend (e.g., Jaeger)**: When an alert fires or a user reports an issue, an engineer can look up the corresponding trace in Jaeger to see the exact path of a failed or slow request, quickly identifying which service or database call caused the problem.

This setup creates a powerful feedback loop: **Health checks** keep the system running automatically, **metrics and alerts** notify you of problems, and **traces** give you the deep context needed to debug them efficiently.