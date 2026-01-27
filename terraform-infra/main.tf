# Data sources for Azure configuration
data "azurerm_subscription" "current" {}

data "azurerm_client_config" "current" {}

resource "random_pet" "prefix" {}

resource "azurerm_resource_group" "rg" {
  name     = "${var.resource_group_name_prefix}-${random_pet.prefix.id}"
  location = var.resource_group_location

  tags = {
    environment = "development"
    managed-by  = "terraform"
  }
}

# Generate SSH key pair
resource "azapi_resource" "ssh_public_key" {
  type      = "Microsoft.Compute/sshPublicKeys@2022-11-01"
  name      = "${random_pet.prefix.id}-ssh-key"
  location  = azurerm_resource_group.rg.location
  parent_id = azurerm_resource_group.rg.id
}

resource "azapi_resource_action" "ssh_public_key_gen" {
  type        = "Microsoft.Compute/sshPublicKeys@2022-11-01"
  resource_id = azapi_resource.ssh_public_key.id
  action      = "generateKeyPair"
  method      = "POST"

  response_export_values = ["publicKey", "privateKey"]
}

# Create AKS cluster
resource "azurerm_kubernetes_cluster" "aks" {
  name                = "${random_pet.prefix.id}-aks"
  location            = azurerm_resource_group.rg.location
  resource_group_name = azurerm_resource_group.rg.name
  dns_prefix          = "${random_pet.prefix.id}-aks"

  default_node_pool {
    name       = "default"
    node_count = var.node_count
    vm_size    = var.vm_size

    # Enable auto-scaling if you want to scale beyond single node
    # auto_scaling_enabled = false
  }

  linux_profile {
    admin_username = var.username

    ssh_key {
      key_data = (azapi_resource_action.ssh_public_key_gen.output).publicKey
    }
  }

  identity {
    type = "SystemAssigned"
  }

  network_profile {
    network_plugin    = "kubenet"
    load_balancer_sku = "standard"
  }

  tags = {
    environment = "development"
    managed-by  = "terraform"
  }
  lifecycle {
    ignore_changes = [default_node_pool[0].upgrade_settings]
  }
}
# Create Azure Container Registry
resource "azurerm_container_registry" "acr" {
  name                = "${replace(random_pet.prefix.id, "-", "")}acr"
  resource_group_name = azurerm_resource_group.rg.name
  location            = azurerm_resource_group.rg.location
  sku                 = "Basic"
  admin_enabled       = true

  tags = {
    environment = "development"
    managed-by  = "terraform"
  }
}

# Grant AKS cluster pull access to ACR
resource "azurerm_role_assignment" "aks_acr_pull" {
  principal_id                     = azurerm_kubernetes_cluster.aks.kubelet_identity[0].object_id
  role_definition_name             = "AcrPull"
  scope                            = azurerm_container_registry.acr.id
  skip_service_principal_aad_check = true
}

# Generate random password for PostgreSQL if not provided
resource "random_password" "postgres_password" {
  length           = 16
  special          = true
  override_special = "!#$%&*()-_=+[]{}?"
}

# Create PostgreSQL Flexible Server
resource "azurerm_postgresql_flexible_server" "postgres" {
  name                   = "${random_pet.prefix.id}-postgres"
  resource_group_name    = azurerm_resource_group.rg.name
  location               = azurerm_resource_group.rg.location
  version                = var.postgres_version
  administrator_login    = var.postgres_admin_username
  administrator_password = var.postgres_admin_password != null ? var.postgres_admin_password : random_password.postgres_password.result

  storage_mb = var.postgres_storage_mb
  sku_name   = var.postgres_sku

  backup_retention_days = 7

  tags = {
    environment = "development"
    managed-by  = "terraform"
  }
  lifecycle {
    ignore_changes = [zone]
  }
}

# Configure PostgreSQL to allow Azure services
resource "azurerm_postgresql_flexible_server_firewall_rule" "allow_azure_services" {
  name             = "allow-azure-services"
  server_id        = azurerm_postgresql_flexible_server.postgres.id
  start_ip_address = "0.0.0.0"
  end_ip_address   = "0.0.0.0"
}

# Create database
resource "azurerm_postgresql_flexible_server_database" "database" {
  name      = var.database_name
  server_id = azurerm_postgresql_flexible_server.postgres.id
  charset   = "UTF8"
  collation = "en_US.utf8"
}

# Create Azure AD Application for GitHub Actions
resource "azuread_application" "github_actions" {
  display_name = "${random_pet.prefix.id}-github-actions"
  owners       = [data.azurerm_client_config.current.object_id]
}

# Create Service Principal
resource "azuread_service_principal" "github_actions" {
  client_id = azuread_application.github_actions.client_id
  owners    = [data.azurerm_client_config.current.object_id]
}

# Create Service Principal Password
resource "azuread_service_principal_password" "github_actions" {
  service_principal_id = azuread_service_principal.github_actions.id
  end_date_relative    = "4320h" # 180 days
}

# Grant Contributor role at Resource Group scope
resource "azurerm_role_assignment" "sp_contributor" {
  scope                = azurerm_resource_group.rg.id
  role_definition_name = "Contributor"
  principal_id         = azuread_service_principal.github_actions.object_id
}

# Grant AcrPush role for pushing images to ACR
resource "azurerm_role_assignment" "sp_acr_push" {
  scope                = azurerm_container_registry.acr.id
  role_definition_name = "AcrPush"
  principal_id         = azuread_service_principal.github_actions.object_id
}

