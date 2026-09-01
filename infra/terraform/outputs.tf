output "cluster_name" {
  description = "Name of the created kind cluster"
  value       = kind_cluster.mlops.name
}

output "kubeconfig_path" {
  description = "Path to the generated kubeconfig"
  value       = kind_cluster.mlops.kubeconfig_path
}

output "endpoint" {
  description = "Kubernetes API server endpoint"
  value       = kind_cluster.mlops.endpoint
}
