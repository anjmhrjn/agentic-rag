---
doc_id: KB-061
doc_type:
  - postmortem
  - incident
service: operations
date: 2024-06-20
---
### KB-061: Postmortem: Unverified Runbook Command Error
**Incident ID:** #2024-06-20 | **Impact:** Medium | **Service:** Operations

#### Incident Summary

An engineer executing a "Disk Cleanup" runbook accidentally ran rm -rf /var/lib/docker on a production EKS node, causing all pods on that node to terminate.

#### Decisions &amp; Reasoning

- **Decision:** Replace "Free-text Commands" with "Restricted Scripting" in runbooks.
- **Reasoning:** Human error in copy-pasting commands is inevitable. By packaging cleanup tasks into versioned shell scripts (e.g., ./cleanup-logs.sh) that include safety checks (e.g., if node == production then prompt), we reduce the risk of catastrophic manual errors.