# GitOps Workflow with Argo CD

This folder contains the declarative GitOps delivery definitions for the TaskBoard project using **Argo CD**.

---

## 1. What is GitOps?

GitOps is an operational framework that takes DevOps best practices used for application development (such as version control, collaboration, compliance, and CI/CD) and applies them to infrastructure and application deployment automation.

### Core Principles
1. **Declarative Descriptions**: The entire system state is described declaratively using Git (Helm charts, Kubernetes manifests).
2. **Git as the Single Source of Truth**: The desired state is version-controlled and immutable in Git.
3. **Automated Continuous Reconciliation**: An agent (Argo CD) continuously monitors the active cluster state and compares it against Git. If drift occurs (e.g. manual `kubectl edit` or pod failure), Argo CD automatically brings the cluster back in sync (`selfHeal: true`).
4. **Pull-based Deployment Model**: The cluster pulls its desired state from Git rather than external CI pipelines pushing credentials directly into Kubernetes.

---

## 2. Architecture & Flow

```text
[Developer]
    │ git push
    ▼
[GitHub Repository] (Source of Truth)
    │
    │ Webhook / Poll (every 3m)
    ▼
[Argo CD Controller] ──(Reconcile Loop)──► [Kubernetes Cluster]
    ▲                                              │
    └──────── Compare Desired vs Live State ───────┘
```

---

## 3. Directory Layout

- `application.yaml`: Registers the `taskboard` application with Argo CD, mapping the Git repository path `session21-python/helm/taskboard` to the `taskboard` Kubernetes namespace.
- `app-of-apps.yaml`: Root application manifest implementing the Argo CD "App of Apps" pattern to manage all sub-applications declaratively.

---

## 4. Setup & Deployment Instructions

### Step 1: Install Argo CD on your cluster
```bash
# Create namespace
kubectl create namespace argocd

# Install official Argo CD manifests
kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml

# Wait for Argo CD pods to become ready
kubectl wait --for=condition=ready pod --all -n argocd --timeout=300s
```

### Step 2: Access the Argo CD UI
```bash
# Port-forward UI to localhost:8080
kubectl port-forward svc/argocd-server -n argocd 8080:443

# Retrieve initial admin password
kubectl -n argocd get secret argocd-initial-admin-secret -o jsonpath="{.data.password}" | base64 -d
echo ""
```
Login via browser at `https://localhost:8080` with username `admin`.

### Step 3: Deploy the TaskBoard GitOps Application
```bash
# Apply the application CRD
kubectl apply -f session21-python/gitops/application.yaml

# Check application status
kubectl get applications -n argocd

# Describe application synchronization details
kubectl describe application taskboard -n argocd
```

### Step 4: Verify Automated Self-Healing & Drift Detection
```bash
# Intentionally cause configuration drift by scaling down manually
kubectl scale deployment taskboard-backend --replicas=0 -n taskboard

# Observe Argo CD detecting drift and automatically reconciling back to 2 replicas:
kubectl get pods -n taskboard -w
```
