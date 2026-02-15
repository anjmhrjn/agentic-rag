---
doc_id: KB-041
doc_type:
  - operations
service: postgresql
date: 2024-03-15
---
### KB-041: Incident Response: Persistence Layer Read-Only Failure
#### Symptoms and Alerts

- **Symptoms:** Database returns READ ONLY errors on INSERT or UPDATE statements.
- **Alert:** storage\_disk\_utilization\_critical.

#### Root Cause Analysis

Usually triggered when the underlying disk volume is 100% full. Most managed databases switch to read-only mode to prevent data corruption.

#### Resolution Steps

1. **Immediate Expansion:** Increase the RDS storage size via the console or CLI (KB-017).
2. **Clear Temporary Logs:** Check if a failed migration (KB-033) left massive temporary files.
3. **Manual Reset:** Once disk space is available, the database may require a manual status reset to move back to ReadWrite.
4. **Verification:** Run a test write to the health\_check table.

#### Decisions &amp; Reasoning

- **Decision:** Expand the disk *immediately* without waiting for approval.
- **Reasoning:** A read-only database is a "Hard Outage" for an e-commerce platform (no orders can be placed). The cost of an extra 500GB of disk is negligible compared to the revenue loss of a 10-minute outage.
- **Decision:** Provisioned IOPS (PIOPS) are used for all production storage.
- **Reasoning:** Standard GP3 volumes can suffer from "Burst Balance Exhaustion," which mimics a full disk. PIOPS ensure consistent performance regardless of volume size, reducing the likelihood of this specific failure mode.