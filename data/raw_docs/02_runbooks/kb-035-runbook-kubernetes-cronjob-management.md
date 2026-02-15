---
doc_id: KB-035
doc_type:
  - architecture
  - operations
service: eks
date: 2024-03-15
---
### KB-035: Runbook: Kubernetes CronJob Management
#### Objective

To schedule and monitor background tasks (e.g., nightly stock reconciliation) in the EKS cluster.

#### Instructions

1. **Define Schedule:** Use the standard Cron syntax (e.g., 0 2 * * * for 2 AM).
2. **Concurrency Policy:** Set concurrencyPolicy: Forbid.
3. **Deployment:** Apply the manifest: kubectl apply -f reconciliation-job.yaml.

#### Decisions &amp; Reasoning

- **Decision:** Use of concurrencyPolicy: Forbid for data-heavy jobs.
- **Reasoning:** If a stock reconciliation job takes 25 hours but runs every 24 hours, an "Allow" policy would result in two jobs running at once. This leads to database deadlocks and inconsistent inventory counts (KB-006). "Forbid" ensures that a new job only starts once the previous one is finished, protecting data integrity.
- **Decision:** Mandatory startingDeadlineSeconds: 600.
- **Reasoning:** If the cluster is under heavy load and cannot provision a pod for the job immediately, this setting allows Kubernetes to "try again" for 10 minutes. Without it, the job might be marked as "Failed" simply because of a temporary resource shortage.