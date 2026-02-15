---
doc_id: KB-028
doc_type:
  - architecture
  - operations
service: cloud-retail
date: 2024-03-15
---
### KB-028: Runbook: Managing Application Feature Flags
#### Objective

To toggle system functionality (e.g., a new checkout flow) without requiring a full code deployment (KB-019).

#### Step-by-Step Instructions

1. **Access Portal:** Log into the internal Feature Management dashboard.
2. **Targeting:** Select the "Retail-Staging" environment first.
3. **Toggle:** Flip the flag for enable\_new\_search\_ui to ON.
4. **Observe:** Check the "Error Rate" metric in KB-013 for 5 minutes before applying to Production.

#### Decisions &amp; Reasoning

- **Decision:** Using Feature Flags instead of long-lived git branches.
- **Reasoning:** Long-lived branches lead to "Merge Hell," where code drifts so far from the main trunk that integration becomes impossible. Feature flags allow us to merge code into main immediately but keep it dormant. This supports "Continuous Integration" (KB-001) while still giving the business control over when a feature actually goes live.
- **Decision:** Flags must have a "Cleanup Ticket" created at birth.
- **Reasoning:** "Flag Rot" is a major source of technical debt. If a flag stays in the code for 2 years, it becomes hard to reason about which path the code is actually taking. Mandatory cleanup tickets ensure that once a feature is 100% rolled out, the toggle is removed from the codebase.