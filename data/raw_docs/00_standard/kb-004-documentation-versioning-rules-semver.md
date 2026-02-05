---
doc_id: KB-004
doc_type:
  - standard
  - reference
service: null
date: 2024-03-15
---
### KB-004: Documentation Versioning Rules (SemVer)
#### Purpose

Defines how changes to the knowledge base are tracked over time.

#### Versioning Tiers

We follow a simplified Semantic Versioning (SemVer) approach for documents:

- **Major (v1.0 to v2.0):** Complete structural rewrite or a change that renders previous instructions dangerous.
- **Minor (v1.1 to v1.2):** Addition of new steps, troubleshooting sections, or new components.
- **Patch (v1.1.1):** Typo fixes, broken link repairs, or formatting adjustments.

#### Decisions &amp; Reasoning

- **Decision:** Every "Major" or "Minor" change must be accompanied by a CHANGELOG entry at the bottom of the document.
- **Reasoning:** Without a history of *why* a document changed, engineers may inadvertently revert a critical safety fix added after a past incident. Traceability ensures that the knowledge base accumulates wisdom rather than just data.