---
doc_id: KB-053
doc_type:
  - operations
service: frontend/cloudfront
date: 2025-01-15
---
### KB-053: Postmortem: Inconsistent Catalog via CDN Cache Rot
**Incident ID:** #2025-01-15 | **Impact:** Medium | **Service:** Frontend/CloudFront

#### Incident Summary

Customers in the EMEA region reported seeing "Out of Stock" labels for items that were available in the US region. The root cause was a failure in the CDN invalidation process (KB-034) during a global catalog update.

#### Timeline of Events

- **10:00 UTC:** Global inventory update pushed to S3.
- **10:05 UTC:** Automated invalidation command for /* executed.
- **10:30 UTC:** Regional monitoring shows EMEA edge locations still serving 10:00 version.
- **11:15 UTC:** Manual invalidation of specific file paths executed.

#### What Went Wrong

The generic /* invalidation command hit an AWS rate limit due to concurrent deployments from other teams. This left the EMEA edge caches in a "Stale" state while the US edges were updated.

#### Decisions &amp; Reasoning

- **Decision:** Transition from "Invalidation-by-Path" to "Content-Addressable Filenames" (Versioning).
- **Reasoning:** Invalidations are eventual and prone to rate limits. By appending a hash of the content (e.g., catalog.v123.json), we bypass the cache entirely for new versions. This makes updates instantaneous and deterministic, permanently solving the "Stale Data" problem without relying on CloudFront API availability.