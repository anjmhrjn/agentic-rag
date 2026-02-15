---
doc_id: KB-052
doc_type:
  - operations
service: catalog-service
date: 2025-11-27
---
### KB-052: Postmortem: Black Friday Redis Cache Exhaustion
**Incident ID:** #2025-11-27 | **Impact:** High | **Service:** Catalog Service

#### Incident Summary

During the Black Friday peak traffic window, the Redis cluster (KB-012) reached 100% memory saturation, leading to a "Thundering Herd" effect on the Inventory Database (KB-008).

#### Timeline of Events

- **08:00 UTC:** Traffic spikes to 15x baseline.
- **08:12 UTC:** Redis memory hits 98%.
- **08:15 UTC:** Eviction policy begins dropping "permanent" configuration keys because they lacked a TTL.
- **08:20 UTC:** Catalog service latency spikes from 100ms to 4.5s.
- **09:00 UTC:** Redis cluster scaled vertically (KB-017) and keys re-warmed (KB-030).

#### What Went Wrong

The Redis cluster was misconfigured with the allkeys-lru eviction policy instead of volatile-lru. This caused the system to delete critical, long-lived application settings when it should have only deleted session-based cache.

#### Decisions &amp; Reasoning

- **Decision:** Standardize on volatile-lru for all production ElastiCache instances.
- **Reasoning:** Our architecture mixes two types of data: disposable transient cache and semi-permanent config data. allkeys-lru is dangerous because it treats all data as equally disposable. volatile-lru protects keys without a TTL, ensuring that "System Settings" are never evicted to make room for temporary product views.
- **Decision:** Implement "Cache Reservation" alerts at 75% memory usage.
- **Reasoning:** Alerting at 95% left no time for vertical scaling, which takes ~10 minutes. 75% provides the necessary lead time for the platform team to intervene before the eviction policy triggers.