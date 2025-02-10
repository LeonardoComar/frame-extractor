## Comandos executados

### Subir ambiente com k8s
* kubectl apply -f deploy/app-service.yaml (executar para todos os arquivos da pasta deploy)

### Verificar pods
* minikube service app-service -n frame-extractor
* kubectl get pods -n frame-extractor -w

## Testes
* k6 run test-load.js (atualizar arquivo com a porta correta)
