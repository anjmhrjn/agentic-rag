---
doc_id: KB-059
doc_type:
  - postmortem
  - incident
service: billing-service
date: 2025-06-12
---
### KB-059: Postmortem: Double-Billing via Postgres Transaction Timeout
**Incident ID:** #2025-06-12 | **Impact:** High | **Service:** Billing Service

#### Incident Summary

A network hiccup caused a client to retry a "Charge" request. Due to a transaction timeout in PostgreSQL, the first charge was committed *after* the second charge was already processed, resulting in double-billing for 142 customers.

#### Decisions &amp; Reasoning

- **Decision:** Implementation of Idempotency Keys (x-idempotency-key) for all billing endpoints.
- **Reasoning:** Database transactions alone cannot solve network-level retries. An idempotency key ensures that the server recognizes a duplicate request and returns the previous successful result rather than executing the charge twice.