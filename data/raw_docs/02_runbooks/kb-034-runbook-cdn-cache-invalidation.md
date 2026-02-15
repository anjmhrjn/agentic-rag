---
doc_id: KB-034
doc_type:
  - observability
  - operations
service: cloudfront
date: 2024-03-15
---
### KB-034: Runbook: CDN Cache Invalidation
#### Objective

To force the CloudFront Global Network to purge old static assets (KB-009) and fetch the latest versions.

#### When to Use

Used after a frontend "Major" deployment (KB-004) or when an emergency fix is applied to the UI.

#### Instructions

1. **Identify Paths:** Determine the specific files (e.g., /index.html, /assets/js/*).
2. **Invalidate:** Execute aws cloudfront create-invalidation --distribution-id &lt;ID&gt; --paths "/*".
3. **Verify:** Check the invalidation status until it moves from InProgress to Completed.

#### Decisions &amp; Reasoning

- **Decision:** We invalidate specific paths rather than the entire distribution where possible.
- **Reasoning:** Invalidating "everything" (/*) is a massive performance hit. It forces every global user to re-download every asset, spiking our "Origin Transfer" costs. By targeting only the changed paths, we maintain high cache-hit ratios for the rest of the site.
- **Decision:** Mandatory invalidation of index.html on every release.
- **Reasoning:** The index.html file contains the links to the versioned Javascript bundles (e.g., app.v2.js). If the browser keeps a cached index.html, it will try to load app.v1.js, which no longer exists on the server, causing a "White Screen of Death."