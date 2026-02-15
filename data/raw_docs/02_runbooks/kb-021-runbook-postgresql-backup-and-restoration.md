---
doc_id: KB-021
doc_type:
  - operations
service: postgresql
date: 2024-03-15
---
### KB-021: Runbook: PostgreSQL RDS Backup and Restoration
#### Objective

To provide a fail-safe procedure for restoring the relational persistence layer to a known-good state following data corruption or accidental deletion.

#### When to Use

Triggered when the data integrity of the PostgreSQL instances (KB-008) is compromised or during scheduled disaster recovery drills.

#### Preconditions

- rds:RestoreDBInstanceToPointInTime permissions.
- Automated backups enabled with at least 7 days of retention.

#### Step-by-Step Instructions

1. **Identify the Recovery Point:** Determine the exact timestamp (UTC) prior to the corruption event. Use the CloudWatch Logs (KB-013) to find the offending transaction.
2. **Initiate Restore:** Use the AWS CLI to create a new instance from the snapshot:
aws rds restore-db-instance-to-point-in-time --source-db-instance-identifier retail-prod-db --target-db-instance-identifier retail-prod-db-restored --restore-time 2026-01-26T14:00:00Z
3. **Validate Data:** Once the instance state is Available, run a sample of 100 queries to verify the missing/corrupted records are present.
4. **Traffic Cutover:** Update the Order Service (KB-006) environment variables to point to the new endpoint and restart the service.

#### Decisions &amp; Reasoning

- **Decision:** We restore to a *new* instance rather than overwriting the existing one.
- **Reasoning:** Overwriting a database is a destructive, irreversible action. By restoring to a separate instance, we allow for "Side-by-Side Comparison." This ensures that if the restoration fails or the timestamp was slightly off, the original data remains available for further investigation. This minimizes the risk of total data loss during a high-pressure recovery scenario.
- **Decision:** Mandatory 35-day retention period for production backups.
- **Reasoning:** Most application-level bugs that cause silent data corruption are not detected immediately. A standard 7-day window is often insufficient for the team to identify the bug, trace the root cause, and initiate a recovery. 35 days provides a significant safety margin, covering a full monthly billing cycle.