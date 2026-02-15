---
doc_id: KB-066
doc_type:
  - process
  - reference
service: platform
date: null
---
### KB-066: Overview of Engineering Tools and Platforms
#### Purpose

To introduce new hires to the primary toolchain used to build, deploy, and maintain the Cloud Retail platform. This prevents "Tooling Sprawl" by defining the authoritative software suite.

#### Platform Stack

- **Infrastructure:** AWS (Compute, Database, Networking).
- **Orchestration:** Kubernetes (EKS) for container lifecycle management.
- **Persistence:** PostgreSQL (RDS) and Redis (ElastiCache).
- **Communication:** Slack (Real-time), Jira (Task Tracking), and Confluence (Long-form docs).

#### Decisions &amp; Reasoning

- **Decision:** Standardizing on a single cloud provider (AWS) rather than a multi-cloud approach.
- **Reasoning:** While multi-cloud offers theoretical redundancy, it introduces massive operational complexity and "Least Common Denominator" architecture. By mastering AWS deeply, the team can leverage native integrations like IAM Identity Center and Secrets Manager (KB-010) more effectively, reducing the overhead of managing cross-cloud networking and security parity.
- **Decision:** Using Jira as the "Record of Work" for all infrastructure changes.
- **Reasoning:** In an SRE environment, work that isn't tracked is work that can't be audited. Mandatory ticket association for every production change ensures that if a failure occurs, we have a clear link between a code change and a human intent, which is vital for the Postmortem process (KB-036).