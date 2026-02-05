---
doc_id: KB-058
doc_type:
  - postmortem
  - incident
service: deployment-pipeline
date: 2025-03-22
---
### KB-058: Postmortem: CI/CD Pipeline Contention Outage
**Incident ID:** #2025-03-22 | **Impact:** Low | **Service:** Deployment Pipeline

#### Incident Summary

Two separate feature teams attempted to deploy changes to the Load Balancer (KB-031) simultaneously. This resulted in a Terraform state lock that blocked all deployments for 2 hours.

#### Decisions &amp; Reasoning

- **Decision:** Transition to "Modular Terraform State" (One state file per service).
- **Reasoning:** Using a single "Global" state file creates a bottleneck. By splitting the state by service domain (e.g., networking-state, database-state), teams can deploy independently without locking each other out.