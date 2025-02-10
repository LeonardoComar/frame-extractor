# frame-extractor

## Comandos para executar o projeto local com docker-compose

### Variáveis de ambiente

* Renomear o arquivo .env.example para .env

* Gerar SECRET_KEY: python -c "import secrets; print(secrets.token_urlsafe(32))"

* Gerar FERNET_KEY: python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"

### Subir os containers

* docker-compose up --build


## Comandos pra verificar as dependências do ambiente local

### Comando para verificar se a tabela users foi criada no localstack, acessar o container e executar:

* aws --endpoint-url=http://localhost:4566 dynamodb scan --table-name users


#### Caso não tenha criado:

* aws --endpoint-url=http://localhost:4566 dynamodb list-tables


### Comando para criar Bucket S3

* aws --endpoint-url=http://localhost:4566 s3 mb s3://frames-bucket


#### Caso não tenha criado:

* aws s3 ls s3://frames-bucket --recursive --endpoint-url=http://localhost:4566


### Comando para registar o e-mail no SES

* aws ses verify-email-identity --email-address noreply@frameextractor.com --endpoint-url http://localhost:4566


## Executar testes

* pytest --cov=app app/tests/

* pytest app/tests -v --cov=app --cov-report=html


## Maiores informações do k8s, ver arquivo k8s.md