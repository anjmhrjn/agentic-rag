---
doc_id: KB-014
doc_type:
  - architecture
  - process
service: cloud-retail
date: 2024-03-15
---
### KB-014: High Availability and Disaster Recovery Strategy
#### Purpose

Defines the technical requirements for keeping the system online during catastrophic failures.

#### Architecture Description

The system employs an **Active-Active** configuration across two AWS Regions (e.g., us-east-1 and us-west-2). Traffic is routed via Route 53 latency-based records.

#### Decisions &amp; Reasoning

- **Decision:** Target Recovery Time Objective (RTO) of 15 minutes.
- **Reasoning:** RTO defines how long the business can tolerate being "down." 15 minutes was chosen because it allows for automated DNS failover and database promotion without requiring manual human intervention for every step, which often takes 60+ minutes under stress.
- **Decision:** Cross-Region Read Replicas for PostgreSQL.
- **Reasoning:** Synchronous replication across regions introduces unacceptable latency (physics limits). By using asynchronous read replicas, we ensure that the secondary region has a near-real-time copy of the data. In a regional disaster, we promote the replica to "Primary." The small risk of "Data Loss" (measured by RPO) is mitigated by our event-driven architecture (KB-009), where lost events can be re-driven from the SQS queue.