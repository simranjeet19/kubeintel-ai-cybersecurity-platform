# KubeIntel — AI & Cybersecurity Research Digest Platform

A self-managed Kubernetes platform that runs an AI-powered cybersecurity research digest workflow. The system collects security and AI research signals, summarizes them using an LLM-backed API, stores results in PostgreSQL, and delivers curated digests.

Built to demonstrate production-style Kubernetes administration, DevSecOps practices, and platform engineering using a bare-metal kubeadm cluster.

---

## Why This Project

Most portfolio Kubernetes projects stop at deploying a simple web app on managed cloud (EKS, GKE). KubeIntel is different:

- Cluster bootstrapped from scratch using kubeadm on bare-metal ARM64 VMs
- Real operational concerns: storage, network isolation, RBAC, health management
- Security-first design: NetworkPolicies, Secrets management, least-privilege RBAC
- Progressive CRD adoption: cert-manager, Argo CD, Prometheus Operator
- AI integration: LLM-backed summarizer API as a core workload

---

## Architecture

```
Research Sources (RSS / APIs)
          |
          v
   n8n Workflow Engine          ← orchestrates data collection
          |
          v
   Summarizer API               ← LLM-backed summarization service
          |
          v
      PostgreSQL                ← persistent storage (StatefulSet + PVC)
          |
          v
    Email Digest / Dashboard
```

---

## Cluster Environment

| Component       | Detail                          |
|-----------------|---------------------------------|
| Platform        | MacBook Pro M1 — UTM hypervisor |
| OS              | Ubuntu 26.04 LTS ARM64          |
| Kubernetes      | v1.36.2                         |
| Container Runtime | containerd                    |
| CNI             | Calico (pod CIDR: 10.244.0.0/16)|
| Nodes           | 1 control-plane + 1 worker      |

---

## Project Status

### Level 1 — CKA Core

- [x] Bootstrap kubeadm cluster (control-plane + worker)
- [x] Configure containerd runtime
- [x] Install Calico CNI
- [x] Verify node readiness
- [ ] Namespace
- [ ] PostgreSQL StatefulSet + PVC
- [ ] Summarizer API Deployment
- [ ] n8n Deployment + PVC
- [ ] Services (ClusterIP + headless)
- [ ] ConfigMaps and Secrets
- [ ] NetworkPolicies
- [ ] RBAC + ServiceAccounts
- [ ] Liveness and readiness probes
- [ ] Resource requests and limits
- [ ] CronJob (backup / digest trigger)

### Level 2 — Production Hardening

- [ ] Helm chart / Kustomize overlays
- [ ] Horizontal Pod Autoscaler
- [ ] metrics-server
- [ ] Prometheus + Grafana

### Level 3 — CRD Extensions

- [ ] cert-manager (TLS automation)
- [ ] Argo CD (GitOps delivery)
- [ ] Prometheus Operator (ServiceMonitor, PrometheusRule)
- [ ] External Secrets Operator

---

## Repository Structure

```
kubeintel-ai-cybersecurity-platform/
├── docs/                        # architecture, setup, troubleshooting, security design
├── k8s/
│   ├── 00-namespace/
│   ├── 01-postgres/
│   ├── 02-summarizer-api/
│   ├── 03-n8n/
│   ├── 04-networking/
│   ├── 05-rbac/
│   ├── 06-observability/
│   └── 07-crds/
├── scripts/                     # cluster ops scripts
├── workflows/                   # n8n workflow exports
└── screenshots/                 # cluster validation screenshots
```

---

## Kubernetes Concepts Demonstrated

- kubeadm cluster bootstrap and node join
- containerd runtime configuration
- CNI installation and pod networking
- Deployments, StatefulSets, CronJobs
- PersistentVolumes and PersistentVolumeClaims
- Services (ClusterIP, Headless)
- Ingress
- ConfigMaps and Secrets
- NetworkPolicies (default-deny + allowlist)
- RBAC and ServiceAccounts
- Liveness and readiness probes
- Resource requests and limits
- Horizontal Pod Autoscaler
- CRD-based platform extensions

---

## Running the Platform

See [docs/cluster-setup.md](docs/cluster-setup.md) for full cluster setup steps.

To apply manifests:

```bash
kubectl apply -f k8s/00-namespace/
kubectl apply -f k8s/01-postgres/
kubectl apply -f k8s/02-summarizer-api/
kubectl apply -f k8s/03-n8n/
kubectl apply -f k8s/04-networking/
kubectl apply -f k8s/05-rbac/
```

---

## Security Design

See [docs/security-design.md](docs/security-design.md) for full security design notes covering:

- Network segmentation via NetworkPolicies
- Secrets management approach
- RBAC least-privilege model
- TLS automation with cert-manager
