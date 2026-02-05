---
doc_id: KB-064
doc_type:
  - postmortem
  - incident
service: order-db
date: 2024-08-14
---
### KB-064: Postmortem: Database Primary Key Exhaustion
**Incident ID:** #2024-08-14 | **Impact:** Critical | **Service:** Order DB

#### Incident Summary

The Orders table reached the limit of a 32-bit integer for the id column. The database began rejecting all new orders as it could no longer generate a unique primary key.

#### Decisions &amp; Reasoning

- **Decision:** Standardize on 64-bit BigInt (Int8) for all primary keys in the "Global System Overview" (KB-006).
- **Reasoning:** 32-bit integers cap at 2.1 billion. While this seemed high at launch, our growth reached this in 3 years. BigInt supports up to 9 quintillion records, effectively eliminating "Key Exhaustion" as a failure mode for the next 100 years.