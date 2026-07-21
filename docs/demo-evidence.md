# KubeIntel Demo Evidence

## Milestone 2: Scheduled AI/Cybersecurity Vulnerability Digest

KubeIntel now runs an automated n8n workflow inside Kubernetes.

Workflow:

```text
Weekly Schedule
  -> Fetch NVD CVEs
  -> Prepare NVD Item
  -> Summarize via Claude
  -> Store in PostgreSQL
  -> Build Digest JSON
  -> Get Current File SHA
  -> Push to GitHub
