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

# Grant Contributor role at Resource Group scope
resource "azurerm_role_assignment" "sp_contributor" {
  scope                = azurerm_resource_group.rg.id
  role_definition_name = "Contributor"
  principal_id         = azuread_service_principal.github_actions.object_id
}

resource "azuread_application_federated_identity_credential" "github_actions" {
  application_id = azuread_application.github_actions.id
  display_name   = "github-actions-federated-cred"
  audiences      = ["api://AzureADTokenExchange"]
  issuer         = "https://token.actions.githubusercontent.com"
  subject        = "repo:BorisovCloud/kubernetes-lessons:ref:refs/heads/main"
}