import boto3
import os
from app.core.config import settings
from app.domain.models import User
from botocore.exceptions import ClientError

# Configuração do DynamoDB
dynamodb = boto3.resource(
    'dynamodb',
    region_name='us-east-1',
    endpoint_url=settings.DYNAMODB_ENDPOINT,  # Endpoint configurado no Docker
    aws_access_key_id='test',  # Para o LocalStack, valores quaisquer
    aws_secret_access_key='test'
)

# Função para criar a tabela de usuários
def create_users_table():
    try:
        # Verificar se a tabela existe antes de tentar criar
        existing_tables = dynamodb.tables.all()
        if 'users' in [table.name for table in existing_tables]:
            print("Tabela já existe.")
            return

        # Criar a tabela caso não exista
        dynamodb.create_table(
            TableName='users',
            KeySchema=[
                {
                    'AttributeName': 'username',
                    'KeyType': 'HASH'  # A chave primária é o username
                }
            ],
            AttributeDefinitions=[
                {
                    'AttributeName': 'username',
                    'AttributeType': 'S'  # Tipo de dado: String
                }
            ],
            ProvisionedThroughput={
                'ReadCapacityUnits': 5,
                'WriteCapacityUnits': 5
            }
        )
        print("Tabela 'users' criada com sucesso.")
    except ClientError as e:
        # Capturar erro de cliente (ex: tabela já existe)
        print(f"Erro ao criar tabela: {e}")
        if 'ResourceInUseException' in str(e):
            print("Tabela já existe, ignorando a criação.")


# Função para acessar a tabela de usuários
def get_user_table():
    table = dynamodb.Table('users')
    return table

# Função para adicionar um usuário à tabela
def add_user(user: User):
    table = get_user_table()
    
    # Extraindo os dados do Pydantic User com .model_dump()
    user_data = user.model_dump()
    
    # Inserindo no DynamoDB
    table.put_item(
        Item={
            'username': user_data['username'],
            'email': user_data['email'],
            'password': user_data['hashed_password'],  # Use o hashed_password
        }
    )