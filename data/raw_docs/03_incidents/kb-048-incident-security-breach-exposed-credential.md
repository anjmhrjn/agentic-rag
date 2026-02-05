---
doc_id: KB-048
doc_type:
  - incident
  - security
service: cloud-retail
date: 2024-03-15
---
### KB-048: Incident Response: Security Breach - Exposed Credential
#### Incident Description

A developer inadvertently committed a production database password or an AWS Access Key to a public GitHub repository.

#### Resolution Steps

1. **Deactivate Immediately:** Go to the source system (AWS IAM or RDS) and disable the key/password.
2. **Rotate Secret:** Generate a new credential and update AWS Secrets Manager (KB-026).
3. **Purge History:** Use git-filter-repo to remove the secret from the repository's git history.
4. **Audit Logs:** Check CloudTrail or RDS logs to see if the exposed key was used by an unauthorized party.

#### Decisions &amp; Reasoning

- **Decision:** Deactivation is step #1, even before rotation.
- **Reasoning:** Once a secret is public, automated bots will scrape it within seconds. Every millisecond it remains active is a risk of a full data exfiltration. Killing the key is the only way to stop an active or imminent attack.
- **Decision:** Mandatory "Post-Leak Audit" of all logs.
- **Reasoning:** Simply changing the password isn't enough. We must know *if* the attacker already used the key to create a "Backdoor" (e.g., a new IAM user). Without an audit, the system remains compromised even after the original hole is plugged.