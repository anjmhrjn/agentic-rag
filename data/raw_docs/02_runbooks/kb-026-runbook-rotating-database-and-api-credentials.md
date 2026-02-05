---
doc_id: KB-026
doc_type:
  - runbook
  - security
service: cloud-retail
date: 2024-03-15
---
### KB-026: Runbook: Rotating Database and API Credentials
#### Objective

To fulfill the 90-day security rotation requirement established in the Security Architecture (KB-010).

#### Instructions

1. **Stage 1:** Create a "v2" secret in AWS Secrets Manager.
2. **Stage 2:** Update the application pods (KB-018) to use both v1 and v2 simultaneously (if the app supports it) or perform a rolling restart.
3. **Stage 3:** Confirm the application is successfully using the v2 secret via connection metrics (KB-013).
4. **Stage 4:** Disable the v1 credential in the source system after a 24-hour buffer.

#### Decisions &amp; Reasoning

- **Decision:** Mandatory 24-hour "Deprecation Buffer" for all secrets.
- **Reasoning:** In complex microservice environments, some background tasks or legacy jobs may not refresh their credentials instantly. By keeping the old secret active for 24 hours, we prevent "Silent Failure" of these secondary tasks, providing a window to identify and fix any components that didn't migrate correctly.
- **Decision:** Automated rotation via Lambda for RDS.
- **Reasoning:** Human rotation is prone to "Key Fatigue" and errors. Automated rotation ensures that rotation *actually happens* every 90 days without relying on an engineer remembering to do it.