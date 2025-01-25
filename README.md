# frame-extractor

## Comandos para executar o projeto

### Subir os containers

* docker build -t video-frame-api .

* docker run -d --name video-frame-api-container -p 8080:8080 video-frame-api

* docker-compose build

* docker-compose up

### Comando para gerar o token JWT

* python -c "import secrets; print(secrets.token_urlsafe(32))"
