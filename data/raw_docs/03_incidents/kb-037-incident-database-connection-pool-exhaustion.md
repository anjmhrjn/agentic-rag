---
doc_id: KB-037
doc_type:
  - incident
  - runbook
service: postgresql
date: 2024-03-15
---
### KB-037: Incident Response: Database Connection Pool Exhaustion
#### Symptoms and Alerts

- **Alert:** rds\_connection\_count\_high (&gt;90% of max\_connections).
- **Symptoms:** Order Service (KB-006) returns "500 Internal Server Error" with logs stating Too many clients or Connection timed out.

#### Root Cause Analysis

Typically caused by a sudden traffic spike, unoptimized queries holding connections too long, or a "Connection Leak" in the application code where connections are not returned to the pool.

#### Resolution Steps

1. **Identify Top Consumers:** Check RDS Performance Insights to see which microservice is hogging connections.
2. **Emergency Scaling:** Immediately scale the RDS instance class vertically (KB-017) to increase memory and the default connection limit.
3. **Flush Connections:** If a specific node is misbehaving, restart the pod to force a connection reset:
kubectl rollout restart deployment/&lt;service-name&gt;
4. **Application Throttle:** As a last resort, reduce the HPA min-replicas (KB-015) to limit the total number of connection attempts.

#### Decisions &amp; Reasoning

- **Decision:** Prioritize vertical scaling over manually killing SQL sessions.
- **Reasoning:** Killing sessions in a live database can leave orphaned locks or cause data inconsistency. Vertical scaling is a cleaner, safer "Brute Force" method that buys the team time to find the underlying leak without risking data integrity.
- **Decision:** Setting max\_connections to 90% of physical capacity as the alert threshold.
- **Reasoning:** In PostgreSQL, the last 10% of connections should be reserved for administrative access (superusers). Alerting at 90% ensures that SREs can still log in to diagnose the system while it is under duress.