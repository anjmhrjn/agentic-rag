---
doc_id: KB-025
doc_type:
  - runbook
  - disaster-recovery
service: cloud-retail
date: 2024-03-15
---
### KB-025: Runbook: Regional Disaster Recovery Failover
#### Objective

To shift 100% of global traffic from the primary AWS region to the secondary region in the event of a catastrophic regional outage.

#### When to Use

Only used when the Primary Region is confirmed to have &gt;50% service degradation as reported by the Health Dashboard.

#### Step-by-Step Instructions

1. **Promote DB:** Move the PostgreSQL Read Replica (KB-014) in the secondary region to "Primary" status.
2. **DNS Shift:** Update the Route 53 Weighted Records to 100 in Region B and 0 in Region A.
3. **Scale Compute:** Manually increase the EKS worker node count (KB-020) to match the primary region's capacity.
4. **Purge Cache:** Invalidate the CloudFront CDN (KB-034) to force users to fetch from the new region.

#### Decisions &amp; Reasoning

- **Decision:** The failover is a "Manual Trigger" rather than fully automated.
- **Reasoning:** Automated DNS failover can trigger "Flapping" (where traffic bounces back and forth during a brief network hiccup). Given the data consistency risks involved in promoting an asynchronous database replica (KB-014), we require a human "Go/No-Go" decision to ensure the failover is truly necessary.
- **Decision:** Use of "Warm Standby" for the database but "Scale-on-Demand" for compute.
- **Reasoning:** Keeping a full-size compute cluster running in a second region 24/7 would double our AWS bill. Databases, however, must be running to receive replication data. This "Hybrid Standby" model optimizes for cost while still meeting our 15-minute RTO (KB-014).