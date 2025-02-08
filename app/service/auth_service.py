# app/service/auth_service.py
import bcrypt
from app.domain.user_model import User
from app.core.jwt import create_access_token, verify_access_token
from app.repository.dynamodb_repository import add_user, get_user_by_username, get_all_users, update_user, get_user_by_email
from app.core.config import settings
from app.service.email_ses_service import send_reset_password_email_ses

class AuthService:
    @staticmethod
    def get_password_hash(password: str) -> str:
        salt = bcrypt.gensalt()
        hashed_password = bcrypt.hashpw(password.encode(), salt)
        return hashed_password.decode()

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        return bcrypt.checkpw(plain_password.encode(), hashed_password.encode())

    def create_user(self, username: str, password: str, email: str):
        existing_user = get_user_by_username(username)
        if existing_user:
            raise ValueError("Usuário já está em uso")
        if existing_user and existing_user.get("email") == email:
            raise ValueError("Email já está em uso")
        hashed_password = self.get_password_hash(password)
        new_user = User(username=username, email=email, hashed_password=hashed_password)
        add_user(new_user)

    def authenticate_user(self, username: str, password: str) -> str:
        user = get_user_by_username(username)
        if not user or not self.verify_password(password, user.get("password")):
            raise ValueError("Credenciais inválidas")
        token = create_access_token(data={"sub": user["username"], "role": user.get("role", "user_level_1")})
        return token

    def get_all_users(self):
        return get_all_users()

    def update_user_status(self, username: str, status: str):
        if status not in {"active", "inactive"}:
            raise ValueError("Status deve ser 'active' ou 'inactive'")
        user = get_user_by_username(username)
        if not user:
            raise ValueError(f"Usuário {username} não encontrado")
        user["status"] = status
        update_user(user)
        
    def reset_password(self, token: str, new_password: str):
        payload = verify_access_token(token)
        if not payload:
            raise ValueError("Token inválido ou expirado")
        username = payload.get("sub")
        if not username:
            raise ValueError("Token inválido")
        user = get_user_by_username(username)
        if not user:
            raise ValueError("Usuário não encontrado")
        hashed_password = self.get_password_hash(new_password)
        user["password"] = hashed_password
        update_user(username, user)
        
    def send_password_reset_email(self, email: str, background_tasks) -> None:
        """
        Busca o usuário pelo e-mail, gera um token de reset e enfileira o envio do e-mail.
        """
        # Busque o usuário usando a função get_user_by_email (lembre-se de implementar ou ajustar essa função no repositório)
        user = get_user_by_email(email)
        if not user:
            raise ValueError("Usuário não encontrado")
        # Gere o token para reset com a expiração configurada
        reset_token = create_access_token(data={"sub": user["username"]})
        # Construa o link de reset usando a URL do frontend definida nas configurações
        reset_link = f"{settings.FRONTEND_URL}/reset-password?token={reset_token}"
        # Enfileire a tarefa de envio de e-mail
        background_tasks.add_task(send_reset_password_email_ses, user["email"], user["username"], reset_link)
