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

### Comando para criar Bucket S3

* aws --endpoint-url=http://localhost:4566 s3 mb s3://frames-bucket

* aws s3 ls s3://frames-bucket --recursive --endpoint-url=http://localhost:4566


### o que falta
* Configurar o arquivo settings pra pegar no .env
* Separar as rotas
* Listar frames especificos de um usuario e salvar mais de um frame pra um mesmo usuario
* Implementar testes
* K8s para duplicação de VM
* Criptografia de e-mail
* Permissões de usuário
* Testes pra garantir que um usuário não acessa as pastas de outro
* Documentação
* Documentação API