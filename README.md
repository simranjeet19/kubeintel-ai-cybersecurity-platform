# KubeIntel — AI & Cybersecurity Research Digest Platform

A self-managed Kubernetes platform that runs an AI-powered cybersecurity research digest workflow. The system collects security and AI research, summarises it using the Claude API, stores results in PostgreSQL, and publishes a weekly digest to GitHub — automatically updating a live portfolio feed.

Built to demonstrate production-style Kubernetes administration, DevSecOps practices, and platform engineering on a bare-metal kubeadm cluster.

---

## Architecture

```
n8n Workflow Engine
        │
        ▼
summarizer-api (FastAPI + Claude API)
        │
        ▼
PostgreSQL (StatefulSet + PVC)
        │
        ▼
digest-exporter CronJob → kubeintel-digests (GitHub) → cyberwithsimran.com
```

All workloads run in the `kubeintel` namespace with default-deny NetworkPolicies and explicit allow rules per communication path.

---

## Cluster Environment

| Component          | Detail                              |
|--------------------|-------------------------------------|
| Platform           | MacBook Pro M1 — UTM hypervisor     |
| OS                 | Ubuntu 26.04 LTS ARM64              |
| Kubernetes         | v1.36.2                             |
| Container Runtime  | containerd                          |
| CNI                | Calico (pod CIDR: 10.244.0.0/16)   |
| Nodes              | 1 control-plane + 1 worker          |
| Storage            | local-path provisioner (default)    |

---

## What's Built

### Workloads

| Component         | Kind          | Notes |
|-------------------|---------------|-------|
| postgres          | StatefulSet   | PostgreSQL 16, 5Gi PVC, init SQL schema |
| summarizer-api    | Deployment    | FastAPI + Claude API (claude-opus-4-8), structured JSON logging, pydantic-settings |
| n8n               | Deployment    | Workflow engine, 2Gi PVC, postgres-backed storage, init container |
| digest-exporter   | CronJob       | Runs weekly (Mon 09:00 UTC), reads postgres, pushes digest.json to GitHub |

### Security

| Resource                   | Detail |
|----------------------------|--------|
| NetworkPolicies (10)       | default-deny-all + explicit allow per path |
| ServiceAccounts (3)        | One per workload, `automountServiceAccountToken: false` |
| Roles + RoleBindings (2)   | Namespace-scoped, least-privilege (own ConfigMap + Secret only) |
| Pod security contexts      | `runAsNonRoot`, `readOnlyRootFilesystem`, `drop: ALL` capabilities |
| Secret management          | `stringData` with placeholder values — real values injected at apply time, never committed |
| Container images           | Multi-stage Alpine Dockerfiles, non-root user (uid 1000), pinned tags |

### Repository Structure

```
kubeintel-ai-cybersecurity-platform/
├── docs/                        # cluster-setup, troubleshooting, architecture, security-design
├── digest-exporter/             # Python CronJob — postgres → GitHub
│   ├── exporter.py
│   ├── Dockerfile
│   └── requirements.txt
├── summarizer-api/              # FastAPI service — LLM summarization
│   ├── app/
│   │   ├── main.py
│   │   ├── config.py            # pydantic-settings typed config
│   │   ├── summarizer.py        # Claude API call, asyncio.to_thread
│   │   ├── models.py
│   │   └── logging_config.py   # structured JSON logging
│   ├── Dockerfile
│   └── requirements.txt
├── k8s/
│   ├── 00-namespace/
│   ├── 01-postgres/             # StatefulSet, headless Service, ConfigMap, Secret, init SQL
│   ├── 02-summarizer-api/       # Deployment, Service, ConfigMap, Secret
│   ├── 03-n8n/                  # Deployment, Service, PVC, ConfigMap, Secret
│   ├── 04-networking/           # 10 NetworkPolicy manifests
│   ├── 05-rbac/                 # ServiceAccounts, Roles, RoleBindings
│   ├── 06-digest-exporter/      # CronJob, ConfigMap, Secret, ServiceAccount
│   └── 07-crds/                 # (reserved for cert-manager, Argo CD, Prometheus Operator)
├── workflows/n8n/               # n8n workflow JSON — version-controlled
├── scripts/
│   └── push-workflow.sh         # pushes workflow JSON to n8n via API
└── screenshots/                 # cluster validation screenshots
```

---

## Applying Manifests

```bash
kubectl apply -f k8s/00-namespace/
kubectl apply -f k8s/01-postgres/
kubectl apply -f k8s/02-summarizer-api/
kubectl apply -f k8s/03-n8n/
kubectl apply -f k8s/04-networking/
kubectl apply -f k8s/05-rbac/
kubectl apply -f k8s/06-digest-exporter/
```

Verify:

```bash
kubectl get all -n kubeintel
kubectl get pvc -n kubeintel
kubectl get networkpolicies -n kubeintel
kubectl get cronjobs -n kubeintel
```

---

## Kubernetes Concepts Demonstrated

- kubeadm cluster bootstrap from scratch
- containerd runtime configuration
- Calico CNI with custom pod CIDR
- Deployments, StatefulSets, CronJobs
- PersistentVolumeClaims (ReadWriteOnce)
- Headless and ClusterIP Services
- ConfigMaps + Secrets (envFrom + valueFrom)
- NetworkPolicies (default-deny + allowlist)
- RBAC: ServiceAccounts, Roles, RoleBindings
- Pod security contexts + container security contexts
- Readiness and liveness probes (httpGet + exec)
- Resource requests and limits
- imagePullSecrets (GHCR private registry)
- Init containers (postgres readiness check)
- Multi-stage Dockerfiles (Alpine, non-root)
- Recreate deployment strategy (PVC-backed workload)
- CronJob with concurrencyPolicy and backoffLimit

---

## Security Design

See [docs/security-design.md](docs/security-design.md) for full details.

- Default-deny NetworkPolicy blocks all traffic in the namespace
- Each component has explicit egress and ingress allow rules
- No service can reach another it has no business reaching
- Secrets never committed — placeholder values only in Git
- GitHub token stored in Kubernetes Secret, not in workflow engine
- All containers run as non-root with read-only filesystem

---

## Project Status

### Level 1 — CKA Core ✅
- [x] kubeadm cluster
- [x] PostgreSQL StatefulSet + PVC
- [x] Application Deployments
- [x] Services
- [x] ConfigMaps + Secrets
- [x] NetworkPolicies
- [x] RBAC
- [x] Probes + resource limits
- [x] CronJob

### Level 2 — Production Hardening
- [ ] HPA for summarizer-api
- [ ] metrics-server
- [ ] Prometheus + Grafana

### Level 3 — CRD Extensions
- [ ] cert-manager
- [ ] Argo CD
- [ ] Prometheus Operator
