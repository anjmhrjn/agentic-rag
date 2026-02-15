---
doc_id: KB-056
doc_type:
  - operations
service: global-traffic-management
date: 2025-05-18
---
### KB-056: Postmortem: Regional Failover Latency Spike
**Incident ID:** #2025-05-18 | **Impact:** High | **Service:** Global Traffic Management

#### Incident Summary

During a regional outage in us-east-1, traffic failover to us-west-2 (KB-025) resulted in a 3.5s latency spike, causing a 40% drop in user conversion for 20 minutes.

#### Timeline of Events

- **12:00 UTC:** Primary region degraded.
- **12:05 UTC:** Route 53 shifts 100% traffic to Region B.
- **12:06 UTC:** Region B compute cluster (EKS) enters CPU saturation as it was only at "Warm Standby" capacity (20% of prod).
- **12:15 UTC:** Autoscaler (KB-015) successfully provisions new nodes.

#### Decisions &amp; Reasoning

- **Decision:** Increase "Warm Standby" minimum capacity to 50% for Region B.
- **Reasoning:** The cost-saving decision to keep Region B at 20% capacity was the root cause of the latency spike. 50% capacity ensures that the system can handle the immediate traffic surge while the Horizontal Pod Autoscaler provisions the remaining 50%.