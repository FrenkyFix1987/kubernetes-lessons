variable "resource_group_location" {
  type        = string
  default     = "westeurope"
  description = "Location of the resource group"
}

variable "resource_group_name_prefix" {
  type        = string
  default     = "rg"
  description = "Prefix of the resource group name"
}

variable "node_count" {
  type        = number
  description = "The initial quantity of nodes for the node pool"
  default     = 1
}

variable "vm_size" {
  type        = string
  description = "The size of the Virtual Machine"
  default     = "Standard_D2_v4"
}

variable "username" {
  type        = string
  description = "The admin username for the nodes"
  default     = "azureadmin"
}

variable "azure_subscription" {
  type        = string
  description = "The Azure Subscription ID to deploy resources into"
  default     = ""
}

variable "postgres_admin_username" {
  type        = string
  description = "The administrator login for PostgreSQL server"
  default     = "pgadmin"
}

variable "postgres_admin_password" {
  type        = string
  description = "The administrator password for PostgreSQL server"
  sensitive   = true
  default     = null
}

variable "postgres_sku" {
  type        = string
  description = "The SKU for PostgreSQL Flexible Server"
  default     = "B_Standard_B1ms"
}

variable "postgres_storage_mb" {
  type        = number
  description = "Storage size in MB for PostgreSQL server"
  default     = 32768
}

variable "postgres_version" {
  type        = string
  description = "PostgreSQL version"
  default     = "16"
}

variable "database_name" {
  type        = string
  description = "The name of the PostgreSQL database"
  default     = "fastapi_db"
}