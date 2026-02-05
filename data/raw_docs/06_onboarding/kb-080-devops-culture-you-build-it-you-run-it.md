---
doc_id: KB-080
doc_type:
  - onboarding
  - sop
service: culture
date: null
---
### KB-080: The DevOps Culture: "You Build It, You Run It"
#### Purpose

The concluding document of the Phase 1 Knowledge Base, defining the cultural expectations of an engineer in this environment.

#### The Philosophy

At Cloud Retail, there is no "Operations Team" that catches bugs from the "Development Team." We operate on a model of **Shared Ownership** .

1. **Accountability:** The engineer who writes the feature is the one who monitors its deployment (KB-019).
2. **Curiosity:** Failures are seen as opportunities for deep reasoning (Category 4), not blame.
3. **Documentation:** High-quality knowledge is a "First-Class System" (this KB), not a side task.

#### Decisions &amp; Reasoning

- **Decision:** The "On-Call" rotation includes both SREs and Software Developers.
- **Reasoning:** If developers never feel the "pain" of a production failure, they have no incentive to write resilient code. By sharing the rotation, the entire team becomes invested in the stability of the platform, leading to better architectural decisions and a more robust system for our customers.
- **Decision:** This 80-document Knowledge Base is the authoritative Source of Truth.
- **Reasoning:** Without a structured, reason-heavy knowledge foundation, a team relies on "Tribal Knowledge." This knowledge base ensures that the "Why" behind every decision is preserved, allowing the team to scale and the system to evolve with absolute clarity.