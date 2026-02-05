---
doc_id: KB-038
doc_type:
  - incident
  - runbook
service: cloud-retail
date: 2024-03-15
---
### KB-038: Incident Response: High Error Rates in Canary Deployment
#### Symptoms and Alerts

- **Alert:** deployment\_canary\_error\_rate\_high (&gt;1% 5xx responses).
- **Symptoms:** New code version shows 500 errors in logs, while the baseline remains stable.

#### Impact Assessment

Medium to High. Only 5% of users are affected (KB-019), but a failure to act quickly could result in a full rollout of the bug.

#### Resolution Steps

1. **Immediate Rollback:** Flip the traffic weight in the Load Balancer (KB-031) back to 100% for the baseline version.
2. **Isolate Canary Pods:** Keep the faulty pods running but remove them from the target group to allow for "Live Debugging."
3. **Log Analysis:** Scan OpenSearch (KB-013) for the specific stack trace associated with the Canary version ID.
4. **Confirm Baseline Health:** Ensure errors have stopped for 100% of users.

#### Decisions &amp; Reasoning

- **Decision:** "Rollback First, Debug Later" policy for all canary failures.
- **Reasoning:** Production is not a playground. Even if the bug seems "interesting," the primary metric is MTTR (Mean Time to Recovery). Reverting the traffic shift takes seconds and restores user trust immediately.
- **Decision:** Keeping faulty pods alive for 30 minutes post-rollback.
- **Reasoning:** Most bugs are hard to reproduce in Staging. By keeping the "live" faulty pod in an isolated state, developers can exec into the container and inspect the memory state or local logs before the evidence is deleted by a standard kubectl delete.