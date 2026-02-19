from typing import List, Dict, Optional
from dataclasses import dataclass

@dataclass
class TestQuery:
    """Single test case for evaluation"""
    query: str
    expected_sources: List[str]  # Doc IDs that should be retrieved
    expected_topics: List[str]   # Keywords that should appear in answer
    query_type: str              # "simple", "complex", "multi_part", "out_of_scope"
    difficulty: str              # "easy", "medium", "hard"
    notes: Optional[str] = None

# DevOps RAG Test Dataset
TEST_DATASET = [
    # ============================================================================
    # CATEGORY 1: Simple Factual Retrieval
    # ============================================================================
    
    TestQuery(
        query="What is the document ID for the runbook about load balancer routing updates?",
        expected_sources=["KB-031"],
        expected_topics=["KB-031", "load balancer", "routing", "ALB"],
        query_type="simple",
        difficulty="easy",
        notes="Direct lookup - document metadata"
    ),
    
    TestQuery(
        query="What date was the Black Friday Redis cache exhaustion incident?",
        expected_sources=["KB-052"],
        expected_topics=["2025-11-27", "Black Friday", "Redis", "cache"],
        query_type="simple",
        difficulty="easy",
        notes="Direct date lookup from postmortem"
    ),
    
    TestQuery(
        query="What percentage of traffic should be shifted to the canary pod during deployment?",
        expected_sources=["KB-019"],
        expected_topics=["5%", "canary", "traffic", "deployment"],
        query_type="simple",
        difficulty="easy",
        notes="Specific metric from canary runbook"
    ),
    
    TestQuery(
        query="What is the maximum number of days of inactivity before an IAM user should be deleted?",
        expected_sources=["KB-032"],
        expected_topics=["90 days", "IAM", "inactive", "delete"],
        query_type="simple",
        difficulty="easy",
        notes="Specific threshold from IAM governance"
    ),
    
    TestQuery(
        query="What tool is mentioned for implementing pre-commit hooks to scan for secrets?",
        expected_sources=["KB-065"],
        expected_topics=["Trufflehog", "Gitleaks", "pre-commit", "secrets"],
        query_type="simple",
        difficulty="easy",
        notes="Specific tool recommendation from postmortem"
    ),
    
    TestQuery(
        query="What is the primary key data type recommendation mentioned in KB-064?",
        expected_sources=["KB-064"],
        expected_topics=["64-bit", "BigInt", "Int8", "primary key"],
        query_type="simple",
        difficulty="easy",
        notes="Direct technical specification"
    ),
    
    TestQuery(
        query="Which Slack channel should be used to announce the start of a runbook execution?",
        expected_sources=["KB-016"],
        expected_topics=["#ops-production", "Slack", "announce", "runbook"],
        query_type="simple",
        difficulty="easy",
        notes="Specific operational requirement"
    ),
    
    TestQuery(
        query="What port should be used when editing the ALB Listener for routing updates?",
        expected_sources=["KB-031"],
        expected_topics=["443", "port", "ALB", "listener"],
        query_type="simple",
        difficulty="easy",
        notes="Specific technical detail"
    ),
    
    TestQuery(
        query="What is the minimum number of replicas for a canary deployment?",
        expected_sources=["KB-019"],
        expected_topics=["1", "replica", "canary", "deployment"],
        query_type="simple",
        difficulty="easy",
        notes="Specific deployment configuration"
    ),
    
    TestQuery(
        query="What is the retention period for CloudWatch logs mentioned in the documentation?",
        expected_sources=["KB-013", "KB-040"],
        expected_topics=["retention", "CloudWatch", "logs"],
        query_type="simple",
        difficulty="medium",
        notes="May require searching across monitoring docs"
    ),
    
    # ============================================================================
    # CATEGORY 2: Process & Procedural Questions
    # ============================================================================
    
    TestQuery(
        query="What are the steps to deploy a service update via canary?",
        expected_sources=["KB-019"],
        expected_topics=["deploy", "canary", "traffic", "observe", "rollout", "steps"],
        query_type="simple",
        difficulty="medium",
        notes="Multi-step procedure from single document"
    ),
    
    TestQuery(
        query="What is the proper sequence for executing a runbook according to KB-016?",
        expected_sources=["KB-016"],
        expected_topics=["announce", "verify", "sequential", "validate", "Slack"],
        query_type="simple",
        difficulty="medium",
        notes="Standard procedure - requires listing steps in order"
    ),
    
    TestQuery(
        query="How should an engineer handle a failed command during runbook execution?",
        expected_sources=["KB-016"],
        expected_topics=["stop", "troubleshooting", "failed", "consult"],
        query_type="simple",
        difficulty="medium",
        notes="Error handling procedure"
    ),
    
    TestQuery(
        query="What are the preconditions that must be met before executing the standard runbook guidelines?",
        expected_sources=["KB-016"],
        expected_topics=["bastion host", "Jira", "incident", "CR", "access"],
        query_type="simple",
        difficulty="easy",
        notes="Listed preconditions"
    ),
    
    TestQuery(
        query="What validation steps should be performed after a canary deployment?",
        expected_sources=["KB-019"],
        expected_topics=["app_version", "Prometheus", "5xx", "HTTP", "validation"],
        query_type="simple",
        difficulty="medium",
        notes="Specific validation checklist"
    ),
    
    TestQuery(
        query="Describe the process for toggling a feature flag in the staging environment.",
        expected_sources=["KB-028"],
        expected_topics=["portal", "staging", "toggle", "observe", "error rate"],
        query_type="simple",
        difficulty="medium",
        notes="Step-by-step process from runbook"
    ),
    
    TestQuery(
        query="What steps are involved in the monthly IAM governance review?",
        expected_sources=["KB-032"],
        expected_topics=["credential report", "90 days", "revoke", "audit", "roles"],
        query_type="simple",
        difficulty="medium",
        notes="Regular maintenance procedure"
    ),
    
    TestQuery(
        query="How should load balancer routing rules be prioritized to avoid traffic stealing?",
        expected_sources=["KB-031"],
        expected_topics=["priority", "catch-all", "lowest", "negative priority"],
        query_type="simple",
        difficulty="medium",
        notes="Priority configuration principle"
    ),
    
    # ============================================================================
    # CATEGORY 3: Decision Reasoning Questions
    # ============================================================================
    
    TestQuery(
        query="Why was path-based routing chosen over host-based routing for internal APIs?",
        expected_sources=["KB-031"],
        expected_topics=["SSL certificate", "IP address", "cost", "complexity", "single"],
        query_type="complex",
        difficulty="medium",
        notes="Requires understanding architectural reasoning"
    ),
    
    TestQuery(
        query="What is the reasoning behind the mandatory Slack announcement for manual production changes?",
        expected_sources=["KB-016"],
        expected_topics=["visibility", "silent changes", "incident", "mental model", "distributed team"],
        query_type="complex",
        difficulty="medium",
        notes="Understanding organizational reasoning"
    ),
    
    TestQuery(
        query="Why are feature flags preferred over long-lived git branches?",
        expected_sources=["KB-028"],
        expected_topics=["merge hell", "continuous integration", "code drift", "trunk"],
        query_type="complex",
        difficulty="medium",
        notes="Software engineering reasoning"
    ),
    
    TestQuery(
        query="What is the rationale for using a 5% traffic shift during canary deployments?",
        expected_sources=["KB-019"],
        expected_topics=["blast radius", "statistically significant", "fail fast"],
        query_type="complex",
        difficulty="medium",
        notes="Risk management reasoning"
    ),
    
    TestQuery(
        query="Why must flags have a Cleanup Ticket created at birth?",
        expected_sources=["KB-028"],
        expected_topics=["flag rot", "technical debt", "cleanup", "removed", "codebase"],
        query_type="complex",
        difficulty="medium",
        notes="Technical debt prevention"
    ),
    
    TestQuery(
        query="Explain the reasoning behind hard-deletion of IAM users inactive for 90+ days.",
        expected_sources=["KB-032"],
        expected_topics=["security", "attack", "inactive", "monitored", "compromise"],
        query_type="complex",
        difficulty="medium",
        notes="Security reasoning"
    ),
    
    TestQuery(
        query="Why should no service account have AdministratorAccess permissions?",
        expected_sources=["KB-032"],
        expected_topics=["blast radius", "compromised", "scoped permissions", "microservice"],
        query_type="complex",
        difficulty="medium",
        notes="Security principle - least privilege"
    ),
    
    TestQuery(
        query="What is the reasoning behind the 64-bit BigInt decision for primary keys?",
        expected_sources=["KB-064"],
        expected_topics=["32-bit", "2.1 billion", "key exhaustion", "growth", "quintillion"],
        query_type="complex",
        difficulty="medium",
        notes="Scalability reasoning from postmortem"
    ),
    
    # ============================================================================
    # CATEGORY 4: Multi-Hop Reasoning
    # ============================================================================
    
    TestQuery(
        query="If I want to deploy a new service version and need to update load balancer routing, which runbooks should I consult and in what order?",
        expected_sources=["KB-019", "KB-031", "KB-016"],
        expected_topics=["canary", "deployment", "load balancer", "routing", "sequence"],
        query_type="multi_part",
        difficulty="hard",
        notes="Requires connecting multiple runbooks in logical sequence"
    ),
    
    TestQuery(
        query="What monitoring tools and metrics should be checked both before and after a canary deployment?",
        expected_sources=["KB-019", "KB-013", "KB-016"],
        expected_topics=["Grafana", "error rate", "Prometheus", "5xx", "health"],
        query_type="multi_part",
        difficulty="hard",
        notes="Requires synthesizing monitoring from multiple sources"
    ),
    
    TestQuery(
        query="How does the feature flag strategy relate to continuous integration practices mentioned in the knowledge base?",
        expected_sources=["KB-028", "KB-001"],
        expected_topics=["continuous integration", "trunk", "merge", "feature flag", "dormant"],
        query_type="complex",
        difficulty="hard",
        notes="Requires connecting architecture concepts across documents"
    ),
    
    TestQuery(
        query="What is the relationship between KB-006, KB-031, and the ALB configuration?",
        expected_sources=["KB-006", "KB-031"],
        expected_topics=["target group", "ALB", "microservice", "routing"],
        query_type="complex",
        difficulty="hard",
        notes="Cross-reference query - tests document relationships"
    ),
    
    TestQuery(
        query="If a Redis cache exhaustion event occurs, what related runbooks might be relevant for recovery?",
        expected_sources=["KB-052", "KB-030", "KB-017", "KB-012"],
        expected_topics=["Redis", "cache", "warm-up", "scaling", "recovery"],
        query_type="multi_part",
        difficulty="hard",
        notes="Incident response - requires connecting postmortem to runbooks"
    ),
    
    TestQuery(
        query="How do the IAM governance practices relate to limiting the blast radius of compromised services?",
        expected_sources=["KB-032", "KB-006"],
        expected_topics=["IAM", "scoped permissions", "blast radius", "compromised", "microservice"],
        query_type="complex",
        difficulty="hard",
        notes="Security architecture connection"
    ),
    
    # ============================================================================
    # CATEGORY 5: Incident Analysis & Troubleshooting
    # ============================================================================
    
    TestQuery(
        query="What was the root cause of the SQS poison pill consumer crash loop incident?",
        expected_sources=["KB-054"],
        expected_topics=["malformed", "JSON parsing", "try-catch", "crash", "acknowledged"],
        query_type="simple",
        difficulty="medium",
        notes="Root cause analysis from postmortem"
    ),
    
    TestQuery(
        query="What immediate action should be taken if Redis memory hits 98% during a traffic spike?",
        expected_sources=["KB-052", "KB-017"],
        expected_topics=["vertical scaling", "alert", "eviction", "memory"],
        query_type="complex",
        difficulty="hard",
        notes="Requires inferring action from incident analysis"
    ),
    
    TestQuery(
        query="What configuration error caused the Black Friday Redis incident, and how should it be fixed?",
        expected_sources=["KB-052"],
        expected_topics=["allkeys-lru", "volatile-lru", "eviction policy", "TTL"],
        query_type="multi_part",
        difficulty="medium",
        notes="Two-part: problem identification and solution"
    ),
    
    TestQuery(
        query="What was the impact duration of the regional failover latency spike incident?",
        expected_sources=["KB-056"],
        expected_topics=["20 minutes", "latency", "3.5s", "failover"],
        query_type="simple",
        difficulty="easy",
        notes="Specific metric from timeline"
    ),
    
    TestQuery(
        query="How quickly was the public AWS credential accessed after being committed to the repository?",
        expected_sources=["KB-065"],
        expected_topics=["4 minutes", "scraped", "public repository"],
        query_type="simple",
        difficulty="easy",
        notes="Timeline detail from security incident"
    ),
    
    TestQuery(
        query="What preventive measure was recommended after the unverified runbook command error?",
        expected_sources=["KB-061"],
        expected_topics=["restricted scripting", "versioned scripts", "safety checks"],
        query_type="simple",
        difficulty="medium",
        notes="Prevention recommendation from postmortem"
    ),
    
    TestQuery(
        query="Why did the regional failover cause a latency spike despite having a warm standby?",
        expected_sources=["KB-056"],
        expected_topics=["20%", "capacity", "CPU saturation", "autoscaler"],
        query_type="complex",
        difficulty="hard",
        notes="Requires understanding capacity planning failure"
    ),
    
    # ============================================================================
    # CATEGORY 6: Comparison & Trade-off Questions
    # ============================================================================
    
    TestQuery(
        query="Compare the benefits of path-based vs. host-based routing according to the documentation.",
        expected_sources=["KB-031"],
        expected_topics=["SSL certificate", "IP address", "DNS", "cost", "complexity"],
        query_type="complex",
        difficulty="medium",
        notes="Comparison query - should contrast both approaches"
    ),
    
    TestQuery(
        query="What are the trade-offs between keeping Region B at 20% vs. 50% capacity?",
        expected_sources=["KB-056"],
        expected_topics=["cost", "latency", "autoscaler", "traffic surge", "capacity"],
        query_type="complex",
        difficulty="hard",
        notes="Cost-performance trade-off analysis"
    ),
    
    TestQuery(
        query="Compare allkeys-lru and volatile-lru eviction policies - when should each be used?",
        expected_sources=["KB-052"],
        expected_topics=["allkeys-lru", "volatile-lru", "TTL", "permanent", "disposable"],
        query_type="complex",
        difficulty="medium",
        notes="Technical comparison with use cases"
    ),
    
    TestQuery(
        query="What is the difference between a Silent Change and an announced change in production?",
        expected_sources=["KB-016"],
        expected_topics=["silent", "visibility", "Slack", "announcement", "incident"],
        query_type="simple",
        difficulty="easy",
        notes="Operational practice comparison"
    ),
    
    TestQuery(
        query="Compare the blast radius of a 5% canary deployment vs. a full immediate rollout.",
        expected_sources=["KB-019"],
        expected_topics=["5%", "blast radius", "canary", "rollout", "impact"],
        query_type="complex",
        difficulty="medium",
        notes="Risk comparison"
    ),
    
    # ============================================================================
    # CATEGORY 7: Configuration & Best Practices
    # ============================================================================
    
    TestQuery(
        query="What eviction policy should be standardized for all production ElastiCache instances?",
        expected_sources=["KB-052"],
        expected_topics=["volatile-lru", "ElastiCache", "production", "standardize"],
        query_type="simple",
        difficulty="easy",
        notes="Specific configuration standard"
    ),
    
    TestQuery(
        query="At what percentage should cache reservation alerts be set, and why?",
        expected_sources=["KB-052"],
        expected_topics=["75%", "alert", "lead time", "vertical scaling"],
        query_type="multi_part",
        difficulty="medium",
        notes="Threshold with reasoning"
    ),
    
    TestQuery(
        query="What is the recommended warm standby capacity for the secondary region?",
        expected_sources=["KB-056"],
        expected_topics=["50%", "warm standby", "capacity", "region"],
        query_type="simple",
        difficulty="easy",
        notes="Capacity planning standard"
    ),
    
    TestQuery(
        query="What tools should be used for schema validation at the SQS consumer entrance?",
        expected_sources=["KB-054"],
        expected_topics=["Pydantic", "Go-Structs", "schema validation"],
        query_type="simple",
        difficulty="easy",
        notes="Specific tool recommendations"
    ),
    
    TestQuery(
        query="What is the proper priority configuration for catch-all rules in ALB?",
        expected_sources=["KB-031"],
        expected_topics=["lowest", "negative priority", "catch-all"],
        query_type="simple",
        difficulty="medium",
        notes="Priority ordering principle"
    ),
    
    TestQuery(
        query="How long should a feature flag be observed in staging before promoting to production?",
        expected_sources=["KB-028"],
        expected_topics=["5 minutes", "error rate", "observe", "staging"],
        query_type="simple",
        difficulty="easy",
        notes="Observation period standard"
    ),
    
    # ============================================================================
    # CATEGORY 8: Cross-Reference Questions
    # ============================================================================
    
    TestQuery(
        query="Which documents reference KB-006?",
        expected_sources=["KB-031", "KB-032", "KB-006"],
        expected_topics=["KB-006", "target group", "microservice", "reference"],
        query_type="complex",
        difficulty="hard",
        notes="Document relationship query - tests cross-referencing"
    ),
    
    TestQuery(
        query="What services are mentioned in connection with the Grafana Dashboard KB-013?",
        expected_sources=["KB-013", "KB-016", "KB-019", "KB-028"],
        expected_topics=["Grafana", "KB-013", "monitoring", "services"],
        query_type="complex",
        difficulty="hard",
        notes="Requires finding all references to KB-013"
    ),
    
    TestQuery(
        query="How many postmortem incidents mention Redis-related issues?",
        expected_sources=["KB-052", "KB-060"],
        expected_topics=["Redis", "postmortem", "cache", "incidents"],
        query_type="complex",
        difficulty="hard",
        notes="Aggregation query across postmortems"
    ),
    
    TestQuery(
        query="Which runbooks are referenced by KB-016 as specific technical playbooks?",
        expected_sources=["KB-016"],
        expected_topics=["KB-017", "KB-035", "runbook", "playbook"],
        query_type="simple",
        difficulty="medium",
        notes="Range reference extraction"
    ),
    
    TestQuery(
        query="What is the relationship between KB-028 and KB-019?",
        expected_sources=["KB-028", "KB-019"],
        expected_topics=["feature flag", "deployment", "canary", "code deployment"],
        query_type="complex",
        difficulty="medium",
        notes="Conceptual relationship between documents"
    ),
    
    # ============================================================================
    # CATEGORY 9: Temporal & Context Questions
    # ============================================================================
    
    TestQuery(
        query="What was the timeline of events during the Black Friday Redis cache exhaustion?",
        expected_sources=["KB-052"],
        expected_topics=["08:00", "08:12", "08:15", "08:20", "09:00", "UTC"],
        query_type="simple",
        difficulty="medium",
        notes="Timeline extraction"
    ),
    
    TestQuery(
        query="How long did the SQS poison pill incident halt order fulfillments?",
        expected_sources=["KB-054"],
        expected_topics=["4 hours", "halted", "fulfillment"],
        query_type="simple",
        difficulty="easy",
        notes="Duration extraction"
    ),
    
    TestQuery(
        query="What is the observation period for error rates after toggling a feature flag?",
        expected_sources=["KB-028"],
        expected_topics=["5 minutes", "error rate", "observe"],
        query_type="simple",
        difficulty="easy",
        notes="Time period specification"
    ),
    
    TestQuery(
        query="When did the system standardize on 64-bit BigInt for primary keys?",
        expected_sources=["KB-064"],
        expected_topics=["standardize", "64-bit", "BigInt", "decision"],
        query_type="simple",
        difficulty="medium",
        notes="Historical decision timing"
    ),
    
    TestQuery(
        query="How long does vertical scaling of Redis take according to the postmortems?",
        expected_sources=["KB-052"],
        expected_topics=["10 minutes", "vertical scaling", "Redis"],
        query_type="simple",
        difficulty="medium",
        notes="Operational timing detail"
    ),
    
    # ============================================================================
    # CATEGORY 10: Synthesis & Analysis
    # ============================================================================
    
    TestQuery(
        query="Explain how the combination of Dead Letter Queues, schema validation, and monitoring would prevent a repeat of KB-054.",
        expected_sources=["KB-054", "KB-042", "KB-013"],
        expected_topics=["DLQ", "schema validation", "monitoring", "poison pill", "prevention"],
        query_type="complex",
        difficulty="hard",
        notes="Multi-solution synthesis - requires connecting multiple concepts"
    ),
    
    TestQuery(
        query="What would be a complete disaster recovery plan based on the incidents and runbooks in the knowledge base?",
        expected_sources=["KB-056", "KB-025", "KB-030", "KB-017", "KB-052"],
        expected_topics=["disaster recovery", "failover", "region", "scaling", "cache"],
        query_type="complex",
        difficulty="hard",
        notes="Synthesis across multiple documents"
    ),
    
    TestQuery(
        query="How do the security practices in KB-032, KB-065, and KB-010 work together to prevent credential compromise?",
        expected_sources=["KB-032", "KB-065", "KB-010"],
        expected_topics=["IAM", "pre-commit", "secrets", "security", "prevention"],
        query_type="complex",
        difficulty="hard",
        notes="Security architecture synthesis"
    ),
    
    TestQuery(
        query="Describe a complete deployment workflow that incorporates runbooks KB-016, KB-019, and KB-028.",
        expected_sources=["KB-016", "KB-019", "KB-028"],
        expected_topics=["runbook", "canary", "feature flag", "deployment", "workflow"],
        query_type="complex",
        difficulty="hard",
        notes="End-to-end workflow synthesis"
    ),
    
    TestQuery(
        query="What are the common themes across all the postmortem incidents regarding monitoring and alerting?",
        expected_sources=["KB-052", "KB-054", "KB-056", "KB-060", "KB-061", "KB-064", "KB-065"],
        expected_topics=["monitoring", "alerting", "prevention", "visibility", "metrics"],
        query_type="complex",
        difficulty="hard",
        notes="Pattern recognition across incidents"
    ),
    
    # ============================================================================
    # CATEGORY 11: Negative Queries (Testing RAG Boundaries)
    # ============================================================================
    
    TestQuery(
        query="What is the procedure for setting up a new Kubernetes cluster from scratch?",
        expected_sources=[],
        expected_topics=["not", "found", "documentation", "unavailable"],
        query_type="out_of_scope",
        difficulty="easy",
        notes="Should recognize absence of Kubernetes setup docs"
    ),
    
    TestQuery(
        query="How should the payment processing service handle PCI compliance?",
        expected_sources=[],
        expected_topics=["not", "found", "documentation", "unavailable"],
        query_type="out_of_scope",
        difficulty="easy",
        notes="PCI compliance not covered in KB"
    ),
    
    TestQuery(
        query="What is the disaster recovery procedure for the customer database?",
        expected_sources=[],
        expected_topics=["not", "found", "specific", "customer database"],
        query_type="out_of_scope",
        difficulty="medium",
        notes="Specific DB recovery not documented"
    ),
    
    TestQuery(
        query="What are the specific Terraform configuration files for the ALB setup?",
        expected_sources=[],
        expected_topics=["not", "found", "Terraform", "configuration"],
        query_type="out_of_scope",
        difficulty="easy",
        notes="Implementation details not in KB"
    ),
    
    TestQuery(
        query="How should the team handle GDPR data deletion requests?",
        expected_sources=[],
        expected_topics=["not", "found", "GDPR", "documentation"],
        query_type="out_of_scope",
        difficulty="easy",
        notes="GDPR procedures not covered"
    ),
    
    TestQuery(
        query="What is the on-call rotation schedule for the operations team?",
        expected_sources=[],
        expected_topics=["not", "found", "rotation", "schedule"],
        query_type="out_of_scope",
        difficulty="easy",
        notes="Operational schedules not in KB"
    ),
    
    TestQuery(
        query="What are the specific API endpoints for the catalog service?",
        expected_sources=[],
        expected_topics=["not", "found", "API", "endpoints"],
        query_type="out_of_scope",
        difficulty="easy",
        notes="API specifications not documented"
    ),
    
    # ============================================================================
    # CATEGORY 12: Edge Cases & Ambiguity
    # ============================================================================
    
    TestQuery(
        query="What should an engineer do if a runbook step fails but there's no troubleshooting section?",
        expected_sources=["KB-016"],
        expected_topics=["stop", "consult", "failed", "troubleshooting"],
        query_type="complex",
        difficulty="hard",
        notes="Edge case handling - requires inference from general guidance"
    ),
    
    TestQuery(
        query="If a feature flag needs to be rolled back, what's the procedure?",
        expected_sources=["KB-028"],
        expected_topics=["toggle", "rollback", "staging", "production"],
        query_type="complex",
        difficulty="medium",
        notes="Reverse procedure - may not be explicitly stated"
    ),
    
    TestQuery(
        query="What happens if both regions fail simultaneously?",
        expected_sources=["KB-056", "KB-025"],
        expected_topics=["region", "failover", "disaster"],
        query_type="complex",
        difficulty="hard",
        notes="Scenario not explicitly covered - tests inference"
    ),
    
    TestQuery(
        query="How should an engineer handle a situation where the Slack announcement requirement conflicts with time-sensitive emergency response?",
        expected_sources=["KB-016"],
        expected_topics=["Slack", "announcement", "emergency", "incident"],
        query_type="complex",
        difficulty="hard",
        notes="Policy conflict scenario"
    ),
    
    TestQuery(
        query="What if a user has been inactive for 89 days - should they be deleted?",
        expected_sources=["KB-032"],
        expected_topics=["90 days", "inactive", "threshold"],
        query_type="complex",
        difficulty="medium",
        notes="Boundary condition testing"
    ),
    
    TestQuery(
        query="If a canary shows identical error rates but different latency, should it proceed?",
        expected_sources=["KB-019"],
        expected_topics=["canary", "error rate", "latency", "metrics"],
        query_type="complex",
        difficulty="hard",
        notes="Ambiguous scenario - not explicitly covered"
    ),
    
    # ============================================================================
    # CATEGORY 13: Specific Technical Details
    # ============================================================================
    
    TestQuery(
        query="What specific error should be monitored after shifting traffic to the canary pod?",
        expected_sources=["KB-019"],
        expected_topics=["5xx", "error rate", "HTTP", "canary"],
        query_type="simple",
        difficulty="easy",
        notes="Specific metric type"
    ),
    
    TestQuery(
        query="What command is used to generate the IAM credential report?",
        expected_sources=["KB-032"],
        expected_topics=["aws iam generate-credential-report", "command"],
        query_type="simple",
        difficulty="easy",
        notes="Exact command syntax"
    ),
    
    TestQuery(
        query="What specific tag in Prometheus should show the new version after deployment?",
        expected_sources=["KB-019"],
        expected_topics=["app_version", "tag", "Prometheus"],
        query_type="simple",
        difficulty="easy",
        notes="Specific metric tag name"
    ),
    
    TestQuery(
        query="After how many failed attempts does SQS move a message to the DLQ?",
        expected_sources=["KB-054"],
        expected_topics=["3", "failed attempts", "DLQ", "SQS"],
        query_type="simple",
        difficulty="easy",
        notes="Specific threshold"
    ),
    
    TestQuery(
        query="What was the CPU saturation percentage during the regional failover incident?",
        expected_sources=["KB-056"],
        expected_topics=["CPU saturation", "EKS", "failover"],
        query_type="simple",
        difficulty="medium",
        notes="May be implied rather than stated"
    ),
    
    TestQuery(
        query="What path pattern is used in the example for adding a new ALB rule?",
        expected_sources=["KB-031"],
        expected_topics=["/api/v2/*", "path", "pattern", "ALB"],
        query_type="simple",
        difficulty="easy",
        notes="Specific example path"
    ),
    
    # ============================================================================
    # CATEGORY 14: Policy & Governance
    # ============================================================================
    
    TestQuery(
        query="What is considered the standard window for IAM user inactivity before deletion?",
        expected_sources=["KB-032"],
        expected_topics=["90 days", "standard", "inactivity", "quarter"],
        query_type="simple",
        difficulty="easy",
        notes="Policy standard"
    ),
    
    TestQuery(
        query="Why is Flag Rot considered a source of technical debt?",
        expected_sources=["KB-028"],
        expected_topics=["flag rot", "technical debt", "hard to reason", "code path"],
        query_type="complex",
        difficulty="medium",
        notes="Concept explanation"
    ),
    
    TestQuery(
        query="What makes a change qualify as Silent according to the documentation?",
        expected_sources=["KB-016"],
        expected_topics=["silent", "no announcement", "visibility", "distributed team"],
        query_type="simple",
        difficulty="medium",
        notes="Definition query"
    ),
    
    TestQuery(
        query="What is meant by Privilege Creep in the context of IAM governance?",
        expected_sources=["KB-032"],
        expected_topics=["privilege creep", "IAM", "permissions", "cleanup"],
        query_type="simple",
        difficulty="medium",
        notes="Term definition"
    ),
    
    TestQuery(
        query="What defines a service account according to the microservices documentation?",
        expected_sources=["KB-006", "KB-032"],
        expected_topics=["service account", "microservice", "IAM", "role"],
        query_type="simple",
        difficulty="medium",
        notes="Concept definition"
    ),
    
    # ============================================================================
    # CATEGORY 15: Causality & Impact Analysis
    # ============================================================================
    
    TestQuery(
        query="What was the causal chain that led to the 10-minute platform outage in KB-060?",
        expected_sources=["KB-060"],
        expected_topics=["cold start", "empty cache", "SQL queries", "overwhelmed", "database"],
        query_type="complex",
        difficulty="hard",
        notes="Requires tracing cause-effect chain"
    ),
    
    TestQuery(
        query="How did the 3.5s latency spike impact business metrics during the regional failover?",
        expected_sources=["KB-056"],
        expected_topics=["40%", "conversion", "latency", "user"],
        query_type="simple",
        difficulty="medium",
        notes="Business impact metric"
    ),
    
    TestQuery(
        query="What was the relationship between the allkeys-lru policy and the deletion of configuration keys?",
        expected_sources=["KB-052"],
        expected_topics=["allkeys-lru", "configuration keys", "TTL", "eviction", "permanent"],
        query_type="complex",
        difficulty="hard",
        notes="Causal relationship explanation"
    ),
    
    TestQuery(
        query="How did the lack of a try-catch block create an infinite loop in KB-054?",
        expected_sources=["KB-054"],
        expected_topics=["crash", "acknowledged", "SQS", "returned", "loop"],
        query_type="complex",
        difficulty="medium",
        notes="Technical causality"
    ),
    
    TestQuery(
        query="What was the connection between keeping Region B at 20% capacity and the autoscaler delay?",
        expected_sources=["KB-056"],
        expected_topics=["20%", "capacity", "surge", "autoscaler", "provisions"],
        query_type="complex",
        difficulty="hard",
        notes="Capacity planning causality"
    ),
    
    # ============================================================================
    # CATEGORY 16: Validation & Testing Questions
    # ============================================================================
    
    TestQuery(
        query="How can you verify that a canary deployment was successful?",
        expected_sources=["KB-019"],
        expected_topics=["app_version", "100%", "5xx", "validation"],
        query_type="simple",
        difficulty="medium",
        notes="Success criteria"
    ),
    
    TestQuery(
        query="What health checks should be performed before making changes according to KB-016?",
        expected_sources=["KB-016"],
        expected_topics=["Grafana", "KB-013", "health", "verify state"],
        query_type="simple",
        difficulty="medium",
        notes="Pre-change validation"
    ),
    
    TestQuery(
        query="How should an engineer validate that all pods are running the new version after deployment?",
        expected_sources=["KB-019"],
        expected_topics=["app_version", "Prometheus", "tag", "100%"],
        query_type="simple",
        difficulty="medium",
        notes="Deployment verification"
    ),
    
    TestQuery(
        query="What metrics indicate that a regional failover was successful?",
        expected_sources=["KB-056", "KB-025"],
        expected_topics=["latency", "traffic", "Route 53", "region"],
        query_type="complex",
        difficulty="hard",
        notes="Success metrics for complex operation"
    ),
    
    TestQuery(
        query="How can you verify that an IAM user has been properly deleted?",
        expected_sources=["KB-032"],
        expected_topics=["IAM", "deleted", "access keys", "revoke"],
        query_type="simple",
        difficulty="medium",
        notes="Deletion verification"
    ),
    
    # ============================================================================
    # CATEGORY 17: Metric & Threshold Questions
    # ============================================================================
    
    TestQuery(
        query="At what memory percentage does Redis begin evicting keys with allkeys-lru?",
        expected_sources=["KB-052"],
        expected_topics=["100%", "memory", "eviction", "allkeys-lru"],
        query_type="simple",
        difficulty="medium",
        notes="Specific threshold behavior"
    ),
    
    TestQuery(
        query="How many concurrent SQL queries overwhelmed the database in KB-060?",
        expected_sources=["KB-060"],
        expected_topics=["15,000", "concurrent", "SQL", "overwhelmed"],
        query_type="simple",
        difficulty="easy",
        notes="Specific metric"
    ),
    
    TestQuery(
        query="What was the traffic multiplier during the Black Friday spike?",
        expected_sources=["KB-052"],
        expected_topics=["15x", "baseline", "traffic", "spike"],
        query_type="simple",
        difficulty="easy",
        notes="Traffic metric"
    ),
    
    TestQuery(
        query="What percentage drop in user conversion occurred during the regional failover?",
        expected_sources=["KB-056"],
        expected_topics=["40%", "conversion", "drop"],
        query_type="simple",
        difficulty="easy",
        notes="Business impact metric"
    ),
    
    TestQuery(
        query="How long should error rates be observed after enabling a feature flag?",
        expected_sources=["KB-028"],
        expected_topics=["5 minutes", "error rate", "observe"],
        query_type="simple",
        difficulty="easy",
        notes="Observation duration"
    ),
    
    TestQuery(
        query="What is the maximum capacity of 32-bit integers mentioned in KB-064?",
        expected_sources=["KB-064"],
        expected_topics=["2.1 billion", "32-bit", "cap"],
        query_type="simple",
        difficulty="easy",
        notes="Technical limit"
    ),
    
    # ============================================================================
    # CATEGORY 18: Tool & Technology Specific
    # ============================================================================
    
    TestQuery(
        query="What tools are mentioned for secret scanning in pre-commit hooks?",
        expected_sources=["KB-065"],
        expected_topics=["Trufflehog", "Gitleaks", "pre-commit"],
        query_type="simple",
        difficulty="easy",
        notes="Specific tool names"
    ),
    
    TestQuery(
        query="What feature management dashboard is mentioned for toggling flags?",
        expected_sources=["KB-028"],
        expected_topics=["Feature Management", "dashboard", "portal"],
        query_type="simple",
        difficulty="easy",
        notes="Tool identification"
    ),
    
    TestQuery(
        query="Where should validation metrics be checked during canary deployments?",
        expected_sources=["KB-019", "KB-013"],
        expected_topics=["Prometheus", "Grafana", "KB-013"],
        query_type="simple",
        difficulty="easy",
        notes="Tool/location for metrics"
    ),
    
    TestQuery(
        query="What console or tool is used to edit ALB listener rules?",
        expected_sources=["KB-031"],
        expected_topics=["ALB console", "Terraform", "listener"],
        query_type="simple",
        difficulty="easy",
        notes="Management interface"
    ),
    
    TestQuery(
        query="What autoscaler is mentioned in relation to the regional failover incident?",
        expected_sources=["KB-056", "KB-015"],
        expected_topics=["Horizontal Pod Autoscaler", "autoscaler", "EKS"],
        query_type="simple",
        difficulty="medium",
        notes="Specific autoscaler type"
    ),
    
    # ============================================================================
    # CATEGORY 19: Incident Prevention
    # ============================================================================
    
    TestQuery(
        query="Based on the postmortems, what are the top 3 preventive measures to avoid cache-related incidents?",
        expected_sources=["KB-052", "KB-060"],
        expected_topics=["volatile-lru", "cache warm-up", "alert", "75%", "monitoring"],
        query_type="complex",
        difficulty="hard",
        notes="Synthesis of prevention strategies"
    ),
    
    TestQuery(
        query="What preventive controls would stop a repeat of the public credential disclosure?",
        expected_sources=["KB-065"],
        expected_topics=["pre-commit hooks", "Trufflehog", "Gitleaks", "scan", "local"],
        query_type="simple",
        difficulty="medium",
        notes="Prevention from postmortem"
    ),
    
    TestQuery(
        query="How can the Thundering Herd effect be prevented based on the knowledge base?",
        expected_sources=["KB-060", "KB-030", "KB-052"],
        expected_topics=["cache warm-up", "pre-load", "cold start", "DLQ"],
        query_type="complex",
        difficulty="hard",
        notes="Prevention strategy synthesis"
    ),
    
    TestQuery(
        query="What measures prevent catastrophic manual errors during runbook execution?",
        expected_sources=["KB-061", "KB-016"],
        expected_topics=["restricted scripting", "versioned scripts", "safety checks", "announcement"],
        query_type="complex",
        difficulty="medium",
        notes="Multiple prevention layers"
    ),
    
    TestQuery(
        query="What architectural decisions help limit the Blast Radius of service compromises?",
        expected_sources=["KB-032", "KB-019"],
        expected_topics=["scoped permissions", "least privilege", "canary", "5%"],
        query_type="complex",
        difficulty="hard",
        notes="Security architecture principles"
    ),
    
    # ============================================================================
    # CATEGORY 20: Complex Scenario Questions
    # ============================================================================
    
    TestQuery(
        query="A new engineer needs to deploy a service update during peak hours. What should they do based on all available guidance?",
        expected_sources=["KB-016", "KB-019", "KB-028"],
        expected_topics=["announce", "canary", "5%", "observe", "validation"],
        query_type="multi_part",
        difficulty="hard",
        notes="End-to-end scenario requiring multiple runbooks"
    ),
    
    TestQuery(
        query="You notice Redis memory at 76% during normal traffic. What actions should you take and why?",
        expected_sources=["KB-052", "KB-017"],
        expected_topics=["75%", "alert", "vertical scaling", "lead time", "action"],
        query_type="complex",
        difficulty="hard",
        notes="Proactive action based on threshold"
    ),
    
    TestQuery(
        query="A feature flag has been enabled in production for 18 months. What should happen next and why?",
        expected_sources=["KB-028"],
        expected_topics=["cleanup ticket", "remove", "flag rot", "technical debt", "2 years"],
        query_type="complex",
        difficulty="hard",
        notes="CRITICAL TEST - This is the question from our earlier conversation"
    ),
    
    TestQuery(
        query="During a deployment, the canary shows a 0.1% increase in errors. Should you proceed? What factors matter?",
        expected_sources=["KB-019"],
        expected_topics=["error rate", "identical", "canary", "observe", "decision"],
        query_type="complex",
        difficulty="hard",
        notes="Decision-making scenario with ambiguous data"
    ),
    
    TestQuery(
        query="An IAM user has been inactive for 85 days but is about to return from extended leave. What should you do?",
        expected_sources=["KB-032"],
        expected_topics=["90 days", "threshold", "inactive", "policy"],
        query_type="complex",
        difficulty="hard",
        notes="Edge case requiring policy interpretation"
    ),
]

def get_test_dataset() -> List[TestQuery]:
    """Return full test dataset"""
    return TEST_DATASET

def get_test_subset(query_type: Optional[str] = None, 
                    difficulty: Optional[str] = None) -> List[TestQuery]:
    """Get filtered subset of test dataset"""
    dataset = TEST_DATASET
    
    if query_type:
        dataset = [q for q in dataset if q.query_type == query_type]
    
    if difficulty:
        dataset = [q for q in dataset if q.difficulty == difficulty]
    
    return dataset

if __name__ == "__main__":
    test_subset = get_test_dataset()
    min_val = 5
    max_val = 1
    for query in test_subset:
        print(f"Query: {query.query}")
        print(f"Expected Sources: {query.expected_sources}")
        min_val = min(min_val, len(query.expected_sources))
        max_val = max(max_val, len(query.expected_sources))
        if len(query.expected_sources) > 5:
            print(f"More than 5 expected sources: {query.query}")
        print(f"Expected Topics: {query.expected_topics}")
        print("-" * 50)
    print(f"Min expected sources: {min_val}")
    print(f"Max expected sources: {max_val}")