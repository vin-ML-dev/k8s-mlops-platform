variable "cluster_name" {
  description = "Name of the kind cluster"
  type        = string
  default     = "mlops"
}

variable "node_image" {
  description = "kind node image (pin a known-good Kubernetes version)"
  type        = string
  # k3s-style pinning isn't used here; kind uses a node image per k8s version.
  default     = "kindest/node:v1.30.0"
}
