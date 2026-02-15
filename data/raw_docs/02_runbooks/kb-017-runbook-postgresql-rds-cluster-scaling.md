---
doc_id: KB-017
doc_type:
  - operations
service: postgresql
date: 2024-03-15
---
### KB-017: Runbook: PostgreSQL RDS Cluster Scaling
#### Objective

Provides step-by-step instructions for increasing database capacity when indexFullness or CPU thresholds are exceeded.

#### When to Use

Use this when the Prometheus alert db\_cpu\_high triggers or when preparing for a high-traffic event (e.g., Black Friday).

#### Preconditions

- AWS CLI configured with DatabaseAdmin permissions.
- The database must be in a Available state.

#### Step-by-Step Instructions

1. Identify the current instance class:
aws rds describe-db-instances --db-instance-identifier retail-prod-db
2. Apply the new instance type (e.g., moving from db.t3.medium to db.r5.large):
aws rds modify-db-instance --db-instance-identifier retail-prod-db --db-instance-class db.r5.large --apply-immediately
3. Monitor the "Status" field. It will move to modifying.

#### Validation Steps

1. Verify the new class is active:
aws rds describe-db-instances... --query 'DBInstances.DBInstanceClass'
2. Confirm that the Order Service (KB-006) latency has returned to the baseline (&lt;200ms).

#### Decisions &amp; Reasoning

- **Decision:** Use of --apply-immediately for capacity-related scaling.
- **Reasoning:** By default, RDS applies changes during the next maintenance window. If we are under active load pressure, we cannot wait for the weekend. While this causes a brief (30-60 second) failover/reboot, it is preferable to a sustained multi-hour slowdown that affects 100% of users.