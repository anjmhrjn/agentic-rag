---
doc_id: KB-015
doc_type:
  - architecture
  - reference
service: cloud-retail
date: 2024-03-15
---
### KB-015: Scaling Policies: Horizontal Pod Autoscaling (HPA)
#### Purpose

Explains how the Kubernetes compute layer automatically reacts to changes in customer demand.

#### Architecture Description

We use the Kubernetes Horizontal Pod Autoscaler (HPA) to dynamically increase or decrease the number of running containers for the Order and Inventory services.

#### Decisions &amp; Reasoning

- **Decision:** Scale based on "Average CPU Utilization" with a 70% threshold.
- **Reasoning:** CPU is the most reliable signal of application load for our Go-based services. Setting the threshold at 70% (rather than 90%) provides a "Buffer Zone." It ensures that new pods are spun up and "Ready" (KB-020) *before* the existing pods are overwhelmed and start dropping customer requests.
- **Decision:** Implementation of "Scale-Down Stabilization" windows (5 minutes).
- **Reasoning:** Rapidly fluctuating traffic can cause "Thrashing"—where the system scales up and down repeatedly in a short window. This wastes resources and causes instability. A 5-minute stabilization window ensures that the system only scales down after traffic has remained low for a sustained period.