# End-to-End Production DevOps Project: LoanBoard   

LoanBoard is a production-style, containerized loan management application built to demonstrate a complete, modern DevOps lifecycle—spanning Infrastructure as Code, CI/CD with automated testing and vulnerability scanning, Kubernetes orchestration with Helm, observability with Prometheus & Grafana, and declarative GitOps with Argo CD.

---

## 1. Project Overview

LoanBoard provides a realistic microservices workflow designed to handle loan applications, status transitions, and server-side EMI calculations:
- **Backend API**: Built with Python 3.12, **FastAPI**, **SQLAlchemy**, and **Pydantic**. Features strict input validation, reducing-balance EMI calculations with exact `Decimal` precision, Alembic database migrations, and 12 unit/integration tests running under **pytest**.
- **Frontend SPA**: A responsive dashboard built with **React** + **Vite**, served through a hardened, non-root multi-stage **Nginx** Alpine container. Includes real-time EMI previews, state-machine transition controls, and INR currency formatting.
- **Database**: **PostgreSQL 16** with a dedicated PersistentVolumeClaim (PVC) ensuring persistent storage across pod restarts.
- **Cloud Infrastructure**: Provisioned using modular **Terraform** on AWS, creating a dedicated dual-AZ VPC, public/private subnets, NAT Gateways, Security Groups, and an AWS EKS managed Kubernetes cluster.
- **Orchestration**: Managed with native Kubernetes manifests and parameterized **Helm** charts supporting separate development (`values-dev.yaml`) and production (`values-prod.yaml`) configurations.
- **CI/CD Pipeline**: GitHub Actions pipeline triggering on push and pull requests, running backend unit tests, building the frontend bundle, scanning containers for CVEs, and publishing tagged images to GitHub Container Registry (GHCR).
- **DevSecOps**: Automated security checks running across the development lifecycle, combining SAST (Bandit), secret leak detection (Gitleaks), and container vulnerability scanning (Trivy) configured to fail on HIGH and CRITICAL CVEs.
- **Monitoring & Observability**: Integrated **Prometheus** and **Grafana** via `kube-prometheus-stack` and a custom `ServiceMonitor` scraping `/metrics` from FastAPI to track request volume, error rates, and p95/p99 latencies.
- **GitOps Delivery**: Continuous reconciliation, automated drift detection, and self-healing powered by **Argo CD**.
- **Troubleshooting Lab**: Documented runbooks diagnosing and remediating real-world Kubernetes failure modes (`ImagePullBackOff` and broken service selectors).

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
                │ Watches: helm/loanboard
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

The application codebase is structured under [`application/`](./application):
- **Backend**: FastAPI REST service providing full CRUD operations for loans, server-side EMI calculation using standard reducing-balance math, strict status state-machine enforcement (`submitted` → `under_review` → `approved`/`rejected` → `disbursed`), readiness/health probes (`/health`, `/ready`), and Prometheus telemetry (`/metrics`).
- **Frontend**: Responsive React UI built with Vite, featuring real-time EMI estimation during loan creation, clean INR currency formatting, dynamic status action buttons, and type/status filters.

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
> ![Running with venv](./screenshots/image.png)
> ![Backend local](./screenshots/image-1.png)
> ![Frontend local](./screenshots/image-2.png)
> ![Frontend local](./screenshots/image-3.png)

---

## 5. Docker Setup

To make local testing and evaluation seamless, a root-level [`docker-compose.yml`](./docker-compose.yml) allows spinning up the entire microservice stack (PostgreSQL database, FastAPI backend, and React frontend) with a single command:

```bash
# Run multi-container stack from project root
docker compose up -d --build

# Verify container status
docker compose ps

# Inspect logs
docker compose logs -f
```

An equivalent compose file is also available under [`docker/`](./docker) for isolated container development.

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

> ![docker compose run](./screenshots/image-4.png)
> ![docker compose run](./screenshots/image-5.png)
> ![ghcr](./screenshots/image-24.png)
> ![ghcr](./screenshots/image-25.png)

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

> ![kubernetes resources](./screenshots/image-6.png)
> ![kubernetes resources](./screenshots/image-26.png)
> ![kubectl deployed frontend](./screenshots/image-27.png)

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

> ![helm deployment](./screenshots/image-7.png)


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

> ![terraform infrastructure](./screenshots/image-8.png)
> ![terraform infrastructure](./screenshots/image-9.png)
> ![terraform infrastructure](./screenshots/image-10.png)
> ![terraform infrastructure](./screenshots/image-11.png)
> ![terraform infrastructure](./screenshots/image-13.png)
> ![terraform infrastructure](./screenshots/image-14.png)
> ![terraform infrastructure](./screenshots/image-15.png)

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

> ![ci cd pipeline](./screenshots/image-12.png)
> Link - https://www.loom.com/share/c9c5ecc1b76c4556b9a207175208938d [link for cicd demonstration]
---

## 10. DevSecOps Implementation

Security policies and scan scripts are located in [`security/`](./security):

1. **Secret Scanning**: `gitleaks.toml` scans every commit to prevent API tokens, passwords, and private certificates from leaking into source control.
2. **SAST (Static Application Security Testing)**: `.bandit` scans the Python AST for security anti-patterns (shell injections, weak hashing, debug modes).
3. **SCA & Container Image Scanning**: `trivy.yaml` scans third-party Python/NPM packages and base OS layers for CVEs. The CI pipeline exits with code `1` if any unpatched HIGH or CRITICAL vulnerability is detected.

