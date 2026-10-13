# End-to-End Production DevOps Project: LoanBoard

An enterprise-grade, end-to-end cloud-native DevOps project demonstrating modern software delivery, automated cloud infrastructure provisioning, containerized microservices orchestration, DevSecOps shift-left security, continuous monitoring, and declarative GitOps continuous delivery.

---

## 1. Project Overview

LoanBoard is a full-stack task management microservices application:
- **Backend API**: Python 3.12 with **FastAPI**, **SQLAlchemy**, and **Pydantic** with unit & integration tests written in **pytest**.
- **Frontend SPA**: Modern reactive UI built with **React** + **Vite**, served via a hardened multi-stage **Nginx** Alpine container.
- **Database**: **PostgreSQL 16** with persistent volume storage and automated connection lifecycle management.
- **Cloud Infrastructure**: Modular AWS infrastructure provisioned with **Terraform** (custom VPC with public/private subnets, NAT Gateways, Security Groups, and an AWS EKS Managed Kubernetes cluster).
- **Orchestration**: Kubernetes manifests and reusable, environment-driven **Helm** charts supporting local dev and production profiles.
- **CI/CD Pipeline**: Automated **GitHub Actions** workflows performing automated testing, multi-arch Docker image builds, security scanning, GHCR publishing, and deployment triggers.
- **DevSecOps**: Multi-layer security gates integrating **SAST** (Bandit), **SCA** (Trivy), **Secret Scanning** (Gitleaks), and **Container Vulnerability Scanning** with automated build blocking on HIGH/CRITICAL CVEs.
- **Monitoring & Observability**: **Prometheus Operator** and **Grafana** stack with custom `ServiceMonitor` definitions, metric scraping, and pre-built health and resource dashboards.
- **GitOps Delivery**: Continuous reconciliation, drift detection, and automated self-healing powered by **Argo CD**.
- **Troubleshooting**: Diagnostic lab solving real-world Kubernetes failure modes (`ImagePullBackOff` and broken service selectors).

---

## 2. Architecture Diagram

```text
=============================================================================================================
                                     DEVELOPER WORKFLOW & GITOPS LIFECYCLE
=============================================================================================================

 [Developer]
      │
      │ 1. Git Commit & Push
      ▼
 [GitHub Repository] (Source of Truth: App Code, Terraform, Helm Charts, GitOps Manifests)
      │
      ├───► 2. GitHub Actions CI/CD Pipeline
      │         │
      │         ├── Stage 1: Build & Automated Testing (pytest + npm test/build)
      │         ├── Stage 2: DevSecOps Gates (Gitleaks secrets + Bandit SAST)
      │         ├── Stage 3: Docker Build & Vulnerability Scan (Trivy CVE scanner)
      │         └── Stage 4: Push Hardened Images to GitHub Container Registry (GHCR)
      │
      └───► 3. Argo CD (GitOps Continuous Reconciliation)
                │
                │ Watches: final-devops-project/helm/loanboard
                │ Pulls desired state & detects live cluster drift
                ▼
 =============================================================================================================
                                       AWS CLOUD INFRASTRUCTURE (TERRAFORM)
 =============================================================================================================
  AWS VPC (10.20.0.0/16)
   ├── Public Subnets (NAT Gateways, Internet Gateway, External ALB Ingress)
   └── Private Subnets (AWS EKS Cluster v1.31 with Managed Node Groups: t3.medium)
        │
        ▼
   =========================================================================================================
                                       KUBERNETES CLUSTER (EKS / LOCAL)
   =========================================================================================================
    Namespace: loanboard
     │
     ├── Ingress Controller (Nginx Ingress / ALB)
     │       │
     │       ├── /api, /docs, /ready ────────► [Service: loanboard-backend] (Port 8000)
     │       │                                          │
     │       │                                          ▼
     │       │                                [Deployment: loanboard-backend] (Replicas: 2-5)
     │       │                                  ├── FastAPI Application Container
     │       │                                  ├── Probes: Startup, Liveness, Readiness
     │       │                                  └── Horizontal Pod Autoscaler (HPA)
     │       │                                          │
     │       │                                          ▼ (SQLAlchemy / psycopg)
     │       │                                [Service & Deployment: loanboard-postgres]
     │       │                                  ├── PostgreSQL 16 Container
     │       │                                  └── PVC: loanboard-postgres-pvc (5Gi)
     │       │
     │       └── / ──────────────────────────► [Service: loanboard-frontend] (Port 80)
     │                                                  │
     │                                                  ▼
     │                                        [Deployment: loanboard-frontend] (Replicas: 2-4)
     │                                          ├── React SPA (Nginx Alpine)
     │                                          └── Horizontal Pod Autoscaler (HPA)
     │
    Namespace: monitoring
     │
     ├── [Prometheus Operator] ◄── Scrapes /metrics via ServiceMonitor ──► [loanboard-backend]
     ├── [Alertmanager]
     └── [Grafana Dashboards] (CPU, Memory, Request Rate, Error Latencies)
```

