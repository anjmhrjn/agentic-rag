---
doc_id: KB-055
doc_type:
  - operations
service: internal-analytics
date: 2024-09-30
---
### KB-055: Postmortem: VPC Peering Disruption during Network Maintenance
**Incident ID:** #2024-09-30 | **Impact:** High | **Service:** Internal Analytics

#### Incident Summary

A routine security group update to the Data Subnet (KB-007) accidentally severed the connection between the Analytics VPC and the Production RDS VPC, stopping all real-time financial reporting.

#### What Went Wrong

The Terraform script (KB-020) used a hard-coded CIDR block that did not account for the overlapping address space introduced by a recent VPC peering expansion.

#### Decisions &amp; Reasoning

- **Decision:** Replace hard-coded CIDRs with "Security Group Referencing".
- **Reasoning:** Hard-coding IP ranges is brittle and leads to the "Configuration Drift" seen here. By allowing ingress from sg-analytics-worker instead of 10.0.5.0/24, the network remains secure even if the underlying IP ranges change, reducing the maintenance burden and preventing human-error outages.