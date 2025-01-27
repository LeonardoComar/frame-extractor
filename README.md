# frame-extractor

## Comandos para executar o projeto

### Subir os containers

* docker build -t video-frame-api .

* docker run -d --name video-frame-api-container -p 8080:8080 video-frame-api

* docker-compose up --build

### Comando para gerar o token JWT

* python -c "import secrets; print(secrets.token_urlsafe(32))"


### Comando para verificar se as tabelas foram criadas no localstack

* aws --endpoint-url=http://localhost:4566 dynamodb list-tables

* aws --endpoint-url=http://localhost:4566 dynamodb scan --table-name users
