---
doc_id: KB-018
doc_type:
  - operations
  - security
service: cloud-retail
date: 2024-03-15
---
### KB-018: Runbook: Rotating Service Account Credentials
#### Objective

To fulfill the 90-day security rotation requirement established in KB-010.

#### Preconditions

- Access to AWS Secrets Manager.
- Permissions to restart pods in the production namespace of EKS.

#### Step-by-Step Instructions

1. **Generate New Secret:** Create a new version of the secret in AWS Secrets Manager with a new password.
2. **Update Deployment:** Trigger a rollout of the microservice to force it to fetch the new secret:
kubectl rollout restart deployment/order-service -n production
3. **Verify Old Secret Invalidation:** After 24 hours, manually disable the old password version in the source database.

#### Validation Steps

1. Check pod logs for "Access Denied" errors:
kubectl logs -l app=order-service -f
2. Confirm successful database connection metrics in Grafana.

#### Decisions &amp; Reasoning

- **Decision:** A 24-hour "Grace Period" between updating the secret and invalidating the old one.
- **Reasoning:** If a legacy background job or an un-restarted pod is still using the old password, immediate invalidation will cause a "Hard Outage." The grace period allows for a safe transition, ensuring all components have successfully migrated before the bridge to the old credential is burnt.