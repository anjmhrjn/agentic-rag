---
doc_id: KB-008
doc_type:
  - architecture
  - concept
service: cloud-retail
date: 2024-03-15
---
### KB-008: Persistence Layer: Relational vs. Document Storage
#### Purpose

Explains why different data types are stored in specific database engines.

#### Storage Architecture

- **Relational (PostgreSQL):** Used for Orders and Billing data.
- **Document (DynamoDB):** Used for Session state and User preferences.

#### Decisions &amp; Reasoning

- **Decision:** Using PostgreSQL for Billing rather than a NoSQL solution.
- **Reasoning:** Billing requires ACID (Atomicity, Consistency, Isolation, Durability) compliance and complex joins. NoSQL databases prioritize "Eventual Consistency," which can lead to double-billing or lost transactions during high-concurrency events. The relational model provides the strict guarantees necessary for financial data.