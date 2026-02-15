---
doc_id: KB-057
doc_type:
  - operations
service: eks-cluster
date: 2024-12-01
---
### KB-057: Postmortem: Worker Node OOM Cascade
**Incident ID:** #2024-12-01 | **Impact:** High | **Service:** EKS Cluster

#### Incident Summary

A memory leak in the Order Service caused individual Kubernetes nodes to reach 100% RAM usage, triggering the Linux OOM Killer. This resulted in a "Cascade" where pods were rescheduled onto healthy nodes, which then also crashed from the sudden load.

#### Root Cause Analysis

The deployment manifest lacked "Memory Requests" and "Limits" (KB-020). Kubernetes was unaware of the service's memory footprint, allowing it to starve the system of resources.

#### Decisions &amp; Reasoning

- **Decision:** Mandatory Resource Quotas for all production namespaces.
- **Reasoning:** Without limits, one "bad neighbor" service can take down the entire cluster. Enforcing strict limits ensures that a leaking pod is killed individually by Kubernetes *before* it impacts the stability of the underlying worker node.