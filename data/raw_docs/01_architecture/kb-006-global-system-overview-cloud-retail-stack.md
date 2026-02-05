---
doc_id: KB-006
doc_type:
  - architecture
  - concept
service: cloud-retail
date: 2024-03-15
---
### KB-006: Global System Overview: The "Cloud Retail" Stack
This system is representative, not a live production environment.

#### Purpose

Provides the high-level context for the entire engineering environment documented in this knowledge base.

#### System Description

The "Cloud Retail" system is a microservices-based e-commerce platform hosted on AWS. It is designed for high availability and global scale, utilizing Kubernetes (EKS) for compute and a combination of relational and NoSQL databases for persistence.

#### Major Components

- **Frontend (React/CloudFront):** Handles user interactions and global content delivery.
- **Order Service (Go/EKS):** Manages transactions and state changes.
- **Inventory Database (PostgreSQL/RDS):** The relational source of truth for stock levels.
- **Search Engine (OpenSearch):** Provides real-time catalog discovery.

#### Decisions &amp; Reasoning

- **Decision:** Deployment across multiple AWS Availability Zones (Multi-AZ).
- **Reasoning:** A single zone failure in AWS is a statistical certainty. Multi-AZ deployment ensures that if one data center goes dark, the platform remains operational, fulfilling the business requirement for 99.9% uptime.