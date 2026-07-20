# Cluster Setup — kubeadm on UTM ARM64

## Environment

| Node              | Role          | IP             | OS                    | Runtime    |
|-------------------|---------------|----------------|-----------------------|------------|
| k8s-control-plane | control-plane | 192.168.64.3   | Ubuntu 26.04 LTS ARM64 | containerd |
| k8s-worker-1      | worker        | 192.168.64.5   | Ubuntu 26.04 LTS ARM64 | containerd |

Both VMs created in UTM on Apple Silicon (M1). No cloud provider — bare-metal equivalent.

---

## Prerequisites (both nodes)

```bash
# disable swap immediately
sudo swapoff -a

# remove swap from persistent config
sudo sed -i '/ swap / s/^/#/' /etc/fstab

# verify
swapon --show

# load required kernel modules
sudo modprobe overlay
sudo modprobe br_netfilter

# persist kernel modules
cat <<EOF | sudo tee /etc/modules-load.d/k8s.conf
overlay
br_netfilter
EOF

# configure sysctl for Kubernetes networking
cat <<EOF | sudo tee /etc/sysctl.d/k8s.conf
net.bridge.bridge-nf-call-iptables  = 1
net.bridge.bridge-nf-call-ip6tables = 1
net.ipv4.ip_forward                 = 1
EOF

sudo sysctl --system
```

---

## containerd Installation (both nodes)

```bash
sudo apt update
sudo apt install -y containerd

sudo mkdir -p /etc/containerd
containerd config default | sudo tee /etc/containerd/config.toml

# enable systemd cgroup driver — required for kubeadm
sudo sed -i 's/SystemdCgroup = false/SystemdCgroup = true/' /etc/containerd/config.toml

sudo systemctl restart containerd
sudo systemctl enable containerd
```

---

## kubeadm, kubelet, kubectl Installation (both nodes)

```bash
sudo apt install -y apt-transport-https ca-certificates curl gpg

curl -fsSL https://pkgs.k8s.io/core:/stable:/v1.36/deb/Release.key \
  | sudo gpg --dearmor -o /etc/apt/keyrings/kubernetes-apt-keyring.gpg

echo 'deb [signed-by=/etc/apt/keyrings/kubernetes-apt-keyring.gpg] \
  https://pkgs.k8s.io/core:/stable:/v1.36/deb/ /' \
  | sudo tee /etc/apt/sources.list.d/kubernetes.list

sudo apt update
sudo apt install -y kubeadm kubelet kubectl
sudo apt-mark hold kubeadm kubelet kubectl
```

---

## Cluster Initialization (control-plane only)

```bash
sudo kubeadm init \
  --apiserver-advertise-address=192.168.64.3 \
  --pod-network-cidr=10.244.0.0/16
```

> Pod CIDR `10.244.0.0/16` was chosen to avoid overlap with the UTM guest network `192.168.64.0/24`.
> See [troubleshooting.md](troubleshooting.md) for the full story.

Set up kubeconfig for the local user:

```bash
mkdir -p $HOME/.kube
sudo cp /etc/kubernetes/admin.conf $HOME/.kube/config
sudo chown $(id -u):$(id -g) $HOME/.kube/config
```

---

## Calico CNI Installation (control-plane only)

```bash
kubectl create -f https://raw.githubusercontent.com/projectcalico/calico/v3.28.0/manifests/tigera-operator.yaml

kubectl create -f https://raw.githubusercontent.com/projectcalico/calico/v3.28.0/manifests/custom-resources.yaml
```

Wait for nodes to become Ready:

```bash
watch kubectl get nodes
```

---

## Worker Node Join (worker node)

On control-plane, generate a fresh join token:

```bash
kubeadm token create --print-join-command
```

Run the printed command on k8s-worker-1:

```bash
sudo kubeadm join 192.168.64.3:6443 \
  --token <token> \
  --discovery-token-ca-cert-hash sha256:<hash>
```

---

## Validation

```bash
kubectl get nodes -o wide
kubectl get pods -A
```

Expected output:

```
NAME                STATUS   ROLES           AGE
k8s-control-plane   Ready    control-plane   ...
k8s-worker-1        Ready    <none>          ...
```
