---
doc_id: KB-060
doc_type:
  - postmortem
  - incident
service: cache-layer
date: 2025-01-14
---
### KB-060: Postmortem: Redis Cold-Start Thundering Herd
**Incident ID:** #2025-01-14 | **Impact:** Medium | **Service:** Cache Layer

#### Incident Summary

Following a Redis cluster upgrade, the system restarted with an empty cache. The resulting 15,000 concurrent SQL queries overwhelmed the Inventory Database, causing a 10-minute platform outage.

#### Decisions &amp; Reasoning

- **Decision:** Mandatory use of the "Cache Warm-up SOP" (KB-030).
- **Reasoning:** High-traffic systems cannot survive a "Cold Start." Pre-loading the top 1% of products into memory before enabling user traffic reduces the DB load by 90% during recovery.