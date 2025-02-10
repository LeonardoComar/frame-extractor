# frame-extractor

## Comandos para executar o projeto

### Subir os containers

* docker-compose up --build


### Comando para gerar o token JWT

* python -c "import secrets; print(secrets.token_urlsafe(32))"


### Comando pra gerar key criptografada do E-mail
* python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"


### Comando para verificar se a tabela users foi criada no localstack

* aws --endpoint-url=http://localhost:4566 dynamodb list-tables

* aws --endpoint-url=http://localhost:4566 dynamodb scan --table-name users


### Comando para criar Bucket S3

* aws --endpoint-url=http://localhost:4566 s3 mb s3://frames-bucket

* aws s3 ls s3://frames-bucket --recursive --endpoint-url=http://localhost:4566


### Comando para registar o e-mail no SES

* aws ses verify-email-identity --email-address noreply@frameextractor.com --endpoint-url http://localhost:4566


### Executar os testes

* pytest --cov=app app/tests/

* pytest app/tests -v --cov=app --cov-report=html


### o que falta
* Documentação
  Desenho da arquitetura

* K8s para duplicação de VM


* Documentação API

Melhoria de código se der tempo:
rota para verificar o processamento do vídeo

ajustar o arquivo env.example
Atualizar readme para execução do projeto

auth_service virar user_service
