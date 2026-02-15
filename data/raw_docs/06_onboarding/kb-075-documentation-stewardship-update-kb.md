---
doc_id: KB-075
doc_type:
  - process
  - reference
service: documentation
date: null
---
### KB-075: Documentation Stewardship: How to Update this KB
#### Purpose

Ensures that the 80 documents in this knowledge base remain accurate and trusted over time.

#### Stewardship Rules

1. **Verification:** Every document must be reviewed annually or after a major system change.
2. **Feedback Loop:** Use the "Edit" button at the bottom of any doc to submit a PR for corrections.
3. **Owner:** The "SRE Platform Squad" is the ultimate curator, but "Authorship" is distributed.

#### Decisions &amp; Reasoning

- **Decision:** Documentation is treated as code.
- **Reasoning:** Traditional wikis (KB-001) become "Information Graveyards" because they lack a review process. By using a Git-based workflow for this KB, we ensure that every update passes the same quality checks as our software, maintaining the "Source of Truth."
- **Decision:** Mandatory last\_verified metadata field.
- **Reasoning:** Engineers instinctively distrust old documentation. A timestamp proves that a human has recently confirmed the steps work. If a doc is &gt;365 days old, it is automatically flagged for a "Verification Drill."