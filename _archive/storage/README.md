# Команды для работы с storage в minikube

## Ephemeral storage

Создание configmap из файла:

```bash
kubectl create configmap index-configmap --from-file nginx_index.html
```

Создание деплоймента с volume types configMap (folder mount) and emptyDir:

```bash
kubectl apply -f 10-nginx-mount-folder.yaml
```

- Зайдите в под и убедитесь, что в папке /usr/share/nginx/html/ только один файл - index.html
- Содержимое файла взято из configmap
- Создайте файлы в папке /nginx_cache внутри пода, удалите под, зайдите в пересозданный под, папка /nginx_cache будет пустой

Создание деплоймента с volume types configMap (file mount) and emptyDir:

```bash
kubectl apply -f 11-nginx-mount-file.yaml
```

- Зайдите в под и убедитесь, что в папке /usr/share/nginx/html/ два файла - index.html (из configmap) и 50x.html

## Persistent storage

Монтирование папки на локальном компьютере в minikube:

```bash
minikube mount <путь к локальной папке>:/mnt_data
```

Создание persistent volume (type hostPath):

```bash
kubectl apply -f 20-pv.yaml
```

Создание persistent volume claim:

```bash
kubectl apply -f 21-pvc.yaml
```

Создание пода с persistent volume:

```bash
kubectl apply -f 22-pod.yaml
```

- В подключенной папке появится файл date.txt
- При каждом запуске пода в файле будет появляться новая строчка с датой и временем

---

Добавляем необходимые плагины в minikube:

```bash
minikube addons enable volumesnapshots
minikube addons enable csi-hostpath-driver
```

Проверяем, что драйвер запустился:

```bash
kubectl -n kube-system get pods -l kubernetes.io/minikube-addons=csi-hostpath-driver
kubectl get csidrivers
```

Создаём pvc:

```bash
kubectl apply -f 30-csi-pvc.yaml
```

Каталог `/var/lib/csi-hostpath-data/` в minikube появился.

Проверяем, что создался pvc и pv:

```bash
kubectl get pvc,pv
```

В каталоге `/var/lib/csi-hostpath-data/` в minikube появилась папка созданного pv.

Создаём pod использующий этот pvc:

```bash
kubectl apply -f 31-csi-pod.yaml
```

В каталоге `/var/lib/csi-hostpath-data/` в minikube в папке созданного pv появился файл `test.txt`.

Можете удалить и пересоздать pod, файл сохранится и данные продолжат записываться.

Удалите pod и pvc - pv и его папка в minikube исчезнут.

---

## Контроллеры управления подами

