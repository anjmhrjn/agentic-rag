---
doc_id: KB-065
doc_type:
  - postmortem
  - incident
service: security
date: 2024-11-03
---
### KB-065: Postmortem: Public Credential Disclosure in Git
**Incident ID:** #2024-11-03 | **Impact:** Critical | **Service:** Security

#### Incident Summary

An AWS Access Key with S3:ListBucket permissions was committed to a public repository by an intern. The key was scraped and used to attempt data exfiltration within 4 minutes.

#### Decisions &amp; Reasoning

- **Decision:** Implementation of "Pre-commit Hooks" (Trufflehog/Gitleaks).
- **Reasoning:** Prevention is more effective than remediation. By scanning code *locally* before it can be committed, we stop secrets from ever entering the git history, fulfilling the "Security Architecture" standards of KB-010.