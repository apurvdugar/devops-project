# Final Troubleshooting Challenge

This directory contains broken Kubernetes manifests designed to test and demonstrate systematic debugging and remediation in a Kubernetes cluster.

---

## Troubleshooting Methodology (5-Step Framework)

1. **Identify the Issue**: Observe symptoms via `kubectl get pods,svc,endpoints -n taskboard`.
2. **Investigate Logs & Resources**: Inspect events, container logs, and status via `kubectl describe` and `kubectl logs`.
3. **Find the Root Cause**: Pinpoint configuration errors, network mismatches, image errors, or probe failures.
4. **Fix the Issue**: Apply corrective patches, configuration fixes, or image tag updates.
5. **Verify the Solution**: Confirm pods reach `Running` & `Ready (1/1)` state and services register healthy endpoints.

---

## Challenge 1: ErrImagePull / ImagePullBackOff

### Step 1: Introduce Issue
```bash
kubectl apply -f final-devops-project/troubleshooting/broken-image.yaml
```

### Step 2: Identify & Investigate
```bash
kubectl get pods -n taskboard
# Output shows STATUS: ImagePullBackOff / ErrImagePull

kubectl describe pod -l app=taskboard-broken-image -n taskboard
```
**Observation in Events:**
`Failed to pull image "ghcr.io/apurvdugar/taskboard-backend:does-not-exist": rpc error: code = NotFound desc = failed to pull and unpack image`

### Step 3: Root Cause
The deployment specifies a non-existent image tag `does-not-exist` that cannot be pulled from GitHub Container Registry.

### Step 4: Fix
Update the image tag to a valid published image:
```bash
kubectl set image deployment/taskboard-broken-image \
  backend=ghcr.io/apurvdugar/taskboard-backend:latest \
  -n taskboard
```

### Step 5: Verify
```bash
kubectl rollout status deployment/taskboard-broken-image -n taskboard
kubectl get pods -l app=taskboard-broken-image -n taskboard
# Expected: STATUS is Running, READY is 1/1
```

---

## Challenge 2: Service Selector Mismatch (Traffic Blackhole)

### Step 1: Introduce Issue
```bash
kubectl apply -f final-devops-project/troubleshooting/broken-service.yaml
```

### Step 2: Identify & Investigate
```bash
# Check service endpoints
kubectl get endpoints broken-service -n taskboard
# Output:
# NAME             ENDPOINTS   AGE
# broken-service   <none>      15s

# Describe service
kubectl describe svc broken-service -n taskboard
# Look at: Selector: app=label-that-does-not-exist
```

### Step 3: Root Cause
The service selector `app: label-that-does-not-exist` does not match the actual pod label `app: taskboard-backend`. As a result, Kubernetes kube-proxy never populates endpoints for this service, causing all incoming traffic to be dropped.

### Step 4: Fix
Update the service's selector to target the running backend pods:
```bash
kubectl set selector svc broken-service "app=taskboard-backend" -n taskboard
```

### Step 5: Verify
```bash
kubectl get endpoints broken-service -n taskboard
# Expected: ENDPOINTS now lists active backend pod IPs (e.g., 10.244.0.12:8000)

kubectl get svc broken-service -n taskboard
```
