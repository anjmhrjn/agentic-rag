---
doc_id: KB-076
doc_type:
  - process
  - reference
service: security
date: null
---
### KB-076: Security Onboarding: Compliance and Threat Models
#### Purpose

Introduces new engineers to the security posture and regulatory requirements (e.g., PCI-DSS) of the retail platform.

#### Security Standards

- **Encryption:** All data in transit must use TLS 1.2+ (KB-023).
- **Data Masking:** PII (Personally Identifiable Information) must be redacted in logs.
- **Auditability:** Every API call to AWS is recorded in CloudTrail.

#### Decisions &amp; Reasoning

- **Decision:** Prohibiting the use of "Plaintext HTTP" even for internal traffic.
- **Reasoning:** While internal traffic is safer than public, a single compromised pod could allow an attacker to "sniff" traffic across the cluster. "Zero Trust" networking inside the VPC ensures that even if a service is breached, the attacker cannot easily intercept sensitive customer data moving between components.
- **Decision:** Weekly automated security scans of the container images.
- **Reasoning:** New vulnerabilities (CVEs) are discovered daily. Waiting for a manual audit is too slow. Automated scans in the pipeline ensure that we never deploy an image with a known "Critical" vulnerability, fulfilling our compliance obligations.