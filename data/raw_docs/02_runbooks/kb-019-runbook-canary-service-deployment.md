---
doc_id: KB-019
doc_type:
  - runbook
  - deployment
service: cloud-retail
date: 2024-03-15
---
### KB-019: Runbook: Deploying a Service Update via Canary
#### Objective

Details the procedure for releasing new code with minimal impact on the user base.

#### When to Use

Standard procedure for all "Minor" or "Major" application updates (KB-004).

#### Instructions

1. **Deploy Canary:** Create a new deployment with the new image, but only 1 replica.
2. **Shift Traffic:** Adjust the Load Balancer to route 5% of traffic to the Canary pod.
3. **Observe:** Monitor the "Error Rate" of the Canary vs. the Production pods for 10 minutes.
4. **Full Rollout:** If error rates are identical, update the main deployment image and scale down the canary.

#### Validation Steps

1. Verify the app\_version tag in Prometheus shows the new version for 100% of requests.
2. Confirm no spike in 5xx HTTP responses.

#### Decisions &amp; Reasoning

- **Decision:** Use of a 5% traffic shift for the initial phase.
- **Reasoning:** 5% is small enough to limit the "Blast Radius" of a bad bug (KB-017), but large enough to generate statistically significant data in our monitoring stack. This allows us to "Fail Fast" without ruining the experience for the entire customer base.