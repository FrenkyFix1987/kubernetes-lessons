output "resource_group_name" {
  value       = azurerm_resource_group.rg.name
  description = "The name of the resource group"
}

output "kubernetes_cluster_name" {
  value       = azurerm_kubernetes_cluster.aks.name
  description = "The name of the AKS cluster"
}

output "node_resource_group" {
  value       = azurerm_kubernetes_cluster.aks.node_resource_group
  description = "The auto-generated Resource Group which contains the resources for this Managed Kubernetes Cluster"
}

output "host" {
  value       = azurerm_kubernetes_cluster.aks.kube_config[0].host
  description = "The Kubernetes cluster server host"
  sensitive   = true
}

output "client_certificate" {
  value       = azurerm_kubernetes_cluster.aks.kube_config[0].client_certificate
  description = "Base64 encoded client certificate"
  sensitive   = true
}

output "client_key" {
  value       = azurerm_kubernetes_cluster.aks.kube_config[0].client_key
  description = "Base64 encoded client key"
  sensitive   = true
}

output "cluster_ca_certificate" {
  value       = azurerm_kubernetes_cluster.aks.kube_config[0].cluster_ca_certificate
  description = "Base64 encoded cluster CA certificate"
  sensitive   = true
}

output "kube_config" {
  value       = azurerm_kubernetes_cluster.aks.kube_config_raw
  description = "Raw Kubernetes config to be used by kubectl and other compatible tools"
  sensitive   = true
}

output "acr_login_server" {
  value       = azurerm_container_registry.acr.login_server
  description = "The URL that can be used to log into the container registry"
}

output "acr_name" {
  value       = azurerm_container_registry.acr.name
  description = "The name of the Azure Container Registry"
}

output "acr_admin_username" {
  value       = azurerm_container_registry.acr.admin_username
  description = "The admin username for the Azure Container Registry"
  sensitive   = true
}

output "acr_admin_password" {
  value       = azurerm_container_registry.acr.admin_password
  description = "The admin password for the Azure Container Registry"
  sensitive   = true
}

output "postgres_server_name" {
  value       = azurerm_postgresql_flexible_server.postgres.name
  description = "The name of the PostgreSQL server"
}

output "postgres_fqdn" {
  value       = azurerm_postgresql_flexible_server.postgres.fqdn
  description = "The fully qualified domain name of the PostgreSQL server"
}

output "postgres_admin_username" {
  value       = var.postgres_admin_username
  description = "The administrator username for PostgreSQL"
  sensitive   = true
}

output "postgres_admin_password" {
  value       = var.postgres_admin_password != null ? var.postgres_admin_password : random_password.postgres_password.result
  description = "The administrator password for PostgreSQL"
  sensitive   = true
}

output "database_name" {
  value       = azurerm_postgresql_flexible_server_database.database.name
  description = "The name of the PostgreSQL database"
}

output "database_connection_string" {
  value       = "postgresql://${var.postgres_admin_username}:${urlencode(var.postgres_admin_password != null ? var.postgres_admin_password : random_password.postgres_password.result)}@${azurerm_postgresql_flexible_server.postgres.fqdn}:5432/${azurerm_postgresql_flexible_server_database.database.name}?sslmode=require"
  description = "PostgreSQL connection string for the backend app"
  sensitive   = true
}

output "sp_client_id" {
  value       = azuread_application.github_actions.client_id
  description = "Service Principal Client ID (Application ID) for GitHub Actions"
  sensitive   = true
}

output "sp_client_secret" {
  value       = azuread_service_principal_password.github_actions.value
  description = "Service Principal Client Secret for GitHub Actions"
  sensitive   = true
}

output "subscription_id" {
  value       = data.azurerm_subscription.current.subscription_id
  description = "Azure Subscription ID"
}

output "tenant_id" {
  value       = data.azurerm_client_config.current.tenant_id
  description = "Azure Tenant ID"
}

output "azure_credentials_json" {
  value = jsonencode({
    clientId       = azuread_application.github_actions.client_id
    clientSecret   = azuread_service_principal_password.github_actions.value
    subscriptionId = data.azurerm_subscription.current.subscription_id
    tenantId       = data.azurerm_client_config.current.tenant_id
  })
  description = "Complete Azure credentials JSON for GitHub Actions AZURE_CREDENTIALS secret"
  sensitive   = true
}
