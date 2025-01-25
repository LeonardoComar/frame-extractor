from passlib.context import CryptContext
from app.repository import users_db
from app.domain.models import User
from app.core.jwt import create_access_token

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class AuthService:
    @staticmethod
    def get_password_hash(password: str) -> str:
        return pwd_context.hash(password)

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        return pwd_context.verify(plain_password, hashed_password)

    def create_user(self, username: str, password: str, email: str):
        # Verifica se o usuário já existe
        if any(user.email == email for user in users_db):
            raise ValueError("Email já está em uso")
        if any(user.username == username for user in users_db):
            raise ValueError("Usuário já está em uso")

        # Gere o hashed_password
        hashed_password = self.get_password_hash(password)

        # Crie o objeto User com o hashed_password
        new_user = User(username=username, email=email, hashed_password=hashed_password)
        users_db.append(new_user)

    def authenticate_user(self, username: str, password: str) -> str:
        # Procura o usuário pelo username
        user = next((u for u in users_db if u.username == username), None)
        if not user or not self.verify_password(password, user.hashed_password):
            raise ValueError("Credenciais inválidas")
        
        # Gera o token JWT
        token = create_access_token(data={"sub": user.username})
        return token
