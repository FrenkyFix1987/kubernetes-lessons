# Команды для работы с ingress и network policy в minikube

Запуск minikube с Calico CNI:

```bash
minikube start --cni=calico
```

Установка ingress addon для minikube:

```bash
minikube addons enable ingress
```

Создание тестовых приложений:

```bash
kubectl apply -f 00-namespace.yaml
kubectl apply -f 10-deploy-app-v1.yaml -f 11-svc-app-v1.yaml
kubectl apply -f 20-deploy-app-v2.yaml -f 21-svc-app-v2.yaml
kubectl apply -f 30-ingress.yaml
```

Применение network policy default deny:

```bash
kubectl apply -f 40-deny-all.yaml
```

Применение network policy разрешающей ingress controller доступ к приложениям:

```bash
kubectl apply -f 41-allow-ingress-controller.yaml
```

Проверка доступности приложений с локальной машины через ingress controller:

```bash
curl --resolve "example.local:80:127.0.0.1" -i http://example.local # → Hello from v1
curl --resolve "v2.example.local:80:127.0.0.1" -i http://v2.example.local # → Hello from v2
```

Запуск тестового пода:

```bash
kubectl run test-client --rm -it --image=curlimages/curl:8.7.1 -n demo-ing -- sh
```

Проверка доступности сервисов из тестового пода:

```bash
curl -s app-v1.demo-ing.svc.cluster.local   # Hello from v1
curl -s app-v2.demo-ing.svc.cluster.local   # Hello from v2
```

Применение network policy разрешающей тестовому поду доступ к приложениям:

```bash
kubectl apply -f 42-allow-from-test-client.yaml
```
