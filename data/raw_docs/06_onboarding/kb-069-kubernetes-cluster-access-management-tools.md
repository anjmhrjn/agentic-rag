---
doc_id: KB-069
doc_type:
  - onboarding
  - sop
service: eks-cluster
date: null
---
### KB-069: Kubernetes Cluster Access and Management Tools
#### Purpose

Standardizes the tools and methods used to interact with the EKS compute layer (KB-006).

#### Required Tooling

- kubectl: The standard CLI for Kubernetes.
- aws-iam-authenticator: For secure login via IAM.
- k9s: A terminal UI for rapid cluster observation.

#### Decisions &amp; Reasoning

- **Decision:** Prohibition of kubectl delete commands on production resources without a peer in Slack.
- **Reasoning:** While Kubernetes is resilient, accidental deletion of a Namespace or a StatefullSet can cause massive data recovery efforts. A "Two-Man Rule" for destructive commands acts as a simple but effective safety gate during high-stress troubleshooting.
- **Decision:** Recommending k9s for monitoring pod health.
- **Reasoning:** While kubectl is authoritative, it is slow for scanning multiple namespaces. k9s provides a real-time visual dashboard that allows SREs to spot CrashLoopBackOff events (KB-044) instantly, reducing the Mean Time to Detect (MTTD).