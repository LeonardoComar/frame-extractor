import boto3
from app.core.config import settings
from app.domain.user_model import User
from botocore.exceptions import ClientError
from boto3.dynamodb.conditions import Attr
from app.core.cryptography import get_email_hash, encrypt_email
import bcrypt

# Configuração do DynamoDB
dynamodb = boto3.resource(
    'dynamodb',
    region_name=settings.AWS_DEFAULT_REGION,
    endpoint_url=settings.DYNAMODB_ENDPOINT,
    aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
    aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY
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
                    'KeyType': 'HASH'
                }
            ],
            AttributeDefinitions=[
                {
                    'AttributeName': 'username',
                    'AttributeType': 'S'
                }
            ],
            ProvisionedThroughput={
                'ReadCapacityUnits': 5,
                'WriteCapacityUnits': 5
            }
        )
        print("Tabela 'users' criada com sucesso.")
    except ClientError as e:
        print(f"Erro ao criar tabela: {e}")
        if 'ResourceInUseException' in str(e):
            print("Tabela já existe, ignorando a criação.")

def create_admin_user():
    """
    Cria o usuário administrador com os seguintes atributos:
      - username: "administrator"
      - email: "administrator@email.com"
      - email_hash: gerado a partir do email
      - password: senha padrão criptografada
      - status: "active"
      - role: "administrator"
    """
    admin_username = "administrator"
    admin_email = "administrator@email.com"

    # Verifica se o usuário já existe pelo username
    if get_user_by_username(admin_username):
        print("Usuário administrador já existe.")
        return

    default_password = settings.ADMIN_PASSWORD
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(default_password.encode(), salt).decode()
    
    email_hash = get_email_hash(admin_email)
    encrypted_email = encrypt_email(admin_email)

    admin_user = User(
        username=admin_username,
        email=encrypted_email,
        email_hash=email_hash,
        hashed_password=hashed_password,
        status="active",
        role="administrator"
    )
    add_user(admin_user)
    print("Usuário administrador criado com sucesso.")

def get_user_table():
    table = dynamodb.Table('users')
    return table

def add_user(user: User):
    table = get_user_table()
    
    user_data = user.model_dump()
    
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

def get_user_by_username(username: str):
    table = get_user_table()
    
    try:
        response = table.get_item(Key={'username': username})
        
        if 'Item' in response:
            return response['Item']
        else:
            return None 
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
            return items[0]
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
