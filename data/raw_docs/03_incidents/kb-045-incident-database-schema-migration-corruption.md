---
doc_id: KB-045
doc_type:
  - incident
  - runbook
service: postgresql
date: 2024-03-15
---
### KB-045: Incident Response: Database Schema Migration Corruption
#### Symptoms and Alerts

- **Symptoms:** Order Service crashes immediately upon start; logs show column "X" does not exist or relation "Y" already exists.

#### Impact Assessment

Critical. New pods cannot start, and existing pods may be unable to write to the database.

#### Resolution Steps

1. **Halt CI/CD:** Disable the pipeline (KB-040) to prevent further automated updates.
2. **Execute Rollback Script:** Run the pre-written Liquibase rollback command (KB-033).
3. **Manual Verification:** Check the DATABASECHANGELOG table to confirm the migration state.
4. **Restore if Necessary:** If the rollback fails, initiate a Point-in-Time recovery (KB-021).

#### Decisions &amp; Reasoning

- **Decision:** "No Migration without a Rollback Script" policy (KB-033).
- **Reasoning:** In the heat of an outage, writing a SQL revert script from scratch is error-prone. Requiring it during the PR phase (KB-005) ensures that we have a "Red Button" ready to go the moment something breaks.
- **Decision:** Schema migrations must be additive where possible (e.g., add a column, then drop the old one in a separate release).
- **Reasoning:** Additive changes are non-breaking for existing code. This allows the system to continue running while the migration is in progress, fulfilling the requirement for Zero-Downtime operations.