import boto3
import os
from app.core.config import settings
from app.domain.user_model import User
from botocore.exceptions import ClientError
from boto3.dynamodb.conditions import Attr

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
            'email_hash': user_data['email_hash'],
            'password': user_data['hashed_password'],
            'status': user_data['status'],
            'role': user_data['role'],
        }
    )

# Função para buscar um usuário pelo username
def get_user_by_username(username: str):
    table = get_user_table()
    
    try:
        response = table.get_item(Key={'username': username})
        
        # Verifica se o item foi encontrado
        if 'Item' in response:
            return response['Item']  # Retorna os dados do usuário
        else:
            return None  # Retorna None caso o usuário não exista
    except ClientError as e:
        print(f"Erro ao buscar o usuário: {e}")
        return None
    
def get_user_by_email_hash(email_hash: str):
    table = get_user_table()
    try:
        response = table.scan(
            FilterExpression=Attr('email_hash').eq(email_hash)
        )
        items = response.get("Items", [])
        if items:
            return items[0]  # Retorna o primeiro usuário que corresponder ao e-mail
        else:
            return None
    except ClientError as e:
        print(f"Erro ao buscar usuário por email: {e}")
        return None
    
def get_all_users():
    table = get_user_table()
    response = table.scan(
        ProjectionExpression="username, #st, #rl",
        ExpressionAttributeNames={"#st": "status", "#rl": "role"}
    )
    return response.get("Items", [])

def update_user(updated_user: dict):
    table = get_user_table()
    table.put_item(Item=updated_user)
