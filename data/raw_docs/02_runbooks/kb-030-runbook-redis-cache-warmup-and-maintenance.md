---
doc_id: KB-030
doc_type:
  - runbook
  - performance
service: redis
date: 2024-03-15
---
### KB-030: Runbook: Redis Cache Warm-up and Maintenance
#### Objective

To manage the performance-tier storage (KB-012) during scaling events or cluster restarts.

#### When to Use

Use this after a Redis cluster maintenance window or a regional failover (KB-025).

#### Instructions

1. **Identify High-Value Keys:** Use the redis-cli --bigkeys command to identify the top 100 most-accessed items.
2. **Execute Warm-up Script:** Run the Python utility cache\_warmer.py to pre-load these items from the PostgreSQL database.
3. **Monitor Latency:** Observe the Application Load Balancer TargetResponseTime to ensure it stays &lt;200ms.

#### Decisions &amp; Reasoning

- **Decision:** Implementing an active "Warm-up" script rather than a "Cold Start."
- **Reasoning:** A "Cold Start" (empty cache) causes a "Thundering Herd" problem. Thousands of users hit the Order Service simultaneously, which then hits the PostgreSQL database (KB-008). This can overwhelm the database and cause a secondary outage. Pre-loading the top 100 keys prevents this spike, ensuring a smooth transition during maintenance.
- **Decision:** Use of a dedicated warm-up service account.
- **Reasoning:** This allows us to track warm-up traffic separately from real user traffic in our logs (KB-013), making it easier to see if the maintenance process itself is causing system strain.