---
doc_id: KB-071
doc_type:
  - onboarding
  - sop
service: cicd-pipeline
date: null
---
### KB-071: CI/CD Pipeline Standards and PR Etiquette
#### Purpose

Outlines the expectations for code quality and automated testing before code reaches the cluster.

#### The Pull Request Contract

- **PR Size:** No more than 500 lines of code (LOC) per PR.
- **Coverage:** 80% unit test coverage required for all new features.
- **Reviewers:** Minimum of two approvals from the core team.

#### Decisions &amp; Reasoning

- **Decision:** Strict 500 LOC limit for Pull Requests.
- **Reasoning:** Research shows that review quality drops precipitously after 400-500 lines. Reviewers begin to "rubber-stamp" large PRs because they are overwhelmed. Small PRs ensure that every line of code is actually read and understood, preventing "logic bombs" from reaching production.
- **Decision:** Automated linting and formatting in the CI pipeline.
- **Reasoning:** Arguing about tabs vs. spaces in a code review is "bike-shedding" that wastes senior engineering time. Automating these checks ensures that the PR conversation remains focused on architectural soundness and system implications.