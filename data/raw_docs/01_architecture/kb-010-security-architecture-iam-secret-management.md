---
doc_id: KB-010
doc_type:
  - architecture
  - standard
service: cloud-retail
date: 2024-03-15
---
### KB-010: Security Architecture: IAM and Secret Management
#### Purpose

Defines the standards for identity and how sensitive data (API keys, DB passwords) is handled.

#### Identity Strategy

We follow the "Principle of Least Privilege" using AWS IAM Roles for Service Accounts (IRSA). Secrets are never stored in code; they are fetched at runtime from AWS Secrets Manager.

#### Decisions &amp; Reasoning

- **Decision:** Mandatory 90-day rotation for all database credentials.
- **Reasoning:** In the event of a "Silent Leak" (where a key is stolen but not immediately used), rotation limits the "Window of Vulnerability." An attacker has a finite time to use the stolen credentials before they become useless, significantly reducing the potential blast radius of a credential compromise. No secrets ever appear in this knowledge base.