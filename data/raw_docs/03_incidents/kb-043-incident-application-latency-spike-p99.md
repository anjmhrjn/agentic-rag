---
doc_id: KB-043
doc_type:
  - incident
  - runbook
service: cloud-retail
date: 2024-03-15
---
### KB-043: Incident Response: Application Latency Spike (P99)
#### Symptoms and Alerts

- **Alert:** app\_p99\_latency &gt; 1.5 seconds for 5 consecutive minutes.
- **Symptoms:** Frontend feels "sluggish"; user bounce rate increases.

#### Root Cause Analysis

Likely causes include "Thundering Herd" on the cache (KB-030), slow SQL queries (KB-037), or resource contention on EKS nodes.

#### Resolution Steps

1. **Trace Investigation:** Open Jaeger (KB-013) and look for traces where the "Span Duration" is excessive.
2. **Identify "Hot" Nodes:** See if the latency is limited to a single Kubernetes node or a specific service.
3. **Restart Slow Components:** If a single pod is an outlier, delete it to force a fresh start.
4. **Apply HPA Pressure:** Decrease the CPU threshold for scaling (KB-015) to force the system to spread the load across more containers.

#### Decisions &amp; Reasoning

- **Decision:** Focus on P99 metrics rather than "Average" latency.
- **Reasoning:** Average latency hides the "Long Tail" of poor experiences. A P99 of 1.5s means that 1 in 100 users is seeing even worse performance. In a high-traffic environment, this represents thousands of unhappy customers. Solving for the P99 usually reveals systemic issues that "Averages" ignore.
- **Decision:** Tracing is required for all production services.
- **Reasoning:** Without traces, we are guessing which part of the stack is slow (Database? Network? Code?). Distributed tracing provides the "smoking gun," showing exactly where the milliseconds are being spent.