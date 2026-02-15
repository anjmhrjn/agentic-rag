---
doc_id: KB-063
doc_type:
  - operations
service: network
date: 2024-10-09
---
### KB-063: Postmortem: Stale DNS Resolution Failures
**Incident ID:** #2024-10-09 | **Impact:** Medium | **Service:** Network

#### Incident Summary

After shifting traffic between AWS regions (KB-025), 15% of users continued to hit the "Down" region for over 2 hours due to deep ISP-level DNS caching.

#### Decisions &amp; Reasoning

- **Decision:** Reduce DNS TTL (Time-to-Live) to 60 seconds for failover records.
- **Reasoning:** A 1-hour TTL is fine for static sites but deadly for failover. A 60-second TTL forces global resolvers to check for changes frequently, ensuring traffic shifts are respected globally within minutes.