---

## 3. Technologies Used

| Category | Technologies & Tools |
|---|---|
| **Programming & Frameworks** | Python 3.12, FastAPI, SQLAlchemy, Pydantic, Node.js, React, Vite |
| **Databases & Storage** | PostgreSQL 16, Kubernetes PersistentVolumeClaims (PVC) |
| **Containerization** | Docker, Docker Compose, Multi-stage Builds, Distroless / Alpine |
| **Artifact Registry** | GitHub Container Registry (GHCR) |
| **Container Orchestration** | Kubernetes (EKS / Kind / Minikube), Ingress-Nginx, HPA |
| **Package Management** | Helm 3 |
| **Infrastructure as Code** | Terraform, HashiCorp AWS Provider (VPC, Subnets, EKS, IAM, Security Groups) |
| **CI / CD Automation** | GitHub Actions |
| **DevSecOps & Security** | Trivy (Vulnerabilities & IaC), Gitleaks (Secrets), Bandit (SAST) |
| **Monitoring & Observability** | Prometheus, Grafana, Alertmanager, ServiceMonitor CRDs |
| **GitOps Continuous Delivery** | Argo CD (declarative synchronization, automated self-healing) |

---

## 4. Application Setup

The application code is organized under [`application/`](./application):
- **Backend**: FastAPI REST service with CRUD endpoints for loan applications (EMI computed server-side, guarded status transitions), health endpoints (`/health`, `/ready`), and Prometheus `/metrics`.
- **Frontend**: Responsive React LoanBoard UI with INR formatting, EMI column + create-form EMI preview, status badges, valid-next-state actions, and status/loan-type filters.

### Local Development Setup

#### Option A: Running with Virtual Environment & Node
```bash
# 1. Start PostgreSQL
docker run -d --name local-postgres -e POSTGRES_DB=loanboard -e POSTGRES_USER=loanboard -e POSTGRES_PASSWORD=loanboard -p 5432:5432 postgres:16-alpine

# 2. Run Backend
cd application/backend
python -m venv .venv
# Linux/macOS: source .venv/bin/activate | Windows: .venv\Scripts\activate
pip install -r requirements.txt
export DATABASE_URL="postgresql+psycopg://loanboard:loanboard@localhost:5432/loanboard"
pytest
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# 3. Run Frontend
cd ../frontend
npm install
npm run dev
```

---

## 5. Docker Setup

Container assets are maintained in [`docker/`](./docker):

```bash
cd docker/
# Run multi-container stack in the background
docker compose up -d --build

# Verify container status
docker compose ps

# Inspect logs
docker compose logs -f
```

