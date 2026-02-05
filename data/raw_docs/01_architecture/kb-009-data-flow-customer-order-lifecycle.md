---
doc_id: KB-009
doc_type:
  - architecture
  - reference
service: cloud-retail
date: 2024-03-15
---
### KB-009: Data Flow: The Lifecycle of a Customer Order
#### Purpose

Explains how data moves through the system components from request to fulfillment.

#### The Flow Path

1. **Ingress:** Request hits CloudFront → Application Load Balancer (ALB).
2. **Processing:** Order Service validates the request against the Inventory DB.
3. **Persistence:** Transaction is written to the Order DB.
4. **Notification:** An event is pushed to SQS (Simple Queue Service) for the Shipping Service to consume.

#### Decisions &amp; Reasoning

- **Decision:** Use of Asynchronous Messaging (SQS) for shipping notifications.
- **Reasoning:** If the Shipping Service is slow or down, the customer's order should not fail. By using a queue, we "decouple" the services. The Order Service finishes its job immediately, and the Shipping Service picks up the work whenever it has the capacity, preventing a bottleneck in the main user flow.