---
doc_id: KB-078
doc_type:
  - onboarding
  - sop
service: disaster-recovery
date: null
---
### KB-078: Disaster Recovery Training and Simulation SOP
#### Purpose

Defines the training requirements for engineers to execute the regional failover defined in KB-025.

#### Training Drills

- **Shadowing:** New engineers must shadow a "DR Exercise" before joining the rotation.
- **GameDays:** Quarterly simulation where we deliberately "break" a region in Staging and practice recovery.
- **Wheel of Misfortune:** Weekly team exercise to walk through a random "Postmortem" (Category 4).

#### Decisions &amp; Reasoning

- **Decision:** Quarterly drills are conducted during "Business Hours."
- **Reasoning:** Most teams run drills at 2 AM to avoid impact. However, the most senior people are asleep and the team is exhausted. By running drills during the day, we ensure that the *process* works when everyone is at their best. If the process is too risky for a daytime drill, it is too risky for a real disaster.
- **Decision:** Mandatory "Retrospective" after every drill.
- **Reasoning:** A drill that doesn't produce an "Action Item" (Category 4) is a missed opportunity. We treat simulations as incidents, ensuring the knowledge base (KB-075) is updated with new findings or missing steps.