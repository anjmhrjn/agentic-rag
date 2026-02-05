---
doc_id: KB-033
doc_type:
  - runbook
  - database
service: postgresql
date: 2024-03-15
---
### KB-033: Runbook: Database Schema Migration Execution
#### Objective

To apply structural changes to the PostgreSQL tables (KB-008) using Liquibase.

#### Preconditions

- Full backup completed (KB-021).
- Migration script reviewed and approved (KB-005).

#### Instructions

1. **Dry Run:** Execute liquibase update-testing-rollback to verify the script can be reverted.
2. **Deploy:** Run liquibase update against the production cluster.
3. **Verify:** Check the DATABASECHANGELOG table to confirm the entry is marked as EXECUTED.

#### Decisions &amp; Reasoning

- **Decision:** Mandatory "Rollback Script" for every schema change.
- **Reasoning:** Many engineers focus only on the "Forward" path. However, if a migration locks a critical table and causes a production timeout, we need an immediate way out. A pre-written and *tested* rollback script reduces the Mean Time to Recovery (MTTR) from hours to minutes.
- **Decision:** Schema migrations are decoupled from code deployments.
- **Reasoning:** Running migrations during application startup (e.g., hibernate.hbm2ddl.auto=update) is dangerous at scale. If 50 pods start simultaneously, they will all try to modify the schema at once, causing deadlocks. Decoupled execution ensures only one controlled process is touching the metadata.