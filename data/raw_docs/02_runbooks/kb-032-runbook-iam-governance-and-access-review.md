---
doc_id: KB-032
doc_type:
  - operations
  - security
service: iam
date: 2024-03-15
---
### KB-032: Runbook: IAM Governance and Access Review
#### Objective

To perform the monthly cleanup of identities and permissions to prevent "Privilege Creep."

#### Instructions

1. **Identify Inactivity:** Run aws iam generate-credential-report.
2. **Scan for 90+ Days:** Locate any users or roles that have not been used in 90 days.
3. **Revoke:** Delete the access keys and the IAM user.
4. **Audit Roles:** Ensure no service account has AdministratorAccess.

#### Decisions &amp; Reasoning

- **Decision:** Hard-deletion of users inactive for 90+ days.
- **Reasoning:** Inactive accounts are a prime target for attackers; they are rarely monitored, and a compromise could go unnoticed for months. 90 days is the standard window; if an employee hasn't logged in for a full quarter, their access is no longer "required for their job function."
- **Decision:** No service accounts with "Admin" rights.
- **Reasoning:** If a microservice (KB-006) is compromised, an "Admin" role would give the attacker total control over the entire AWS account. By using scoped permissions (e.g., S3:PutObject only), we limit the "Blast Radius" of a single component breach.