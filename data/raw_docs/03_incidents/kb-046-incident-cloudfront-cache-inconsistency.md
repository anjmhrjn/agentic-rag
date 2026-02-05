---
doc_id: KB-046
doc_type:
  - incident
  - runbook
service: cloudfront
date: 2024-03-15
---
### KB-046: Incident Response: CloudFront Cache Inconsistency
#### Symptoms and Alerts

- **Symptoms:** Users in Europe see "Version A" of the site, while US users see "Version B."
- **Root Cause:** The CDN (KB-034) has stale versions of the assets in some edge locations.

#### Resolution Steps

1. **Validate Origin:** Confirm the S3 bucket contains the correct latest version of the file.
2. **Create Invalidation:** Execute a global invalidation for the affected paths (SOP KB-034).
3. **Check Edge Status:** Use a "CDN Checker" tool to verify the headers from multiple global IP addresses.

#### Decisions &amp; Reasoning

- **Decision:** Use of "File Versioning" (e.g., app.v123.js) rather than just invalidating app.js.
- **Reasoning:** Cache invalidation can take 5–15 minutes to propagate globally. By changing the *filename* itself, we bypass the cache entirely and force the browser to fetch the new file immediately. This is the most reliable way to ensure 100% version consistency during a deployment.