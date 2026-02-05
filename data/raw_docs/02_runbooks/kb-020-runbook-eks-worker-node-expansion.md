---
doc_id: KB-020
doc_type:
  - runbook
  - infrastructure
service: eks
date: 2024-03-15
---
### KB-020: Runbook: EKS Worker Node Expansion
#### Objective

Manually expanding the compute cluster when the autoscaler (KB-015) reaches its limit.

#### Preconditions

- terraform installed and initialized.
- AWS IAM permissions for EKS:UpdateNodegroupConfig.

#### Instructions

1. Open the variables.tf file for the infrastructure-as-code repo.
2. Increase the node\_group\_max\_size from (e.g.) 10 to 15.
3. Run terraform plan to verify the change.
4. Run terraform apply.

#### Validation Steps

1. Verify new nodes are "Ready":
kubectl get nodes
2. Check that "Pending" pods are now "Running."

#### Decisions &amp; Reasoning

- **Decision:** Use of Infrastructure as Code (Terraform) rather than the AWS Console.
- **Reasoning:** Manual changes in the console create "Configuration Drift." If someone later runs a terraform deployment, it might undo the manual scaling, causing a sudden and unexplained capacity drop. By making scaling changes in code, we ensure that the "Source of Truth" remains synchronized with reality.