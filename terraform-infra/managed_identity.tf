resource "azurerm_user_assigned_identity" "backend_identity" {
  name                = "${random_pet.prefix.id}-backend-identity"
  resource_group_name = azurerm_resource_group.rg.name
  location            = azurerm_resource_group.rg.location

  tags = {
    environment = "development"
    managed-by  = "terraform"
  }

}

resource "azurerm_role_assignment" "backend_identity_storage_blob_data_contributor" {
  scope                = "/subscriptions/7a016bad-eb8a-41c2-acc2-af1d1d8ee11f/resourceGroups/main-infra/providers/Microsoft.Storage/storageAccounts/terraformstate2076"
  role_definition_name = "Storage Blob Data Contributor"
  principal_id         = azurerm_user_assigned_identity.backend_identity.principal_id
}