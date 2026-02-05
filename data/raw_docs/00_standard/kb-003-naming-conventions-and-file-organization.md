---
doc_id: KB-003
doc_type:
  - standard
  - reference
service: null
date: 2024-03-15
---
### KB-003: Naming Conventions and File Organization
#### Purpose

Standardizes how files are named and where they are stored to prevent path collisions and confusion.

#### Convention Rules

1. **File Names:** Use lowercase characters and hyphens (kebab-case). Example: database-backup-runbook.md.
2. **Folder Structure:** Flat categorization by type (e.g., /runbooks/, /incidents/).
3. **No Abbreviations:** Use architecture instead of arch, and incident instead of inc.

#### Decisions &amp; Reasoning

- **Decision:** Use hyphens instead of underscores in filenames.
- **Reasoning:** Search engines and indexing tools often treat hyphens as word separators but treat underscores as part of a single string. Hyphens ensure that each word in a filename is individually indexed, making it significantly easier for both humans and future automated systems to find documents via search.