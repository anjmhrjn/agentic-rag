---
doc_id: KB-068
doc_type:
  - onboarding
  - sop
service: developer-environment
date: null
---
### KB-068: Development Environment Setup: Local Machines
#### Purpose

Step-by-step instructions for configuring a local workstation to match the production "Cloud Retail" stack.

#### Setup Steps

1. **Runtime:** Install Homebrew (macOS) or Chocolatey (Windows).
2. **Containerization:** Install Docker Desktop and configure the docker-compose environment for local DB testing.
3. **Language SDKs:** Use asdf or nvm to install specific versions of Go (1.23) and Node.js (20) to ensure environment parity.

#### Decisions &amp; Reasoning

- **Decision:** Mandatory use of version managers (e.g., asdf) rather than global OS installs.
- **Reasoning:** "It worked on my machine" is usually caused by version mismatches between developer tools and CI runners. Version managers allow developers to switch between versions per project, ensuring that the code is built and tested against the exact same binaries that run in the Kubernetes cluster.
- **Decision:** Using docker-compose for local service dependencies (DB/Cache).
- **Reasoning:** Forcing developers to connect to a shared staging DB for local testing creates "Test Interference," where one developer's data cleanup breaks another's feature test. Local containers provide a clean, isolated environment for every test cycle.