[ReplicaSet](https://kubernetes.io/docs/concepts/workloads/controllers/replicaset/) - используется в составе deployment, stateless, поды взаимозаменяемы, имена подов уникальны

[StatefulSet](https://kubernetes.io/docs/concepts/workloads/controllers/statefulset/) - имена подов стабильны, порядок запуска и завершения гарантирован, каждый под может иметь свой PVC через volumeClaimTemplates, stateful

[DaemonSet](https://kubernetes.io/docs/concepts/workloads/controllers/daemonset/) - гарантирует присутствие по одному поду на каждой ноде, автоматически создаёт под при добавлении новой ноды, stateless

## StatefulSet + volumeClaimTemplates + Dynamic Provisioning

Проверяем, что csi-hostpath-driver включен

```bash
minikube addons list | grep csi-hostpath-driver
kubectl get csidrivers
```

Создаём StorageClass с ReclaimPolicy Retain и проверяем, что он создался

```bash
kubectl apply -f 40-storageclass.yaml
kubectl get storageclass | grep csi-hostpath-sc-retain
```

Создаём Headless service и StatefulSet

```bash
kubectl apply -f 41-webapp-service.yaml
kubectl apply -f 42-webapp-statefulset.yaml
```

Проверяем, что поды, pvc и pv успешно созданы

```bash
kubectl get sts,po,pvc,pv
```

Проверяем индивидуальные данные каждого пода

```bash
kubectl exec webapp-0 -- curl -s localhost
# → Hello from webapp-0

kubectl exec webapp-1 -- curl -s localhost
# → Hello from webapp-1
```

Удаляем под

```bash
kubectl delete pod webapp-1 --force
```

Проверяем, что под восстановился и в index.html сохранилась строка с первого запуска (теперь их две)

```bash
kubectl get po
kubectl exec webapp-1 -- curl -s localhost
```

Увеличиваем количество реплик в StatefulSet

```bash
kubectl scale statefulset webapp --replicas=3
```

Убеждаемся, что новый под создан вместе с pvc и pv

```bash
kubectl get sts,po,pvc,pv
```

Проверяем индивидуальные данные нового пода

```bash
kubectl exec webapp-2 -- curl -s localhost
# → Hello from webapp-2
```

Уменьшаем количество реплик в StatefulSet

```bash
kubectl scale statefulset webapp --replicas=2
```

Убеждаемся, что под удалился, но pvc и pv остались

```bash
kubectl get sts,po,pvc,pv
```

Удаляем pvc и убеждаемся, что pv остался в статусе Released

```bash
kubectl delete pvc webapp-storage-webapp-2
kubectl get pvc,pv
```

Создаём временный под для проверки работы headless service

```bash
kubectl run temp-pod --image=nginx:1.24 --rm -it -- bash
```

В временном поде проверяем доступность подов StatefulSet по DNS-именам

```bash
curl webapp-0.webapp-service.default.svc.cluster.local
curl webapp-0.webapp-service.default.svc.cluster.local
# Выходим из пода по Ctrl+D, под будет удалён после выхода
```

## Работа с VolumeSnapshot

Проверяем, что в кластере есть VolumeSnapshotClass

```bash
kubectl get volumesnapshotclass
```

Записываем в index.html пода webapp-0 данные, которые должны сохраниться в бэкапе

```bash
kubectl exec webapp-0 -- sh -c "echo '---\nGood data that we want to backup\n---' >> /usr/share/nginx/html/index.html"
```

Создаём snapshot из pvc пода webapp-0

```bash
kubectl apply -f 43-snapshot.yaml
```

Записываем в index.html пода webapp-0 данные, которые мы не хотим сохранять

```bash
kubectl exec webapp-0 -- sh -c "echo 'Wrong data that should not be here' >> /usr/share/nginx/html/index.html"
```

Проверяем, что нужные и не нужные данные есть в index.html

```bash
kubectl exec webapp-0 -- curl -s localhost
```

Удаляем StatefulSet и pvc пода webapp-0 перед восстановлением данных

```bash
kubectl delete sts webapp
kubectl delete pvc webapp-storage-webapp-0
```

Убеждаемся, что поды удалились, остался один pvc webapp-storage-webapp-1 и два pv, один из которых в статусе Released

```bash
kubectl get po,pvc,pv
```

Создаём pvc для пода webapp-0 из VolumeSnapshot

```bash
kubectl apply -f 44-restore-pvc.yaml
```

Убеждаемся, что pvc webapp-storage-webapp-0 создан в статусе Pending

```bash
kubectl get pvc
```

Снова создаём StatefulSet и проверяем, что данные, которые мы записали до того, как сделали snapshot сохранились, а те, которые мы записали позже - исчезли

```bash
kubectl apply -f 42-webapp-statefulset.yaml
kubectl exec webapp-0 -- curl -s localhost
```

---

## Резервное копирование и восстановление с помощью Velero и Azure Blob Storage

Скачиваем Velero CLI для своей платформы по [ссылке](https://velero.io/docs/v1.17/basic-install/)

Создаём Azure Storage Account и Blob Storage container в вашей подписке Azure через Azure CLI

```bash
RESOURCE_GROUP=velero-demo
STORAGE_ACCOUNT=velerostorage$RANDOM
CONTAINER=velerobackups

az group create -n $RESOURCE_GROUP -l westeurope
az storage account create -n $STORAGE_ACCOUNT -g $RESOURCE_GROUP -l westeurope --sku Standard_LRS --encryption-services blob
az storage container create -n $CONTAINER --account-name $STORAGE_ACCOUNT
```

Получаем ключ от созданного Azure Storage Account и Subscription ID

```bash
AZURE_STORAGE_KEY=$(az storage account keys list -g $RESOURCE_GROUP -n $STORAGE_ACCOUNT --query '[0].value' -o tsv)
SUBSCRIPTION_ID=$(az account show --query 'id' -o tsv)
```

Сохраняем ключ в файл конфигурации для последующей установки Velero

```bash
cat <<EOF > credentials-velero
AZURE_STORAGE_ACCOUNT_ACCESS_KEY=$AZURE_STORAGE_KEY
AZURE_CLOUD_NAME=AzurePublicCloud
EOF
```

Устанавливаем Velero в kubernetes

```bash
velero install \
    --provider azure \
    --plugins velero/velero-plugin-for-microsoft-azure:v1.13.0 \
    --bucket $CONTAINER \
    --secret-file ./credentials-velero \
    --backup-location-config resourceGroup=$RESOURCE_GROUP,storageAccount=$STORAGE_ACCOUNT,storageAccountKeyEnvVar=AZURE_STORAGE_ACCOUNT_ACCESS_KEY \
    --use-volume-snapshots=false
```

Проверяем, что velero установлен и backup-location доступен (Available)

```bash
kubectl get pods -n velero
velero backup-location get
```

Создаём namespace, configmap и statefulset, которые будем бэкапить

```bash
kubectl apply -f 50-velero-demo-app.yaml
```

Проверяем, что ресурсы создались, а данные присутствуют в поде

```bash
kubectl get -n velero-demo sts,po,cm,pvc,pv
kubectl exec -n velero-demo demo-app-0 -- cat /data/file.txt
kubectl exec -n velero-demo demo-app-0 -- cat /etc/custom_config
```

Создаём бэкап и проверяем его статус

```bash
velero backup create demo-backup --include-namespaces velero-demo
velero backup get demo-backup
# Статус должен стать Completed
```

Удаляем namespace вместе со всеми ресурсами в нём и проверяем, что namespace удалён

```bash
kubectl delete namespace velero-demo
kubectl get ns | grep velero-demo
```

Восстанавливаем из бэкапа

```bash
velero restore create --from-backup demo-backup
```

Проверяем, что всё успешно восстановилось

```bash
velero restore get
kubectl get -n velero-demo sts,po,cm,pvc,pv
kubectl exec -n velero-demo demo-app-0 -- cat /etc/custom_config
kubectl exec -n velero-demo demo-app-0 -- cat /data/file.txt
kubectl exec -n demo demo-app-0 -- cat /data/file.txt
```
