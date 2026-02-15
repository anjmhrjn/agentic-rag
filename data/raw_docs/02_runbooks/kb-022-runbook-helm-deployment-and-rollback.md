---
doc_id: KB-022
doc_type:
  - architecture
  - operations
service: cloud-retail
date: 2024-03-15
---
### KB-022: Runbook: Helm-based Service Deployment and Rollback
#### Objective

To standardize the deployment of microservices into the EKS cluster (KB-006) using Helm as the package manager.

#### When to Use

Standard procedure for all application updates as defined in the versioning rules (KB-004).

#### Step-by-Step Instructions

1. **Package Versioning:** Ensure the Chart.yaml version has been incremented according to SemVer (KB-004).
2. **Deployment:** Execute the upgrade with the atomic flag:
helm upgrade --install order-service./charts/order-service --namespace production --atomic --timeout 5m
3. **Manual Rollback (If needed):** If the release fails health checks (KB-020):
helm rollback order-service 1 --namespace production

#### Decisions &amp; Reasoning

- **Decision:** Mandatory use of the --atomic flag during upgrades.
- **Reasoning:** Without the atomic flag, a failed deployment leaves "half-finished" resources in the cluster (e.g., a service pointing to a non-existent pod). The atomic flag treats the deployment as a single transaction; if the pods do not reach a "Ready" state within the timeout, Helm automatically triggers a rollback. This ensures the production environment is never left in an inconsistent state.
- **Decision:** Deployment timeouts are set to 5 minutes.
- **Reasoning:** A 5-minute window allows sufficient time for the Horizontal Pod Autoscaler (KB-015) to provision new nodes if necessary, without making the CI/CD pipeline feel sluggish. It balances "System Patience" with "Developer Velocity."