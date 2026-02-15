---
doc_id: KB-005
doc_type:
  - process
service: null
date: 2024-03-15
---
### KB-005: The Verification and Review Process (PR Workflow)
#### Purpose

Explains the "Human-in-the-loop" gate required before any document becomes a "Source of Truth."

#### The Review Chain

1. **Author:** Drafts document following the Category Template.
2. **Peer Review:** A second engineer executes the runbook (in Staging) or verifies the architecture diagram.
3. **Approval:** Signed off via a Pull Request (PR) in the documentation repository.

#### Decisions &amp; Reasoning

- **Decision:** "Operational Release" review must focus only on changed content.
- **Reasoning:** Re-reviewing a 600-word document for every minor update is a "velocity killer." Focusing only on the diff (the changes) ensures the knowledge base remains agile and up-to-date without overwhelming the senior engineers responsible for verification.