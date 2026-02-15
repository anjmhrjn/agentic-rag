---
doc_id: KB-027
doc_type:
  - operations
service: networking
date: 2024-03-15
---
### KB-027: Runbook: VPC Connectivity and Peering Troubleshooting
#### Objective

To diagnose and repair communication failures between isolated network segments defined in KB-007.

#### Symptoms

Connection Timeout errors between a microservice and the Data Subnet database.

#### Troubleshooting Steps

1. **Check Security Groups:** Verify that the DB Security Group allows ingress on port 5432 from the EKS Worker Node CIDR.
2. **Analyze Flow Logs:** Use CloudWatch to see if traffic is being REJECTED at the network interface.
3. **Test Routing:** Verify the Route Table in the Private Subnet includes a route to the Data Subnet.

#### Decisions &amp; Reasoning

- **Decision:** We use "Explicit Ingress" rules rather than broad CIDR blocks (e.g., 0.0.0.0/0).
- **Reasoning:** Broad rules are a security liability. By explicitly white-listing only the EKS Security Group, we ensure that even if an attacker gains access to the VPC (e.g., via a compromised VPN), they cannot reach the database unless they are coming from a trusted application node.
- **Decision:** Enabling VPC Flow Logs only on "Metadata Mode."
- **Reasoning:** Full packet capture is extremely expensive and generates petabytes of noise. Metadata mode (Source/Dest IP and Port) provides 95% of the troubleshooting value for 1% of the cost.