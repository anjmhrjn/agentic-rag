---
doc_id: KB-047
doc_type:
  - operations
service: networking
date: 2024-03-15
---
### KB-047: Incident Response: DNS Resolution Failures
#### Symptoms and Alerts

- **Symptoms:** UnknownHostException in microservice logs; frontend returns NXDOMAIN.
- **Impact:** Total system isolation.

#### Resolution Steps

1. **Check Domain Status:** Verify the domain has not expired in the registrar.
2. **Internal vs External:** Determine if the failure is inside the VPC (CoreDNS) or outside (Route 53).
3. **Restart CoreDNS:** If internal, restart the CoreDNS pods in the kube-system namespace.
4. **Verify NS Records:** Ensure the Name Server records in Route 53 match the registrar settings.

#### Decisions &amp; Reasoning

- **Decision:** Mandatory use of "Negative Cache" settings in CoreDNS.
- **Reasoning:** If a service tries to resolve a non-existent host, CoreDNS caches that failure. If the service is then created, it may still fail for 30 seconds due to the negative cache. We set this to a low value (5s) to allow for rapid recovery during scaling events.