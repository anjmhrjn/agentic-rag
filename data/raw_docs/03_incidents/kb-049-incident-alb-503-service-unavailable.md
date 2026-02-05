---
doc_id: KB-049
doc_type:
  - incident
  - runbook
service: alb
date: 2024-03-15
---
### KB-049: Incident Response: ALB 503 (Service Unavailable)
#### Symptoms and Alerts

- **Symptoms:** Application Load Balancer returns HTTP 503; users see "Service Temporarily Unavailable."

#### Root Cause Analysis

This occurs when the ALB has no healthy targets in its target group. Either all pods are failing health checks, or the service has scaled to zero.

#### Resolution Steps

1. **Check Target Health:** In the AWS Console, check the "Target Health" status.
2. **Verify Health Check Path:** Confirm that the /health endpoint is returning 200 OK from the pods.
3. **Manual Restart:** If pods are "Unhealthy" but running, restart the deployment (KB-018).
4. **Bypass Security Groups:** Ensure the ALB Security Group is allowed to reach the EKS pods on the application port.

#### Decisions &amp; Reasoning

- **Decision:** Health checks should be "Deep" but "Fast."
- **Reasoning:** A health check that checks the database connection is "Deep" and accurate, but if it takes 10 seconds to run, the ALB might mark the pod as dead during a brief DB hiccup. We implement a 2-second timeout to ensure the ALB reacts quickly to true pod failures without being overly sensitive to transient issues.