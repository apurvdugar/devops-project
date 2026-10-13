# Final Troubleshooting Challenge

This directory contains broken Kubernetes manifests designed to test and demonstrate systematic debugging and remediation in a Kubernetes cluster.

---

## Troubleshooting Methodology (5-Step Framework)

1. **Identify the Issue**: Observe symptoms via `kubectl get pods,svc,endpoints -n loanboard`.
2. **Investigate Logs & Resources**: Inspect events, container logs, and status via `kubectl describe` and `kubectl logs`.
3. **Find the Root Cause**: Pinpoint configuration errors, network mismatches, image errors, or probe failures.
4. **Fix the Issue**: Apply corrective patches, configuration fixes, or image tag updates.
5. **Verify the Solution**: Confirm pods reach `Running` & `Ready (1/1)` state and services register healthy endpoints.

---

## Challenge 1: ErrImagePull / ImagePullBackOff

### Step 1: Introduce Issue
```bash
kubectl apply -f troubleshooting/broken-image.yaml
```

### Step 2: Identify & Investigate
```bash
kubectl get pods -n loanboard
# Output shows STATUS: ImagePullBackOff / ErrImagePull

kubectl describe pod -l app=loanboard-broken-image -n loanboard
```
**Observation in Events:**
`Failed to pull image "ghcr.io/apurvdugar/loanboard-backend:does-not-exist": rpc error: code = NotFound desc = failed to pull and unpack image`

### Step 3: Root Cause
The deployment specifies a non-existent image tag `does-not-exist` that cannot be pulled from GitHub Container Registry.

### Step 4: Fix
Update the image tag to a valid published image:
```bash
kubectl set image deployment/loanboard-broken-image \
  backend=ghcr.io/apurvdugar/loanboard-backend:latest \
  -n loanboard
```

### Step 5: Verify
```bash
kubectl rollout status deployment/loanboard-broken-image -n loanboard
kubectl get pods -l app=loanboard-broken-image -n loanboard
# Expected: STATUS is Running, READY is 1/1
```

---

## Challenge 2: Service Selector Mismatch (Traffic Blackhole)

### Step 1: Introduce Issue
```bash
kubectl apply -f troubleshooting/broken-service.yaml
```

### Step 2: Identify & Investigate
```bash
# Check service endpoints
kubectl get endpoints broken-service -n loanboard
# Output:
# NAME             ENDPOINTS   AGE
# broken-service   <none>      15s

# Describe service
kubectl describe svc broken-service -n loanboard
# Look at: Selector: app=label-that-does-not-exist
```

### Step 3: Root Cause
The service selector `app: label-that-does-not-exist` does not match the actual pod label `app: loanboard-backend`. As a result, Kubernetes kube-proxy never populates endpoints for this service, causing all incoming traffic to be dropped.

### Step 4: Fix
Update the service's selector to target the running backend pods:
```bash
kubectl set selector svc broken-service "app=loanboard-backend" -n loanboard
```

### Step 5: Verify
```bash
kubectl get endpoints broken-service -n loanboard
# Expected: ENDPOINTS now lists active backend pod IPs (e.g., 10.244.0.12:8000)

kubectl get svc broken-service -n loanboard
```