### Trivy Scan — What It Does and What It Found

Trivy scans both the container base OS layers (Alpine for the frontend, Debian Bookworm Slim for the backend) and application-level libraries (pip packages in Python, npm dependencies in React). In our CI workflow, Trivy is configured with `severity: HIGH,CRITICAL` and `exit-code: '1'`, acting as a strict quality gate that halts the build and prevents images from being pushed to GHCR if any fixable HIGH or CRITICAL vulnerability is found.

During our security hardening phase, Trivy initially detected vulnerable sub-dependencies (`starlette`, `urllib3`, `msgpack`, and `setuptools`). We resolved these by pinning updated patched package versions and adopting a multi-stage Docker build to strip build artifacts. As a result, our final pipeline run passed with 0 HIGH or CRITICAL vulnerabilities across both container images.

```bash
# Execute local DevSecOps security suite:
bash security/scan.sh
```

> ![trivy scan](./screenshots/image-16.png)
---

## 11. Monitoring & Observability

Observability configurations are located in [`monitoring/`](./monitoring):

- **Prometheus Operator**: Deployed into the `monitoring` namespace using the `kube-prometheus-stack` Helm chart.
- **ServiceMonitor**: Custom resource [`monitoring/servicemonitor.yaml`](./monitoring/servicemonitor.yaml) targets the `loanboard-backend` service on port 8000, scraping FastAPI's `/metrics` endpoint every 15 seconds.
- **Grafana Dashboard**: Pre-configured JSON dashboard ([`monitoring/loanboard-dashboard.json`](./monitoring/loanboard-dashboard.json)) visualizing live HTTP throughput, error rates, request latency percentiles (p50, p95, p99), and pod resource utilization.

```bash
# Deploy monitoring stack
helm upgrade --install monitoring prometheus-community/kube-prometheus-stack \
  -n monitoring --create-namespace \
  -f monitoring/prometheus-values.yaml

kubectl apply -f monitoring/servicemonitor.yaml

# Access Grafana
kubectl port-forward svc/monitoring-grafana -n monitoring 3000:80
```
> ![prometheus dashboard](./screenshots/image-28.png)
> ![grafana dashboard](./screenshots/image-17.png)
> ![grafana dashboard](./screenshots/image-18.png)

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

> ![argocd dashboard](./screenshots/image-19.png)
> ![argocd dashboard](./screenshots/image-20.png)
> ![argocd dashboard](./screenshots/image-21.png)

---

## 13. Troubleshooting Challenges & Solutions

Practice scenarios and broken manifests are provided in [`troubleshooting/`](./troubleshooting):

### Challenge 1: ErrImagePull / ImagePullBackOff
- **Issue**: Deployment `loanboard-broken-image` enters `ImagePullBackOff`.
- **Investigation**: `kubectl describe pod -l app=loanboard-broken-image -n loanboard` shows `Failed to pull image ... NotFound`.
- **Root Cause**: Invalid image tag `does-not-exist`.
- **Remediation**: `kubectl set image deployment/loanboard-broken-image backend=ghcr.io/apurvdugar/loanboard-backend:latest -n loanboard`.
- **Verification**: Pod transitions to `Running` and passes readiness probes.

> ![troubleshooting image](./screenshots/image-22.png)

### Challenge 2: Service Selector Mismatch
- **Issue**: Incoming traffic fails; `kubectl get endpoints broken-service -n loanboard` returns `<none>`.
- **Investigation**: Service selector points to `app: label-that-does-not-exist`.
- **Root Cause**: Selector label does not match actual running pods (`app: loanboard-backend`).
- **Remediation**: Update the selector using `kubectl set selector svc broken-service "app=loanboard-backend" -n loanboard`.
- **Verification**: Endpoints instantly update with healthy pod IPs (`10.244.x.x:8000`).


> ![troubleshooting service](./screenshots/image-23.png)

---

## 14. Domain decisions (LoanBoard)

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

1. **Shift-Left Security Catches Issues Early**: Enforcing Trivy scans with strict exit-code 1 in the CI pipeline caught vulnerable sub-dependencies immediately, preventing security debt from ever reaching our production registry.
2. **GitOps Eliminates Configuration Drift**: Using Argo CD ensures that Git is always the single source of truth. Any direct cluster edits (`kubectl edit`) are detected and automatically reverted by self-healing within minutes.
3. **Helm Parameterization Ensures Environment Parity**: Maintaining one unified chart with environment-specific value overlays (`values-dev.yaml` and `values-prod.yaml`) eliminates duplicate manifests and prevents subtle staging-vs-production discrepancies.
4. **Resilience Depends on Thoughtful Probes & Autoscaling**: Combining proper startup, liveness, and readiness probes with an HPA prevents traffic from hitting uninitialized pods and handles sudden traffic surges reliably.
5. **Structured Troubleshooting Saves Hours**: Adopting a disciplined 5-step diagnostic workflow (`get` → `describe` → `logs` → `fix` → `verify`) makes resolving real cluster failures like `ImagePullBackOff` fast and deterministic.
