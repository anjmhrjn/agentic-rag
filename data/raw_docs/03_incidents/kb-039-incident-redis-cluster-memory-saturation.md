---
doc_id: KB-039
doc_type:
  - incident
  - runbook
service: redis
date: 2024-03-15
---
### KB-039: Incident Response: Redis Cluster Memory Saturation
#### Symptoms and Alerts

- **Alert:** redis\_memory\_usage\_high (&gt;95%).
- **Symptoms:** Application latency increases; logs show OOM command not allowed.

#### Root Cause Analysis

Likely due to an unexpected surge in session data or a failure of the eviction policy (KB-012) to clear enough space for new keys.

#### Resolution Steps

1. **Identify Large Keys:** Run redis-cli --bigkeys to find if a single key is consuming excessive memory.
2. **Manual Flush (Emergency):** If non-critical cache is the culprit, flush the cache (SOP KB-030).
3. **Scaling:** Increase the node type in ElastiCache to provide more RAM.
4. **Policy Check:** Verify that the maxmemory-policy is still set to volatile-lru.

#### Decisions &amp; Reasoning

- **Decision:** Vertical scaling (more RAM) is preferred over horizontal scaling (more shards) for immediate relief.
- **Reasoning:** Resharding a Redis cluster is a heavy operation that can cause a temporary latency spike. Vertical scaling of the underlying instance is faster and ensures that all existing data remains available without relocation overhead.
- **Decision:** Using volatile-lru as a safety guard.
- **Reasoning:** If memory hits 100%, Redis must decide what to kill. By targeting only keys with a TTL, we protect our core configuration data from being deleted, which could cause a catastrophic "System-Wide Configuration Loss" incident.