### Build & Run Individual Containers Manually
```bash
# Build Backend image
docker build -t ghcr.io/apurvdugar/loanboard-backend:latest -f docker/Dockerfile.backend application/backend

# Build Frontend image
docker build -t ghcr.io/apurvdugar/loanboard-frontend:latest -f docker/Dockerfile.frontend application/frontend

# Test Backend container
docker run -d -p 8000:8000 \
  -e DATABASE_URL="postgresql+psycopg://loanboard:loanboard@host.docker.internal:5432/loanboard" \
  ghcr.io/apurvdugar/loanboard-backend:latest
```

> ![docker compose run](./screenshots/image.png)

---

## 6. Kubernetes Deployment

The [`kubernetes/`](./kubernetes) directory provides raw, declarative YAML manifests:

```bash
# Apply entire directory
kubectl apply -f kubernetes/

# Verify objects across all types
kubectl get pods,svc,configmaps,secrets,pvc,hpa,ingress -n loanboard
```

### Included Kubernetes Resources:
1. **Namespace**: `loanboard` isolation
2. **ConfigMap**: Application parameters (`DB_NAME`, `ENVIRONMENT`, `PORT`)
3. **Secret**: Base64 encoded database credentials and connection URLs
4. **PersistentVolumeClaim**: 5Gi storage allocation for PostgreSQL data
5. **Deployment & Service (PostgreSQL)**: Single-replica stateful backend database
6. **Deployment & Service (Backend)**: 2-replica stateless FastAPI application configured with `startupProbe`, `livenessProbe`, and `readinessProbe`
7. **Deployment & Service (Frontend)**: 2-replica Nginx web server
8. **HorizontalPodAutoscaler (HPA)**: Scales pods automatically between 2 and 5 replicas on CPU (>75%) or Memory (>80%)
9. **Ingress**: Host-based routing for `loanboard.local`

> ![kubernetes resources](./screenshots/image-3.png)

---

## 7. Helm Deployment

The [`helm/loanboard`](./helm/loanboard) chart provides parameterized templating and multi-environment values (`values-dev.yaml` and `values-prod.yaml`).

```bash
# Lint the chart
helm lint helm/loanboard

# Deploy in Development mode
helm upgrade --install loanboard helm/loanboard \
  --namespace loanboard \
  --create-namespace \
  -f helm/loanboard/values-dev.yaml

# Deploy in Production mode (higher replicas, tighter resource limits)
helm upgrade --install loanboard helm/loanboard \
  --namespace loanboard \
  --create-namespace \
  -f helm/loanboard/values-prod.yaml

# Inspect release
helm list -n loanboard
helm status loanboard -n loanboard
```

> ![helm deployment](./screenshots/image-2.png)

---

## 8. Terraform Infrastructure

Cloud resources are defined under [`terraform/`](./terraform) using HashiCorp AWS modules:

### AWS Resources Managed:
- **Custom VPC**: `10.20.0.0/16` across 2 Availability Zones (`us-east-1a`, `us-east-1b`)
- **Subnets**: Public subnets with Internet Gateway and Private subnets with Managed NAT Gateway
- **EKS Cluster**: Kubernetes v1.31 with IAM control plane roles and managed node group (`t3.medium`, auto-scaling min 2 / max 4)

```bash
cd terraform/
terraform init
terraform validate
terraform plan -out=tfplan
terraform apply tfplan

# Configure kubeconfig to connect to newly created EKS cluster:
aws eks update-kubeconfig --region us-east-1 --name loanboard-cluster
```

> ![terraform infrastructure](./screenshots/image-4.png)

---

## 9. CI/CD Pipeline

The GitHub Actions pipeline ([`.github/workflows/ci-cd.yml`](./.github/workflows/ci-cd.yml)) runs automatically on every pull request and push to the `main` branch:

