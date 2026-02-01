resource "helm_release" "argocd" {
  name       = "argocd"
  repository = "https://argoproj.github.io/argo-helm"
  chart      = "argo-cd"
  namespace  = "argocd"

  create_namespace = true

  # values = [
  #     file("${path.module}/argocd_values.yaml")
  # ]

  depends_on = [azurerm_kubernetes_cluster.aks]

}