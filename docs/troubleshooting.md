# Troubleshooting Notes

Real issues hit during cluster setup, with root cause analysis and fixes.

---

## Issue 1 — Pod CIDR Overlap with UTM Guest Network

### Symptom

After installing Calico with `192.168.0.0/16` as the pod CIDR, SSH connectivity from the host to the VMs became unreliable. Routes were being mismatched.

### Root Cause

The UTM guest network is `192.168.64.0/24`. The initial pod CIDR `192.168.0.0/16` is a supernet that includes `192.168.64.x`. Calico injected routes that shadowed the VM network routes.

### Fix

Reset the cluster and reinitialize with a non-overlapping pod CIDR:

```bash
sudo kubeadm reset -f
sudo kubeadm init \
  --apiserver-advertise-address=192.168.64.3 \
  --pod-network-cidr=10.244.0.0/16
```

### Lesson

Always check that your pod CIDR does not overlap with:
- Host machine network
- VM/hypervisor guest network
- VPN ranges (if applicable)
- Cloud VPC CIDR (for future hybrid setups)

`10.244.0.0/16` (Flannel default) and `192.168.0.0/16` (Calico default) both conflict with common LAN ranges. `10.244.0.0/16` was safe here.

---

## Issue 2 — Swap Re-enabled After Reboot

### Symptom

kubeadm init failed or kubelet refused to start after a VM reboot with an error about swap being enabled.

### Root Cause

`sudo swapoff -a` disables swap for the current session only. The swap entry in `/etc/fstab` was still present, so it was re-mounted on reboot.

### Fix

```bash
sudo swapoff -a
sudo sed -i '/ swap / s/^/#/' /etc/fstab
swapon --show   # should return empty
```

### Lesson

For kubeadm clusters, swap must be persistently disabled unless Kubernetes is configured with `--fail-swap-on=false` (not recommended for production).

---

## Issue 3 — Worker Join Failed Due to Certificate Time Drift

### Symptom

kubeadm join reached the API server on port 6443 but failed during TLS handshake:

```
x509: certificate has expired or is not yet valid:
current time is before certificate validity start time
```

### Root Cause

The worker node clock was behind the control-plane by enough to fall outside the certificate validity window. Kubernetes TLS certificates are time-sensitive.

### Fix

Install and force-sync Chrony on both nodes:

```bash
sudo apt install -y chrony
sudo systemctl enable --now chrony
sudo chronyc makestep
```

Then regenerate the join token and retry:

```bash
# on control-plane
kubeadm token create --print-join-command

# on worker
sudo kubeadm reset -f
sudo kubeadm join ...
```

### Lesson

All nodes in a Kubernetes cluster must have synchronized clocks. In production this is enforced via NTP (chrony, timesyncd). Certificate validation, etcd consensus, and audit logs all depend on accurate time.
