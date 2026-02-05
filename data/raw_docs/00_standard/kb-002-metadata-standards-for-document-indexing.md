---
doc_id: KB-002
doc_type:
  - standard
  - reference
service: null
date: 2024-03-15
---
### KB-002: Metadata Standards for Document Indexing
#### Purpose

Defines the mandatory key-value pairs (frontmatter) that must accompany every document to ensure it is discoverable and filterable.

#### Mandatory Metadata Schema

Every .md file must begin with a YAML block:

- doc\_id: Unique identifier (e.g., KB-022).
- category: Architecture, Runbook, Incident, Postmortem, or SOP.
- system\_domain: Compute, Storage, Network, or Security.
- impact\_level: Low, Medium, High, or Critical.
- last\_verified: Date (YYYY-MM-DD).

#### Decisions &amp; Reasoning

- **Decision:** Mandatory inclusion of system\_domain.
- **Reasoning:** As the knowledge base grows to 80+ documents, simple keyword search becomes noisy. Categorizing by domain allows for "Faceted Search," where an engineer can filter for "Networking Runbooks" only, reducing information overload during a high-stress outage.