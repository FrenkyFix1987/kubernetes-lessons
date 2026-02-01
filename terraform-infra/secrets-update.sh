gh secret set ACR_NAME -b "$(terraform output -raw acr_name)" -R BorisovCloud/kubernetes-lessons

gh secret set AKS_RESOURCE_GROUP -b "$(terraform output -raw resource_group_name)" -R BorisovCloud/kubernetes-lessons
gh secret set AKS_CLUSTER_NAME -b "$(terraform output -raw kubernetes_cluster_name)" -R BorisovCloud/kubernetes-lessons

gh secret set AZURE_SUBSCRIPTION_ID -b "$(terraform output -raw subscription_id)" -R BorisovCloud/kubernetes-lessons
gh secret set AZURE_TENANT_ID -b "$(terraform output -raw tenant_id)" -R BorisovCloud/kubernetes-lessons
gh secret set AZURE_CLIENT_ID -b "$(terraform output -raw sp_client_id)" -R BorisovCloud/kubernetes-lessons

gh secret set DATABASE_URL -b "$(terraform output -raw database_connection_string)" -R BorisovCloud/kubernetes-lessons
gh secret set AZURE_CREDENTIALS -b "$(terraform output -raw azure_credentials_json)" -R BorisovCloud/kubernetes-lessons
