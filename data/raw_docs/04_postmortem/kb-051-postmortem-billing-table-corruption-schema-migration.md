---
doc_id: KB-051
doc_type:
  - operations
service: order-service
date: 2025-03-12
---
### KB-051: Postmortem: Billing Table Corruption via Schema Migration
**Incident ID:** #2025-03-12 | **Impact:** Critical | **Service:** Order Service

#### Incident Summary

Between 14:15 and 16:30 UTC, the Cloud Retail Billing system experienced 100% service failure following a structural database change to the Orders table. 30% of user transactions resulted in "Phantom Charges" or failed persistence due to a column type mismatch.

#### Timeline of Events

- **14:10 UTC:** Automated deployment of v2.4.0 starts, including a schema migration via Liquibase.
- **14:15 UTC:** Prometheus alerts for order\_persistence\_failure\_rate &gt; 10%.
- **14:25 UTC:** On-call engineer identifies the issue in PostgreSQL logs: column "transaction\_id" type mismatch.
- **14:40 UTC:** Manual rollback attempted. Discovery that the rollback script for this specific migration was never tested.
- **15:30 UTC:** Emergency point-in-time restoration (PITR) initiated (KB-021).
- **16:30 UTC:** Database restored to 14:05 state; services return to nominal health.

#### What Went Wrong

The schema migration included a non-additive change that was incompatible with the current running code version. Crucially, the "Verification and Review Process" (KB-005) was bypassed for the rollback script because it was considered "low risk" metadata.

#### What Went Well

Automated metrics (KB-013) detected the anomaly within 5 minutes of deployment. The multi-AZ backup strategy (KB-014) ensured that a recent snapshot was available for immediate restoration.

#### Decisions &amp; Reasoning (Long-term Fixes)

- **Decision:** Mandatory "Tested Rollback" gate in CI/CD (KB-033, KB-045).
- **Reasoning:** This incident proved that a forward-only migration strategy is a single point of failure. We now require all PRs containing schema changes to include an automated test that executes the migration AND the rollback in a containerized PostgreSQL environment before approval.
- **Decision:** Move to "Additive-Only" schema changes for mission-critical tables.
- **Reasoning:** To achieve zero-downtime, we will no longer drop or alter columns in a single step. We will add the new column, dual-write from the application, and only drop the old column in a separate release two weeks later.