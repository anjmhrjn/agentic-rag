---
doc_id: KB-036
doc_type:
  - operations
  - process
service: cloud-retail
date: 2024-03-15
---
### KB-036: Meta-Procedure: The Incident Management Lifecycle
#### Incident Description

This document defines the universal stages of responding to any service degradation or outage within the Cloud Retail environment. It establishes the "rules of engagement" to prevent chaos during high-pressure events.

#### Impact Assessment

A failure to follow a structured lifecycle results in "Incident Drift," where symptoms are treated rather than root causes, leading to extended downtime and team burnout.

#### Resolution Stages

1. **Detection:** Identifying an anomaly via Prometheus/Grafana (KB-013) or user reports.
2. **Triage:** Determining severity (P0–P4) and assigning an Incident Commander (IC).
3. **Containment:** Implementing temporary fixes (e.g., scaling up, KB-017) to stop the "bleeding."
4. **Resolution:** Applying a permanent fix and verifying system health.
5. **Recovery:** Gradual restoration of full service and cleanup of temporary assets.

#### Decisions &amp; Reasoning

- **Decision:** Mandatory separation of the "Incident Commander" (IC) and "Communications Lead" roles.
- **Reasoning:** During a P0 outage, the engineer fixing the system cannot effectively update stakeholders. By decoupling these roles, the IC can maintain 100% focus on technical remediation while the Comm Lead manages expectations, reducing the "interruption tax" on the engineering team.
- **Decision:** Use of a dedicated incident Slack channel for every P1/P0 event.
- **Reasoning:** Mixing incident chatter with regular development talk creates noise and loses critical history. A dedicated channel (e.g., #incident-2026-01-26) acts as a real-time log that is invaluable for the later Postmortem (Category 4).