---
doc_id: KB-070
doc_type:
  - process
  - reference
service: version-control
date: null
---
### KB-070: Code Versioning Workflow: Trunk-Based Development
#### Purpose

Defines the branching strategy used to maintain high deployment velocity for the microservices stack.

#### Workflow Rules

1. **Main Branch:** The main branch is always in a deployable state.
2. **Short-lived Branches:** Feature branches must be merged back into main within 48 hours.
3. **Merge Strategy:** We use "Squash and Merge" to maintain a clean git history.

#### Decisions &amp; Reasoning

- **Decision:** Choosing Trunk-Based Development over GitFlow.
- **Reasoning:** GitFlow, with its long-lived "Develop" and "Release" branches, creates massive "Merge Hells" and delays feedback. Trunk-Based Development forces small, frequent integrations. This aligns with our DevOps culture (KB-001) by ensuring that bugs are caught immediately after integration rather than weeks later during a release cycle.
- **Decision:** Mandatory "Squash and Merge."
- **Reasoning:** Standard merges create a "Spaghetti" graph in git history. Squashing turns a complex feature development into a single, clean commit on main. This makes it significantly easier to revert changes if a deployment triggers an incident (KB-038).