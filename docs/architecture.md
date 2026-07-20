# Architecture

## System Overview

KubeIntel is an AI-powered cybersecurity research digest platform. It automates the collection, summarization, and delivery of curated AI and security research.

```
┌─────────────────────────────────────────────────────────┐
│                  kubeintel namespace                     │
│                                                          │
│  ┌─────────────┐     ┌──────────────────┐               │
│  │     n8n     │────▶│  summarizer-api  │               │
│  │  (workflow) │     │  (LLM backend)   │               │
│  └─────────────┘     └────────┬─────────┘               │
│                               │                          │
│                       ┌───────▼──────┐                   │
│                       │  PostgreSQL  │                   │
│                       │ (StatefulSet)│                   │
│                       └──────────────┘                   │
│                                                          │
│  ┌────────────────────────────────────────────────────┐  │
│  │               NetworkPolicy boundary               │  │
│  └────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
```

## Components

### n8n
- Workflow automation engine
- Collects research signals from RSS feeds and security APIs
- Triggers summarizer-api for each item
- Deployed as a Kubernetes Deployment with a PVC for workflow persistence

### summarizer-api
- Custom Python FastAPI service
- Sends collected content to an LLM (Claude API) for summarization
- Returns structured summaries to n8n
- Deployed as a Kubernetes Deployment with HPA for scaling

### PostgreSQL
- Stores research items, summaries, and digest history
- Deployed as a StatefulSet with a PersistentVolumeClaim
- Accessed only by n8n and summarizer-api via NetworkPolicy

## Kubernetes Resource Map

```
kubeintel (Namespace)
├── postgres (StatefulSet)
│   ├── postgres-pvc (PersistentVolumeClaim)
│   ├── postgres-secret (Secret)
│   ├── postgres-config (ConfigMap)
│   └── postgres-svc (Service — headless)
├── summarizer-api (Deployment)
│   ├── summarizer-config (ConfigMap)
│   ├── summarizer-secret (Secret — API key)
│   └── summarizer-svc (Service — ClusterIP)
├── n8n (Deployment)
│   ├── n8n-pvc (PersistentVolumeClaim)
│   ├── n8n-config (ConfigMap)
│   └── n8n-svc (Service — ClusterIP + Ingress)
├── NetworkPolicies
│   ├── default-deny-all
│   ├── allow-n8n-to-summarizer
│   ├── allow-n8n-to-postgres
│   └── allow-summarizer-to-postgres
└── RBAC
    ├── kubeintel-sa (ServiceAccount)
    ├── kubeintel-role (Role)
    └── kubeintel-rolebinding (RoleBinding)
```

## Network Design

- Default-deny NetworkPolicy applied to the namespace
- Explicit allow policies per communication path
- n8n is the only component exposed externally via Ingress
- PostgreSQL has no external exposure — ClusterIP only

## Storage Design

| Component  | Storage Class | Access Mode    | Size  |
|------------|---------------|----------------|-------|
| PostgreSQL | local-path    | ReadWriteOnce  | 5Gi   |
| n8n        | local-path    | ReadWriteOnce  | 2Gi   |
