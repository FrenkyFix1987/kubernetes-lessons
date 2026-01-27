# Команды установки

```bash
helm repo add grafana https://grafana.github.io/helm-charts
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts

helm upgrade --install prometheus prometheus-community/prometheus -n monitoring
helm upgrade --install promtail grafana/promtail -n monitoring -f ./monitoring/promtail-values-compact.yaml
helm upgrade --install loki grafana/loki -n monitoring -f ./monitoring/loki-values-compact.yaml
helm upgrade --install grafana grafana/grafana -n monitoring
```
