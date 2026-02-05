---
doc_id: KB-012
doc_type:
  - architecture
  - standard
service: cloud-retail
date: 2024-03-15
---
### KB-012: Caching Layer: Redis Integration and Eviction Policies
#### Purpose

Details the performance-tier storage used to reduce latency for the components described in KB-009.

#### Architecture Description

We utilize Amazon ElastiCache (Redis) as a distributed, in-memory cache for frequently accessed, non-authoritative data, such as product catalog metadata and user session tokens.

#### Decisions &amp; Reasoning

- **Decision:** Use of the volatile-lru (Least Recently Used) eviction policy.
- **Reasoning:** In an e-commerce environment, some products are "viral" while others are rarely viewed. An LRU policy automatically clears out items that haven't been accessed recently to make room for new high-traffic items. By specifying volatile-lru, we ensure that only keys with an expiration time (TTL) are evicted, protecting "permanent" configuration data from being accidentally deleted when memory is tight.
- **Decision:** Mandatory Time-To-Live (TTL) of 60 minutes for all product metadata.
- **Reasoning:** Caching improves speed but introduces "Stale Data" risk. A 60-minute TTL balances performance with accuracy; it ensures that if an inventory count changes in the PostgreSQL source (KB-008), the frontend (KB-006) will be inconsistent for no more than one hour, which is an acceptable business trade-off for the 10x gain in page load speed.