```text
git push
   │
   ▼
[Job 1: Test & Lint]
   ├── Python backend unit tests (pytest)
   ├── Frontend lint & production build (npm run build)
   │
   ▼
[Job 2: DevSecOps Gates]
   ├── Gitleaks secret scan
   ├── Bandit SAST security analysis
   │
   ▼
[Job 3: Docker Build & Vulnerability Scan]
   ├── Build Docker images
   ├── Run Trivy scan for CRITICAL and HIGH CVEs (Security Gate)
   └── Push images to GitHub Container Registry (ghcr.io)
   │
   ▼
[Job 4: Automated Deploy] (Triggers on main branch)
   └── Updates Helm values / notifies Argo CD for GitOps sync
```

> ![ci cd pipeline](./screenshots/image-5.png)

---

## 10. DevSecOps Implementation

Security policies and scan scripts are located in [`security/`](./security):

1. **Secret Scanning**: `gitleaks.toml` scans every commit to prevent API tokens, passwords, and private certificates from leaking into source control.
2. **SAST (Static Application Security Testing)**: `.bandit` scans the Python AST for security anti-patterns (shell injections, weak hashing, debug modes).
3. **SCA & Container Image Scanning**: `trivy.yaml` scans third-party Python/NPM packages and base OS layers for CVEs. The CI pipeline exits with code `1` if any unpatched HIGH or CRITICAL vulnerability is detected.

```bash
# Execute local DevSecOps security suite:
bash security/scan.sh
```

> ![trivy scan](./screenshots/image-6.png)

---

## 11. Monitoring & Observability

Observability configurations are located in [`monitoring/`](./monitoring):

- **Prometheus Operator**: Deployed via `kube-prometheus-stack` Helm chart.
- **ServiceMonitor**: Custom CRD [`monitoring/servicemonitor.yaml`](./monitoring/servicemonitor.yaml) targets `loanboard-backend` pods on port 8000.
- **Grafana Dashboard**: Visualizes cluster CPU, memory saturation, container restarts, and HTTP response latencies.

```bash
# Deploy monitoring stack
helm upgrade --install monitoring prometheus-community/kube-prometheus-stack \
  -n monitoring --create-namespace \
  -f monitoring/prometheus-values.yaml

kubectl apply -f monitoring/servicemonitor.yaml

# Access Grafana
kubectl port-forward svc/monitoring-grafana -n monitoring 3000:80
```

> ![grafana dashboard](./screenshots/image-7.png)

---

## 12. GitOps with Argo CD

Declarative continuous delivery definitions are located in [`gitops/`](./gitops):

- **Single Source of Truth**: Kubernetes state is synchronized with the Git repository.
- **Continuous Reconciliation**: Argo CD detects any configuration drift between the Git repository and the live cluster every 3 minutes.
- **Automated Self-Healing**: If a pod or service is modified or deleted manually, Argo CD immediately restores the desired state defined in Git (`selfHeal: true`).

```bash
# Install Argo CD
kubectl create namespace argocd
kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml

# Register the LoanBoard GitOps application
kubectl apply -f gitops/application.yaml

# Monitor GitOps Synchronization
kubectl get applications -n argocd
```

> ![argocd dashboard](./screenshots/image-8.png)

---

## 13. Troubleshooting Challenges & Solutions

Practice scenarios and broken manifests are provided in [`troubleshooting/`](./troubleshooting):

### Challenge 1: ErrImagePull / ImagePullBackOff
- **Issue**: Deployment `loanboard-broken-image` enters `ImagePullBackOff`.
- **Investigation**: `kubectl describe pod -l app=loanboard-broken-image -n loanboard` shows `Failed to pull image ... NotFound`.
- **Root Cause**: Invalid image tag `does-not-exist`.
- **Remediation**: `kubectl set image deployment/loanboard-broken-image backend=ghcr.io/apurvdugar/loanboard-backend:latest -n loanboard`.
- **Verification**: Pod transitions to `Running` and passes readiness probes.

> ![troubleshooting image](./screenshots/image-9.png)

