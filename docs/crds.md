# CRD Extensions

This directory contains Level 3 Kubernetes extensions using Custom Resource Definitions from production-grade operators.

## Components

### Nginx Ingress Controller

Exposes n8n externally via NodePort (30080/30443) on the worker node. Uses `IngressClass` to allow multiple ingress controllers to coexist.

```bash
# Install
kubectl apply -f k8s/07-crds/nginx-ingress.yaml

# Access n8n after cert-manager setup
curl -k https://192.168.64.5:30443 -H "Host: n8n.kubeintel.local"
```

### cert-manager

Automates TLS certificate lifecycle using CRDs.

Objects used:
- `ClusterIssuer` (selfsigned-issuer) — root CA for the lab
- `Certificate` (kubeintel-ca) — self-signed CA cert
- `ClusterIssuer` (kubeintel-ca-issuer) — issues certs signed by the CA
- `Certificate` (n8n-tls) — TLS cert for n8n.kubeintel.local

```bash
# Install cert-manager
kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.16.2/cert-manager.yaml
kubectl wait --namespace cert-manager \
  --for=condition=ready pod \
  --selector=app.kubernetes.io/instance=cert-manager \
  --timeout=120s

# Apply issuers and certificates
kubectl apply -f k8s/07-crds/cert-manager-issuer.yaml

# Verify certificate issued
kubectl get certificate -n kubeintel
kubectl describe certificate n8n-tls -n kubeintel
```

### n8n Ingress with TLS

Routes `n8n.kubeintel.local` through Nginx Ingress to the n8n service with TLS termination. Includes WebSocket proxy headers required by n8n.

Add to `/etc/hosts` on your Mac to access via browser:
```
192.168.64.5  n8n.kubeintel.local
```

Then open: `https://n8n.kubeintel.local:30443`

### Argo CD

GitOps continuous delivery. The `Application` CRD points at this repository and automatically syncs the `k8s/` directory to the cluster.

```bash
# Install Argo CD
kubectl create namespace argocd
kubectl apply -n argocd \
  -f https://raw.githubusercontent.com/argoproj/argo-cd/v2.13.0/manifests/install.yaml

kubectl wait --namespace argocd \
  --for=condition=ready pod \
  --selector=app.kubernetes.io/name=argocd-server \
  --timeout=180s

# Apply the Application CRD
kubectl apply -f k8s/07-crds/argocd-application.yaml

# Get admin password
kubectl -n argocd get secret argocd-initial-admin-secret \
  -o jsonpath="{.data.password}" | base64 -d

# Access UI
kubectl port-forward svc/argocd-server -n argocd 8080:443
# Open: https://localhost:8080
```

Once synced, any `git push` to `main` automatically reconciles the cluster state.

## CRDs Demonstrated

| CRD | API Group | Purpose |
|-----|-----------|---------|
| `Certificate` | cert-manager.io/v1 | Declarative TLS certificate lifecycle |
| `ClusterIssuer` | cert-manager.io/v1 | Cluster-wide certificate authority |
| `Application` | argoproj.io/v1alpha1 | GitOps sync from Git to cluster |
| `Ingress` | networking.k8s.io/v1 | HTTP/HTTPS routing (native K8s) |
| `IngressClass` | networking.k8s.io/v1 | Ingress controller selection |
