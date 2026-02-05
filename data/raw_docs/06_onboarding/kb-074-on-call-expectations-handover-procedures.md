---
doc_id: KB-074
doc_type:
  - onboarding
  - sop
service: operations
date: null
---
### KB-074: On-Call Expectations and Handover Procedures
#### Purpose

Defines the responsibilities of the engineer "holding the pager" for the Cloud Retail stack.

#### On-Call Pillars

- **Response Time:** 15 minutes to acknowledge a P0/P1 alert.
- **Escalation:** If you cannot resolve the issue in 30 minutes, you MUST page the Secondary or a Subject Matter Expert (SME).
- **The Handover:** Weekly Tuesday meeting to review all alerts triggered during the previous shift.

#### Decisions &amp; Reasoning

- **Decision:** Mandatory "Acknowledgement" does not mean "Resolution."
- **Reasoning:** The goal of the 15-minute window is to ensure someone is watching. We do not expect a fix in 15 minutes, but we do expect a "Containment" strategy (KB-036) to begin, protecting the user experience.
- **Decision:** Weekly "Alert Audit" meeting.
- **Reasoning:** If an on-call engineer ignores "flaky" alerts, the system's "Signal-to-Noise" ratio degrades. Auditing ensure that we either fix the system or delete the alert, preventing "Alert Fatigue"—the leading cause of human error during major outages.