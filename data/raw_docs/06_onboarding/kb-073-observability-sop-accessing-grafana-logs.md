---
doc_id: KB-073
doc_type:
  - process
  - reference
service: observability
date: null
---
### KB-073: Observability SOP: Accessing Grafana and Logs
#### Purpose

Guidelines for using the monitoring stack defined in KB-013 to verify system health.

#### Common Workflows

- **Health Check:** Access the "Global Retail Overview" dashboard in Grafana.
- **Log Investigation:** Use OpenSearch Dashboards (Kibana) to search for trace\_id or user\_email.
- **Tracing:** Use Jaeger to visualize the latency of a specific checkout transaction.

#### Decisions &amp; Reasoning

- **Decision:** Every dashboard must include a "How to Read" panel.
- **Reasoning:** A complex graph is useless if a new engineer doesn't know what a "spike" means. Documentation within the tool ensures that the knowledge base remains relevant even when the engineer is looking at live data.
- **Decision:** Standardizing on correlation\_id across all logs.
- **Reasoning:** In a microservices stack, a single user request hits five different services. Without a shared ID, it is impossible to reconstruct the story of a failure. A correlation\_id allows us to "grep" the entire stack for a single event, reducing MTTR by 60-70%.