---
doc_id: KB-011
doc_type:
  - architecture
  - concept
service: cloud-retail
date: 2024-03-15
---
### KB-011: Data Partitioning and Sharding Strategies
#### Purpose

Explains how the "Cloud Retail" stack manages large-scale data growth within the persistence layer defined in KB-008.

#### Architecture Description

As the Inventory and Order databases grow, a single PostgreSQL instance eventually hits I/O and CPU limits. We implement **Horizontal Partitioning (Sharding)** for the Orders table, splitting data across multiple database nodes based on a tenant\_id or customer\_id hash.

#### Decisions &amp; Reasoning

- **Decision:** Use Hash-based Sharding rather than Range-based Sharding.
- **Reasoning:** Range-based sharding (e.g., by date) often creates "hot shards"—where the most recent month's shard receives 90% of the traffic while older shards sit idle. Hash-based sharding ensures a statistically even distribution of writes across all nodes, preventing any single database server from becoming a performance bottleneck during peak sales events.
- **Decision:** Application-level sharding logic is abstracted through a "Data Access Layer" (DAL).
- **Reasoning:** Hard-coding shard locations into microservices makes the system brittle. By using a DAL, we can re-balance shards or add new nodes without modifying the core business logic of the Order Service (KB-006), significantly reducing the risk of regression during infrastructure expansion.