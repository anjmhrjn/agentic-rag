---
doc_id: KB-072
doc_type:
  - onboarding
  - sop
service: security
date: null
---
### KB-072: Secret Management SOP: Requesting and Using Secrets
#### Purpose

Procedural guide for adding new sensitive data (API keys, DB credentials) to the system.

#### Procedure

1. **Request:** Open a ticket with the "Security Domain" to generate the secret.
2. **Storage:** The secret is injected into AWS Secrets Manager (Production) or SSM Parameter Store (Staging).
3. **Consumption:** Apps must use the Kubernetes External Secrets operator to fetch these as native K8s secrets.

#### Decisions &amp; Reasoning

- **Decision:** Secrets are never committed to the repository, even in encrypted form (e.g., git-crypt).
- **Reasoning:** Repository access is broad. Secrets Manager access is narrow and audited. Storing secrets in a dedicated vault ensures that we can rotate them (KB-026) without having to push a new version of the code, decoupling security operations from the development cycle.
- **Decision:** Use of the "External Secrets Operator."
- **Reasoning:** This allows developers to work with standard Kubernetes Secret objects while the "Source of Truth" remains safely in AWS. It abstracts the cloud provider's complexity away from the application manifests.