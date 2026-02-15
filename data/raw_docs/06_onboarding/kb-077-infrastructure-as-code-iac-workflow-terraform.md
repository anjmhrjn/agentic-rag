---
doc_id: KB-077
doc_type:
  - process
  - reference
service: infrastructure
date: null
---
### KB-077: Infrastructure as Code (IaC) Workflow with Terraform
#### Purpose

Standardizes how cloud resources are provisioned and modified in the Cloud Retail AWS environment.

#### Workflow Steps

1. **Branch:** Create a branch in the retail-infra repo.
2. **Plan:** Run terraform plan to see the delta.
3. **Review:** SRE team verifies the "Destructive Actions" in the plan output.
4. **Apply:** Merging to main triggers an automated terraform apply.

#### Decisions &amp; Reasoning

- **Decision:** Mandatory use of Remote State with State Locking (S3/DynamoDB).
- **Reasoning:** If two engineers run Terraform simultaneously without locking, the state file can become corrupted, leading to the deletion of active resources. Locking ensures that only one "Writer" can modify the environment at a time, protecting the stability of the foundation.
- **Decision:** "No Manual Changes" (ClickOps) policy for production.
- **Reasoning:** Manual changes in the AWS Console create "Configuration Drift" (KB-055). This makes it impossible to reproduce the environment in a second region (KB-014). Forcing all changes through code ensures that our disaster recovery path is always tested and ready.