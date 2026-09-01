#!/usr/bin/env bash
# Install Argo CD, then hand deployment control to Git (App-of-Apps).
set -euo pipefail

kubectl create namespace argocd --dry-run=client -o yaml | kubectl apply -f -

# server-side apply avoids the "annotations: Too long" CRD error
kubectl apply -n argocd --server-side --force-conflicts \
  -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml

kubectl -n argocd rollout status deploy/argocd-server --timeout=300s

# apply the project (root app does NOT sync this), then the root app
kubectl apply -f argocd/projects/mlops-project.yaml
kubectl apply -f argocd/bootstrap/root-app.yaml

echo "Argo CD installed and root app applied. Check: kubectl -n argocd get applications"
