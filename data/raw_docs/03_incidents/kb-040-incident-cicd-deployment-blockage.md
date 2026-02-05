---
doc_id: KB-040
doc_type:
  - incident
  - runbook
service: cicd
date: 2024-03-15
---
### KB-040: Incident Response: CI/CD Pipeline Deployment Blockage
#### Symptoms and Alerts

- **Symptoms:** GitHub Actions (KB-019) fail consistently during the "Apply" phase; no code is reaching Staging or Production.

#### Impact Assessment

High for Development Velocity. Engineers are unable to ship critical bug fixes or features.

#### Resolution Steps

1. **Check Cloud Provider Health:** Verify AWS EKS API status.
2. **Credential Audit:** Check if the CI/CD service account token has expired (KB-026).
3. **State Lock Clearing:** If using Terraform, check for a "State Lock." If a previous job crashed, the lock might need manual removal: terraform force-unlock &lt;lock-id&gt;
4. **Bypass Deploy:** If an emergency fix is needed, perform a manual deployment from the Bastion host following SOP KB-016.

#### Decisions &amp; Reasoning

- **Decision:** Mandatory use of "State Locking" in the S3 backend.
- **Reasoning:** Without locking, two concurrent CI jobs could try to modify the same resource simultaneously, leading to "Resource Corruption." While locks occasionally get stuck (causing this incident), they are a necessary evil to prevent permanent infrastructure damage.
- **Decision:** Manual deployment requires a secondary "Peer Approval" in Slack.
- **Reasoning:** Manual actions bypass the safety checks of the CI/CD pipeline. To prevent human error, a second pair of eyes must confirm the commands being run on the Bastion host.