---
doc_id: KB-054
doc_type:
  - postmortem
  - incident
service: shipping-service
date: 2025-02-05
---
### KB-054: Postmortem: SQS Poison Pill Consumer Crash Loop
**Incident ID:** #2025-02-05 | **Impact:** Medium | **Service:** Shipping Service

#### Incident Summary

A single malformed order message containing a null shipping\_address caused 100% of Shipping Service pods to enter a CrashLoopBackOff state, halting all order fulfillments for 4 hours.

#### Root Cause Analysis

The Shipping Service lacked a try-catch block around the JSON parsing logic. When the service pulled the malformed message, it crashed. Because the message was not acknowledged, SQS returned it to the queue, causing the next pod to pick it up and crash.

#### Decisions &amp; Reasoning

- **Decision:** Mandatory Dead Letter Queue (DLQ) for all SQS integrations (KB-042).
- **Reasoning:** This incident was a classic "Infinite Loop." A DLQ acts as a circuit breaker; after 3 failed attempts, SQS moves the message to a side-queue. This allows the system to continue processing valid orders while the "poison pill" is isolated for manual inspection.
- **Decision:** Implementation of Schema Validation (Pydantic/Go-Structs) at the consumer entrance.
- **Reasoning:** We should fail the message, not the process. Strict validation ensures that malformed data is caught and logged as an error without crashing the container.