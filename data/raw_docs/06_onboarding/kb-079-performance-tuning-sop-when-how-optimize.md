---
doc_id: KB-079
doc_type:
  - onboarding
  - sop
service: performance
date: null
---
### KB-079: Performance Tuning SOP: When and How to Optimize
#### Purpose

Provides a framework for deciding when a service requires optimization vs. simple scaling.

#### The Optimization Trigger

- **Threshold:** If scaling (KB-015) increases costs by &gt;20% month-over-month without a corresponding traffic increase.
- **Metric:** CPU utilization is high, but throughput is low (indicating inefficient code).

#### Decisions &amp; Reasoning

- **Decision:** Vertical scaling is the first response; optimization is the second.
- **Reasoning:** In an outage, "Developer Hours" are more expensive than "AWS Credits." We scale vertically (KB-017) to stop the outage immediately. We only invest in code optimization once the system is stable, ensuring that we aren't performing "Premature Optimization" that complicates the codebase.
- **Decision:** Standardizing on pprof for Go profiling.
- **Reasoning:** Profiling reveals exactly which function is hogging the CPU. Without standard tools, performance tuning is guesswork. Providing a specific SOP for profiling ensures that every engineer can diagnose a "Slow Path" without needing a specialized performance team.