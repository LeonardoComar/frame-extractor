from passlib.context import CryptContext
from app.domain.models import User
from app.core.jwt import create_access_token
from app.repository.dynamodb_repository import add_user, get_user_by_username, get_all_users, update_user

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class AuthService:
    @staticmethod
    def get_password_hash(password: str) -> str:
        return pwd_context.hash(password)

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        return pwd_context.verify(plain_password, hashed_password)

    def create_user(self, username: str, password: str, email: str):
        # Busca o usuário existente pelo username
        existing_user = get_user_by_username(username)
        
        # Verifica se o username já está em uso
        if existing_user:
            raise ValueError("Usuário já está em uso")
        
        # Verifica se o email já está em uso (somente se o usuário foi encontrado)
        if existing_user and existing_user.get("email") == email:
            raise ValueError("Email já está em uso")

        # Gere o hashed_password
        hashed_password = self.get_password_hash(password)

        # Crie o objeto User com o hashed_password
        new_user = User(username=username, email=email, hashed_password=hashed_password)
        
        # Adicione o usuário no DynamoDB
        add_user(new_user)

    def authenticate_user(self, username: str, password: str) -> str:
        # Procura o usuário pelo username no DynamoDB
        user = get_user_by_username(username)
        if not user or not self.verify_password(password, user.get("password")):
            raise ValueError("Credenciais inválidas")
        
        # Gera o token JWT
        token = create_access_token(data={"sub": user["username"]})
        return token
    
    def get_all_users(self):
        return get_all_users()
    
    def update_user_status(self, username: str, status: str):
        # Verificar se o status é válido
        if status not in {"active", "inactive"}:
            raise ValueError("Status deve ser 'active' ou 'inactive'")

        # Buscar o usuário
        user = get_user_by_username(username)
        if not user:
            raise ValueError(f"Usuário {username} não encontrado")

        # Atualizar o status
        user["status"] = status
        update_user(username, user)
