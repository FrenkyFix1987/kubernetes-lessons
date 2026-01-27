gh secret set ACR_LOGIN_SERVER -b "$(terraform output -raw acr_login_server)" -R BorisovCloud/kubernetes-lessons
gh secret set ACR_USERNAME -b "$(terraform output -raw acr_admin_username)" -R BorisovCloud/kubernetes-lessons
gh secret set ACR_PASSWORD -b "$(terraform output -raw acr_admin_password)" -R BorisovCloud/kubernetes-lessons

gh secret set DATABASE_URL -b "$(terraform output -raw database_connection_string)" -R BorisovCloud/kubernetes-lessons

gh secret set AZURE_CREDENTIALS -b "$(terraform output -raw azure_credentials_json)" -R BorisovCloud/kubernetes-lessons
gh secret set AKS_RESOURCE_GROUP -b "$(terraform output -raw resource_group_name)" -R BorisovCloud/kubernetes-lessons
gh secret set AKS_CLUSTER_NAME -b "$(terraform output -raw kubernetes_cluster_name)" -R BorisovCloud/kubernetes-lessons