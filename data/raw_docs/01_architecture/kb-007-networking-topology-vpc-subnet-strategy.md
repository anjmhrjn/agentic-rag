---
doc_id: KB-007
doc_type:
  - architecture
  - standard
service: cloud-retail
date: 2024-03-15
---
### KB-007: Networking Topology: VPC and Subnet Strategy
#### Purpose

Details the structural constraints of the network to ensure secure and efficient communication.

#### Layout Description

The system operates within a Virtual Private Cloud (VPC) divided into three tiers:

1. **Public Subnets:** Housing Load Balancers and NAT Gateways.
2. **Private Subnets:** Housing the EKS Worker Nodes (Microservices).
3. **Data Subnets:** Isolated subnets for RDS and Cache layers, with no direct internet egress.

#### Decisions &amp; Reasoning

- **Decision:** Placement of Databases in "Data Subnets" with no direct internet access.
- **Reasoning:** This "Defense in Depth" strategy ensures that even if a microservice is compromised, the database is not directly reachable from the internet. Attackers would need to perform complex lateral movement, providing more time for security teams to detect and remediate the breach.