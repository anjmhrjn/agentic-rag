---
doc_id: KB-042
doc_type:
  - operations
service: sqs
date: 2024-03-15
---
### KB-042: Incident Response: SQS Queue Depth Buildup (Bottleneck)
#### Symptoms and Alerts

- **Alert:** sqs\_approximate\_number\_of\_messages\_visible &gt; 10,000.
- **Symptoms:** Customers report that "Shipping Confirmation" emails are taking hours to arrive.

#### Root Cause Analysis

The consumer service (Shipping Service) is either down, crashing, or processing messages slower than the Order Service is producing them.

#### Resolution Steps

1. **Check Consumer Health:** Check the Shipping Service logs for OutOfMemory or Connection Timeout errors.
2. **Scale Consumers:** Increase the EKS replica count for the consumer deployment (KB-015).
3. **Analyze DLQ:** Check the Dead Letter Queue (DLQ) for "poison pill" messages that are causing consumers to crash repeatedly.
4. **Purge (Extreme):** If the messages are non-critical duplicates, purge the queue.

#### Decisions &amp; Reasoning

- **Decision:** Use of a Dead Letter Queue (DLQ) for all asynchronous flows.
- **Reasoning:** A "Poison Pill" (a malformed message) can crash every consumer that picks it up. Without a DLQ, the message stays in the queue and keeps crashing new pods, creating a "CrashLoopBackOff" cycle. A DLQ automatically moves failing messages to the side, allowing the rest of the queue to be processed.
- **Decision:** Horizontal Scaling of consumers as the first reaction.
- **Reasoning:** If the consumers are healthy but slow, adding more "workers" is the fastest way to drain the backlog. This assumes the bottleneck is CPU/Compute and not a downstream database limit.