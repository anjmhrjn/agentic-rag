---
doc_id: KB-067
doc_type:
  - onboarding
  - sop
service: security
date: null
---
### KB-067: Access Requirements: Identity and SSO
#### Purpose

Defines the procedures for obtaining and managing access to internal systems following the "Principle of Least Privilege."

#### Provisioning Steps

1. **Identity Provider:** Use Okta to log into the AWS IAM Identity Center (Successor to AWS SSO).
2. **Role Selection:** Engineers are assigned to the Developer-Read-Only role by default.
3. **Elevated Access:** Requesting PowerUser or Administrator access requires a Jira ticket and a specific time-window (Just-In-Time access).

#### Decisions &amp; Reasoning

- **Decision:** Mandatory use of Single Sign-On (SSO) for all third-party and internal tools.
- **Reasoning:** Maintaining separate passwords for AWS, GitHub, and Datadog is a security liability. SSO ensures that when an employee departs, their access can be revoked globally in seconds from a single dashboard, preventing "Orphaned Accounts" that attackers frequently target.
- **Decision:** Defaulting to "Read-Only" access for all environments.
- **Reasoning:** Most production incidents are caused by manual "out-of-band" changes. By making write-access an exception rather than the rule, we force engineers to use the CI/CD pipeline (KB-019) for changes, ensuring all actions are peer-reviewed and version-controlled.