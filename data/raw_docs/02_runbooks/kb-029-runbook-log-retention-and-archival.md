---
doc_id: KB-029
doc_type:
  - runbook
  - observability
service: cloud-retail
date: 2024-03-15
---
### KB-029: Runbook: Implementing Log Retention and Archival
#### Objective

To manage the lifecycle of system logs (KB-013) to balance forensic needs with storage costs.

#### Policy

- **Hot Storage (OpenSearch):** 14 Days.
- **Cold Storage (S3):** 1 Year (Gzipped).

#### Step-by-Step Instructions

1. **Config:** Update the Fluent-bit configuration to stream to both OpenSearch and S3.
2. **Lifecycle Rule:** Apply an S3 Lifecycle Policy to move objects to "Glacier" after 90 days.
3. **Verification:** Check the S3 bucket size monthly to ensure archival is functioning.

#### Decisions &amp; Reasoning

- **Decision:** Retention of "Hot" logs for only 14 days.
- **Reasoning:** 99% of log-based troubleshooting happens within 48 hours of an incident. Storing logs in an indexed, searchable state (OpenSearch) is expensive. By moving data to S3 after 14 days, we reduce our observability costs by ~70% while still remaining compliant with SOC2 auditing requirements.
- **Decision:** Use of Gzip compression for all S3 archives.
- **Reasoning:** DevOps logs are highly repetitive and compress at a ratio of ~10:1. This simple step saves thousands of dollars in storage costs annually with zero impact on recovery speed.