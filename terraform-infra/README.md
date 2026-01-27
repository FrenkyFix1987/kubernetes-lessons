# AKS Cluster Terraform Configuration

This directory contains Terraform configuration for deploying a minimal single-node Azure Kubernetes Service (AKS) cluster.

## Prerequisites

- [Terraform](https://www.terraform.io/downloads.html) >= 1.0
- [Azure CLI](https://docs.microsoft.com/en-us/cli/azure/install-azure-cli)
- Active Azure subscription
- [kubectl](https://kubernetes.io/docs/tasks/tools/) for cluster management

## Configuration

The configuration creates:
- Azure Resource Group
- SSH key pair for node access
- Single-node AKS cluster with:
  - SystemAssigned managed identity
  - Kubenet network plugin
  - Standard load balancer SKU
  - Default VM size: Standard_D2_v2

## Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `resource_group_location` | Azure region for resources | `eastus` |
| `resource_group_name_prefix` | Prefix for resource group name | `rg` |
| `node_count` | Number of nodes in the cluster | `1` |
| `vm_size` | VM size for cluster nodes | `Standard_D2_v4` |
| `username` | Admin username for nodes | `azureadmin` |
| `azure_subscription` | The Azure Subscription ID to deploy resources into | |

## Deployment

### 1. Authenticate with Azure

```bash
az login
```

Optionally, set the subscription if you have multiple:

```bash
az account set --subscription "YOUR_SUBSCRIPTION_ID"
```

### 2. Initialize Terraform

```bash
terraform init
```

### 3. Review the plan

```bash
terraform plan -out main.tfplan
```

### 4. Apply the configuration

```bash
terraform apply main.tfplan
```

This will take 5-10 minutes to complete.

## Using the Cluster

### Get kubeconfig

After deployment, retrieve the kubeconfig:

```bash
echo "$(terraform output -raw kube_config)" > ~/.kube/aks-config
```

### Set KUBECONFIG environment variable

```bash
export KUBECONFIG=~/.kube/aks-config
```

Or merge with existing config:

```bash
az aks get-credentials --resource-group $(terraform output -raw resource_group_name) --name $(terraform output -raw kubernetes_cluster_name)
```

### Verify cluster access

```bash
kubectl get nodes
kubectl get pods --all-namespaces
```

## Outputs

| Output | Description |
|--------|-------------|
| `resource_group_name` | Name of the created resource group |
| `kubernetes_cluster_name` | Name of the AKS cluster |
| `node_resource_group` | Auto-generated resource group for cluster resources |
| `host` | Kubernetes API server host (sensitive) |
| `client_certificate` | Client certificate for authentication (sensitive) |
| `client_key` | Client key for authentication (sensitive) |
| `cluster_ca_certificate` | Cluster CA certificate (sensitive) |
| `kube_config` | Complete kubeconfig file (sensitive) |

## Cleanup

To destroy all resources:

```bash
terraform plan -destroy -out main.destroy.tfplan
terraform apply main.destroy.tfplan
```

Or simply:

```bash
terraform destroy
```

## Cost Estimation

A single Standard_D2_v2 node costs approximately:
- ~$70-100 USD per month (depending on region)
- Additional costs for storage, networking, and data transfer

**Note:** This is a development/testing configuration. For production use, consider:
- Increasing node count to at least 3 for high availability
- Enabling autoscaling
- Configuring Azure Monitor and Log Analytics
- Setting up Azure AD integration
- Implementing network policies and security controls

## Customization

To customize the configuration, you can:

1. **Change VM size:**
   ```bash
   terraform apply -var="vm_size=Standard_D4_v2"
   ```

2. **Change region:**
   ```bash
   terraform apply -var="resource_group_location=westeurope"
   ```

3. **Create terraform.tfvars file:**
   ```hcl
   resource_group_location = "westeurope"
   node_count             = 1
   vm_size                = "Standard_B2s"
   username               = "aksadmin"
   ```

## Troubleshooting

### Authentication Issues

If you encounter authentication errors:
```bash
az account clear
az login
```

### Provider Download Issues

If providers fail to download:
```bash
terraform init -upgrade
```

### Cluster Not Ready

Wait a few minutes after `terraform apply` completes. AKS cluster provisioning can take 5-10 minutes.

## Files

- `providers.tf` - Terraform and provider configuration
- `variables.tf` - Input variable definitions
- `main.tf` - Main resource definitions
- `outputs.tf` - Output value definitions
- `README.md` - This file
