---
doc_id: KB-044
doc_type:
  - operations
service: eks
date: 2024-03-15
---
### KB-044: Incident Response: Kubernetes Pod CrashLoopBackOff
#### Symptoms and Alerts

- **Alert:** k8s\_pod\_restart\_rate\_high.
- **Symptoms:** kubectl get pods shows status CrashLoopBackOff.

#### Resolution Steps

1. **Describe Pod:** Run kubectl describe pod &lt;pod-name&gt; to check the "Events" section for OOMKilled or LivenessProbe failures.
2. **Check Logs:** Use kubectl logs &lt;pod-name&gt; --previous to see why the application crashed in its last incarnation.
3. **Adjust Resources:** If OOMKilled, increase the memory limits in the deployment manifest (KB-020).
4. **Fix Config:** If it's a configuration error, revert the latest ConfigMap change.

#### Decisions &amp; Reasoning

- **Decision:** Mandatory use of --previous when checking crash logs.
- **Reasoning:** When a pod crashes, the current log is empty because the container just started. The --previous flag fetches the logs from the *failed* container, which is the only place the error message (e.g., NullPointerException) will exist.
- **Decision:** Liveness probes must be "Graceful."
- **Reasoning:** A liveness probe that is too aggressive can kill a pod that is simply doing a heavy startup task. We implement an initialDelaySeconds of 30 to give the application time to warm up its cache (KB-030) before Kubernetes starts checking its health.