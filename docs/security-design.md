# Security Design

## Principles

1. **Least privilege** — every component gets only the permissions it needs
2. **Network segmentation** — default-deny, explicit allow-list
3. **Secrets isolation** — no plaintext credentials in manifests or ConfigMaps
4. **Immutable infrastructure** — no exec into pods in production; changes go through Git
5. **Audit trail** — all changes tracked via Git commit history

---

## Network Security — NetworkPolicies

A default-deny policy is applied to the `kubeintel` namespace. All traffic is blocked unless explicitly permitted.

```
default-deny-all         blocks all ingress and egress
allow-n8n-to-summarizer  n8n → summarizer-api on port 8000
allow-n8n-to-postgres    n8n → postgres on port 5432
allow-summarizer-to-postgres  summarizer-api → postgres on port 5432
allow-ingress-to-n8n     ingress controller → n8n on port 5678
```

This means PostgreSQL is unreachable from anything except n8n and summarizer-api, even within the cluster.

---

## Secrets Management

- Kubernetes `Secret` objects used for all credentials (DB password, LLM API key)
- `stringData` used in YAML for readability during development; base64-encoded in cluster
- Secret values are **never committed to Git** — `.gitignore` blocks `*-secret-values.yaml` and `.env`
- Future: migrate to External Secrets Operator pulling from a secrets backend (Vault or cloud KMS)

---

## RBAC Design

A dedicated `ServiceAccount` is created for the KubeIntel workloads.

| Resource       | Verbs                        | Reason                        |
|----------------|------------------------------|-------------------------------|
| pods           | get, list, watch             | health monitoring              |
| configmaps     | get                          | read own config                |
| secrets        | get                          | read own secrets               |

No cluster-level permissions are granted. The `Role` is namespace-scoped to `kubeintel`.

---

## TLS (Level 3)

cert-manager will be used to automate TLS certificate lifecycle:

- `ClusterIssuer` backed by Let's Encrypt (or self-signed CA for lab)
- `Certificate` objects managed declaratively
- Ingress TLS termination handled automatically

---

## Future Security Additions

| Area                  | Tool / Approach                        |
|-----------------------|----------------------------------------|
| External secrets      | External Secrets Operator + Vault      |
| Image scanning        | Trivy in CI pipeline                   |
| Policy enforcement    | Kyverno or OPA Gatekeeper              |
| Runtime security      | Falco                                  |
| mTLS between services | Linkerd or Istio service mesh          |
