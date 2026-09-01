#!/usr/bin/env bash
# Seal a plaintext Kubernetes Secret into an encrypted SealedSecret.
#
# Usage:  ./seal-secret.sh <plaintext-secret.yaml> <output-sealed.yaml>
#
# The plaintext file must NEVER be committed. Only the sealed output is safe for Git.
# Requires kubeseal (matching the controller version) and a running controller.
set -euo pipefail

IN="${1:?usage: seal-secret.sh <plaintext.yaml> <sealed-output.yaml>}"
OUT="${2:?usage: seal-secret.sh <plaintext.yaml> <sealed-output.yaml>}"

kubeseal \
  --controller-namespace kube-system \
  --controller-name sealed-secrets-controller \
  --format yaml \
  < "${IN}" > "${OUT}"

echo "sealed: ${IN} -> ${OUT}"
