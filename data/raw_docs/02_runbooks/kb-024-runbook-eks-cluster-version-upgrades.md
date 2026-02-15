---
doc_id: KB-024
doc_type:
  - architecture
  - operations
service: eks
date: 2024-03-15
---
### KB-024: Runbook: Amazon EKS Cluster Version Upgrades
#### Objective

To safely update the Kubernetes control plane and worker nodes to a newer minor version (e.g., 1.29 to 1.30).

#### When to Use

Triggered quarterly or when a specific Kubernetes version reaches end-of-life (EOL).

#### Instructions

1. **Control Plane Upgrade:** Run aws eks update-cluster-version for the master nodes.
2. **Node Group Rollout:** Create a new "Blue" node group with the updated version.
3. **Taint and Drain:** Mark the old "Green" nodes as unschedulable:
kubectl drain &lt;node-name&gt; --ignore-daemonsets
4. **Decommission:** Once all pods have migrated, delete the old node group.

#### Decisions &amp; Reasoning

- **Decision:** Using "Blue/Green" node groups rather than in-place upgrades.
- **Reasoning:** In-place upgrades of worker node AMIs are risky; if a node fails to reboot, capacity drops immediately. By spinning up a completely new node group first, we ensure we have surplus capacity *before* we start killing old nodes. This "Infrastructure Immobility" approach reduces the risk of a cluster-wide outage during maintenance.
- **Decision:** Mandatory 72-hour soak period in the Staging environment.
- **Reasoning:** Kubernetes upgrades can introduce API deprecations that break specific microservices. A 72-hour window in Staging allows for a full cycle of automated tests and manual verification (KB-005) before we touch the production traffic.