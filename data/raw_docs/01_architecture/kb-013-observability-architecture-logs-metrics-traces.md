---
doc_id: KB-013
doc_type:
  - architecture
  - process
service: cloud-retail
date: 2024-03-15
---
### KB-013: Observability Architecture: Logs, Metrics, and Traces
#### Purpose

Provides a blueprint for how we monitor the health and performance of the Cloud Retail stack.

#### Architecture Description

The architecture follows the "Three Pillars of Observability":

1. **Metrics (Prometheus):** Numerical data tracking system health (CPU, Memory, Request Rate).
2. **Logs (Fluent-bit/OpenSearch):** Textual records of specific events for forensic analysis.
3. **Traces (Jaeger/OpenTelemetry):** Visual maps of how a single request travels through multiple microservices.

#### Decisions &amp; Reasoning

- **Decision:** Standardizing on OpenTelemetry (OTel) for instrumentation.
- **Reasoning:** Proprietary monitoring agents lock the organization into a single vendor's ecosystem. OTel is an open standard that allows us to swap our backend (e.g., moving from Datadog to an open-source Grafana stack) without ever changing a single line of application code. This "Vendor Agnosticism" protects the long-term flexibility of the platform.
- **Decision:** Metrics are prioritised over Logs for initial alerting.
- **Reasoning:** Logs are expensive to store and slow to query at scale. Metrics are lightweight and provide near-instant feedback. By alerting on "Error Rate %" (Metric) rather than "Error String" (Log), we can detect outages in seconds rather than minutes, directly improving our Mean Time to Detect (MTTD).