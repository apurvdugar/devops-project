# DevSecOps Security Implementation

This directory contains the security gate configurations and tooling used to shift security left throughout the CI/CD pipeline.

---

## 1. Pillars of DevSecOps in TaskBoard

| Pillar | Focus | Tool | Config / Gate |
|---|---|---|---|
| **Secret Scanning** | Prevent API keys, passwords, and private keys from entering Git | Gitleaks / TruffleHog | `gitleaks.toml` — blocks commits with credentials |
| **SAST** (Static Application Security Testing) | Scan source code for unsafe patterns (SQL injection, hardcoded secrets, weak crypto) | Bandit (Python) | `.bandit` — scans `backend/app/` |
| **SCA** (Software Composition Analysis) | Identify vulnerable third-party dependencies in `requirements.txt` & `package.json` | Trivy / pip-audit / npm audit | Flags dependencies with known CVEs |
| **Container Scanning** | Identify OS-level & layer vulnerabilities in Docker images | Trivy | `trivy.yaml` — fails CI build on HIGH / CRITICAL CVEs |
| **IaC Scanning** | Validate Kubernetes manifests and Terraform code for misconfigurations | Trivy / tfsec / checkov | Flags containers running as root, insecure security groups |

---

## 2. Security Gate Policy

Our pipeline enforces a zero-tolerance policy for exploitable critical vulnerabilities:
- **Blocking Rule**: Any vulnerability with Severity `HIGH` or `CRITICAL` that has an available upstream fix will exit with code `1`, causing the CI pipeline to fail immediately.
- **Artifact Protection**: Docker images with failing security scans are discarded and never pushed to GHCR (GitHub Container Registry).
- **Cluster Isolation**: Manifests enforce non-root execution (`runAsNonRoot: true`), read-only root filesystems where applicable, and restricted capabilities (`drop: [ALL]`).

---

## 3. Running Security Scans Locally

Run the security suite against your code and containers:

```bash
# Run all security gates
bash session21-python/security/scan.sh

# Or run individual tools:
bandit -c session21-python/security/.bandit -r session21-python/backend/app
gitleaks detect --config session21-python/security/gitleaks.toml
trivy image --severity HIGH,CRITICAL taskboard-backend:latest
```
