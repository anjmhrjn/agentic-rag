---
doc_id: KB-023
doc_type:
  - operations
  - security
service: networking
date: 2024-03-15
---
### KB-023: Runbook: SSL/TLS Certificate Management via ACM
#### Objective

To manage and rotate the digital certificates ensuring encrypted communication (KB-007) for the frontend.

#### Preconditions

- Domain ownership verified in Route 53.
- Permissions for AWS Certificate Manager (ACM).

#### Step-by-Step Instructions

1. **Request Certificate:** Create a request for the wildcard domain *.cloudretail.com.
2. **DNS Validation:** Choose DNS validation over Email validation.
3. **Record Creation:** Add the generated CNAME records to the Route 53 hosted zone.
4. **Attachment:** Update the ALB (KB-009) listener to use the new Certificate ARN.

#### Decisions &amp; Reasoning

- **Decision:** Standardizing on DNS Validation instead of Email.
- **Reasoning:** Email validation requires a human to click a link in an inbox, which is impossible to automate through Infrastructure as Code (KB-020). DNS validation allows our Terraform scripts to automatically create the validation records. Once established, ACM can auto-renew certificates without any human intervention, permanently solving the "Certificate Expiry Outage" failure mode.
- **Decision:** Use of Wildcard Certificates (*) for internal subdomains.
- **Reasoning:** Managing 50 individual certificates for 50 microservices creates massive administrative overhead and increases the probability that one is missed. A wildcard certificate simplifies management and ensures that new services (KB-006) are secure from the moment they are launched.