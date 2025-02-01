# frame-extractor

## Comandos para executar o projeto

### Subir os containers

* docker-compose up --build


### Comando para gerar o token JWT

* python -c "import secrets; print(secrets.token_urlsafe(32))"


### Comando para verificar se a tabela users foi criada no localstack

* aws --endpoint-url=http://localhost:4566 dynamodb list-tables

* aws --endpoint-url=http://localhost:4566 dynamodb scan --table-name users


### Comando para criar Bucket S3

* aws --endpoint-url=http://localhost:4566 s3 mb s3://frames-bucket

* aws s3 ls s3://frames-bucket --recursive --endpoint-url=http://localhost:4566


### Executar os testes

* pytest --cov=app app/tests/

* pytest app/tests -v --cov=app --cov-report=html


### o que falta
* Implementar testes
* Permissões de usuário
* Criptografia de e-mail
* K8s para duplicação de VM
* github CI/CD
* Documentação
* Documentação API