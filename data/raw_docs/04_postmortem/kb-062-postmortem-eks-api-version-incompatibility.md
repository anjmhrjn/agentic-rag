---
doc_id: KB-062
doc_type:
  - postmortem
  - incident
service: orchestration-layer
date: 2025-04-05
---
### KB-062: Postmortem: EKS API Version Incompatibility
**Incident ID:** #2025-04-05 | **Impact:** High | **Service:** Orchestration Layer

#### Incident Summary

Updating the EKS Control Plane to version 1.29 (KB-024) caused the Order Service to stop scaling. The root cause was the removal of the v1beta1 HorizontalPodAutoscaler API.

#### Decisions &amp; Reasoning

- **Decision:** Mandatory "API Deprecation Scan" in Staging.
- **Reasoning:** Kubernetes upgrades frequently remove old APIs. We now use pluto or kubent to scan our Helm charts (KB-022) for deprecated versions before any production upgrade is scheduled.