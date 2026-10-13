# Monitoring & Observability

This directory contains configuration files and manifests to set up end-to-end monitoring and alerting using **Prometheus Operator (kube-prometheus-stack)** and **Grafana**.

---

## 1. Components

- **Prometheus**: Scrapes and stores time-series metrics from nodes, Kubernetes control plane, and LoanBoard pods.
- **Grafana**: Preconfigured visual dashboards for CPU, memory, request rates, error codes, and network I/O.
- **ServiceMonitor**: Custom Resource Definition (`ServiceMonitor`) configured to scrape the `/metrics` endpoint on `loanboard-backend`.
- **Alertmanager**: Dispatches alerts based on threshold violations (e.g. High CPU, Pod CrashLoopBackOff).

---

## 2. Installation via Helm

```bash
# Add prometheus-community chart repository
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update

# Install kube-prometheus-stack
helm upgrade --install monitoring prometheus-community/kube-prometheus-stack \
  -n monitoring \
  --create-namespace \
  -f final-devops-project/monitoring/prometheus-values.yaml

# Apply the custom ServiceMonitor
kubectl apply -f final-devops-project/monitoring/servicemonitor.yaml

# Verify monitoring pods
kubectl get pods -n monitoring
```

---

## 3. Accessing Dashboards

```bash
# Access Grafana (default credentials: admin / prom-operator)
kubectl port-forward svc/monitoring-grafana -n monitoring 3000:80

# Access Prometheus UI
kubectl port-forward svc/monitoring-kube-prometheus-prometheus -n monitoring 9090:9090
```

Recommended Prometheus Queries:
- CPU Utilization: `sum(rate(container_cpu_usage_seconds_total{namespace="loanboard"}[5m])) by (pod)`
- Memory Utilization: `sum(container_memory_working_set_bytes{namespace="loanboard"}) by (pod)`
- Request Rate: `sum(rate(http_requests_total{namespace="loanboard"}[5m]))`
