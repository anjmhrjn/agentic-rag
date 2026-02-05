---
doc_id: KB-031
doc_type:
  - runbook
  - networking
service: alb
date: 2024-03-15
---
### KB-031: Runbook: Load Balancer Rule and Routing Updates
#### Objective

To modify the path-based routing rules of the Application Load Balancer (ALB).

#### Preconditions

- Updated target group for the new service (KB-006).

#### Step-by-Step Instructions

1. **Edit Listener:** In the ALB console/Terraform, locate the Listener for port 443.
2. **Add Rule:** Create a new rule: IF Path is /api/v2/* THEN Forward to TargetGroup-v2.
3. **Priority:** Ensure the new rule has a higher priority than the default /api/* catch-all.

#### Decisions &amp; Reasoning

- **Decision:** Use of Path-based routing instead of Host-based routing for internal APIs.
- **Reasoning:** Path-based routing (cloudretail.com/orders) allows us to share a single SSL certificate and IP address across multiple microservices. This reduces networking complexity and cost compared to host-based routing (orders.cloudretail.com), which would require a unique certificate and DNS record for every single component.
- **Decision:** Mandatory "Negative Priority" for catch-all rules.
- **Reasoning:** If the catch-all rule (e.g., /*) has high priority, it will steal traffic from specific service rules. By setting it to the lowest possible priority, we ensure that new services can be safely "carved out" of the traffic flow without impacting existing ones.