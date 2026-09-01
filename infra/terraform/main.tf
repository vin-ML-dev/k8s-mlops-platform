# Creates the 3-node kind cluster with an INLINE kind_config block.
# (The tehcyx/kind provider expects an inline kind_config; it does NOT support
#  kind_config_path.)
#
# Node role labels are set inline. Taints are applied by hand after apply — kind's
# inline taint handling varies across versions, so we do it with kubectl in the
# guide for reliability.
resource "kind_cluster" "mlops" {
  name           = var.cluster_name
  node_image     = var.node_image
  wait_for_ready = true

  kind_config {
    kind        = "Cluster"
    api_version = "kind.x-k8s.io/v1alpha4"

    # control-plane = infra node
    node {
      role = "control-plane"
      labels = {
        node-role = "infra"
      }
      extra_port_mappings {
        container_port = 30080
        host_port      = 8080
        protocol       = "TCP"
      }
    }

    # worker = model node
    node {
      role = "worker"
      labels = {
        node-role = "model"
      }
    }

    # worker = agent node
    node {
      role = "worker"
      labels = {
        node-role = "agent"
      }
    }
  }
}