### Challenge 2: Service Selector Mismatch
- **Issue**: Incoming traffic fails; `kubectl get endpoints broken-service -n loanboard` returns `<none>`.
- **Investigation**: Service selector points to `app: label-that-does-not-exist`.
- **Root Cause**: Selector label does not match actual running pods (`app: loanboard-backend`).
- **Remediation**: Update the selector using `kubectl set selector svc broken-service "app=loanboard-backend" -n loanboard`.
- **Verification**: Endpoints instantly update with healthy pod IPs (`10.244.x.x:8000`).

> ![troubleshooting service](./screenshots/image-10.png)

---

## 14. Screenshots Reference

| Screenshot | Description | Target Path |
|---|---|---|
| `image.png` | Docker Compose running services | `screenshots/image.png` |
| `image-1.png` | Docker build and tag outputs | `screenshots/image-1.png` |
| `image-2.png` | Helm upgrade & deployment status | `screenshots/image-2.png` |
| `image-3.png` | Kubectl get all, hpa, ingress in loanboard namespace | `screenshots/image-3.png` |
| `image-4.png` | Terraform apply outputs (VPC + EKS cluster) | `screenshots/image-4.png` |
| `image-5.png` | GitHub Actions CI/CD pipeline green runs | `screenshots/image-5.png` |
| `image-6.png` | Trivy security scan report output | `screenshots/image-6.png` |
| `image-7.png` | Grafana metrics dashboard | `screenshots/image-7.png` |
| `image-8.png` | Argo CD UI showing Synced & Healthy state | `screenshots/image-8.png` |
| `image-9.png` | Troubleshooting 1: Pod describe & image fix | `screenshots/image-9.png` |
| `image-10.png` | Troubleshooting 2: Service selector patch & endpoints | `screenshots/image-10.png` |

---

---

## 16. Domain decisions (LoanBoard)

Loan API:

```text
GET    /api/loans?status=&loan_type=
GET    /api/loans/stats
GET    /api/loans/{id}
POST   /api/loans
PUT    /api/loans/{id}
PATCH  /api/loans/{id}/status
DELETE /api/loans/{id}
```

1. **EMI formula**: reducing-balance `EMI = P*r*(1+r)^n / ((1+r)^n - 1)`, `r = annual_rate/12/100`, computed server-side in `application/backend/app/loans.py` with `Decimal`, stored as `Numeric(12, 2)`. Known check: P=100000, 12%, 12m → ₹8884.88.
2. **Status state machine**: `submitted → under_review → approved/rejected`, `approved → disbursed`; terminal `rejected`/`disbursed`. Other moves return HTTP 400 via `PATCH /api/loans/{id}/status`.
3. **Money as Decimal**: `principal_amount Numeric(12,2)`, `annual_interest_rate Numeric(5,2)`; validation `principal > 0`, `tenure 6–360`, `rate 1–40%`, valid email. Never float for money.

## 15. Lessons Learned

1. **Shift-Left Security Saves Time & Money**: Integrating Trivy, Gitleaks, and Bandit into the CI pipeline catches vulnerabilities before code ever touches a container registry or cluster.
2. **GitOps Eliminates Configuration Drift**: Argo CD provides a verifiable audit trail of every change. Direct cluster edits (`kubectl edit`) are immediately reverted by self-healing.
3. **Parameterization with Helm Enables Multi-Environment Parity**: Using a single chart with distinct `values-dev.yaml` and `values-prod.yaml` prevents configuration duplication and deployment mistakes.
4. **Resilience Requires Layered Probes & Autoscaling**: Combining `startupProbe`, `livenessProbe`, `readinessProbe`, and `HPA` guarantees high availability even under sudden load spikes or slow container warmups.
5. **Systematic Kubernetes Troubleshooting**: Following the 5-step methodology (`get` → `describe` → `logs` → `fix` → `verify`) eliminates guesswork when diagnosing cluster incidents.
