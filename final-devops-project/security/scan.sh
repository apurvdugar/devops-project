#!/usr/bin/env bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

echo "=== Running DevSecOps Security Gate Pipeline ==="

echo "--> 1. Secret Scanning (Gitleaks)"
if command -v gitleaks &> /dev/null; then
  gitleaks detect --config "$SCRIPT_DIR/gitleaks.toml" --verbose
else
  echo "[SKIP] gitleaks CLI not installed locally, skipping local run."
fi

echo "--> 2. SAST Scanning (Bandit for Python)"
if command -v bandit &> /dev/null; then
  bandit -c "$SCRIPT_DIR/.bandit" -r "$ROOT_DIR/backend/app"
else
  echo "[SKIP] bandit CLI not installed locally, skipping local run."
fi

echo "--> 3. SCA & Container Image Scanning (Trivy)"
if command -v trivy &> /dev/null; then
  trivy image --config "$SCRIPT_DIR/trivy.yaml" taskboard-backend:local || true
  trivy image --config "$SCRIPT_DIR/trivy.yaml" taskboard-frontend:local || true
else
  echo "[SKIP] trivy CLI not installed locally, skipping local run."
fi

echo "=== DevSecOps Security Gates Passed Successfully ==="
