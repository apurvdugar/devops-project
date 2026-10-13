# Kubernetes Manifests

This directory contains standalone Kubernetes manifests organized for declarative cluster deployment without Helm.

---

## Resources Included

| Manifest | Kind | Purpose |
|---|---|---|
| `00-namespace.yaml` | `Namespace` | Creates isolated `loanboard` namespace |
| `01-configmap.yaml` | `ConfigMap` | Non-sensitive runtime application configuration |
| `02-secret.yaml` | `Secret` | Sensitive credentials (Postgres password, connection string) |
| `03-pvc.yaml` | `PersistentVolumeClaim` | 5Gi persistent volume claim for PostgreSQL database |
| `04-postgres.yaml` | `Deployment` + `Service` | Database workload with volume mount and readiness probe |
| `05-backend.yaml` | `Deployment` + `Service` | FastAPI replicas with startup, liveness, and readiness probes |
| `06-frontend.yaml` | `Deployment` + `Service` | React frontend static Nginx deployment |
| `07-hpa.yaml` | `HorizontalPodAutoscaler` | Auto-scaling policies for backend & frontend based on CPU/Memory |
| `08-ingress.yaml` | `Ingress` | Nginx Ingress routing `/` to frontend and `/api` to backend |

---

## Deployment Order

Apply all manifests in sequence:

```bash
kubectl apply -f kubernetes/
```

Or step-by-step:
```bash
kubectl apply -f kubernetes/00-namespace.yaml
kubectl apply -f kubernetes/01-configmap.yaml
kubectl apply -f kubernetes/02-secret.yaml
kubectl apply -f kubernetes/03-pvc.yaml
kubectl apply -f kubernetes/04-postgres.yaml
kubectl apply -f kubernetes/05-backend.yaml
kubectl apply -f kubernetes/06-frontend.yaml
kubectl apply -f kubernetes/07-hpa.yaml
kubectl apply -f kubernetes/08-ingress.yaml
```

Verify deployment:
```bash
kubectl get all,pvc,hpa,ingress -n loanboard
```
