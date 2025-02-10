# app/service/auth_service.py
import bcrypt
from app.domain.user_model import User, UserCreate
from app.core.jwt import create_access_token, verify_access_token
from app.repository.dynamodb_repository import add_user, get_user_by_username, get_all_users, update_user, get_user_by_email_hash
from app.core.config import settings
from app.service.email_ses_service import send_reset_password_email_ses, send_active_user_email_ses, send_inactive_user_email_ses
from app.core.cryptography import encrypt_email, decrypt_email, get_email_hash

class AuthService:
    @staticmethod
    def get_password_hash(password: str) -> str:
        salt = bcrypt.gensalt()
        hashed_password = bcrypt.hashpw(password.encode(), salt)
        return hashed_password.decode()

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        return bcrypt.checkpw(plain_password.encode(), hashed_password.encode())

    def create_user(self, user_data: UserCreate):
        username = user_data.username.lower().strip()
        email = user_data.email.lower().strip()

        if get_user_by_username(username):
            raise ValueError("Usuário já está em uso")
        
        email_hash = get_email_hash(email)
        if get_user_by_email_hash(email_hash):
            raise ValueError("Email já está em uso")
              
                # Criptografa o email e gera o hash
        encrypted_email = encrypt_email(email)
        hashed_password = self.get_password_hash(user_data.password)
        
        # Criação do novo usuário
        new_user = User(
            username=username,
            email=encrypted_email,
            email_hash=email_hash,
            hashed_password=hashed_password
        )
        add_user(new_user)

    def authenticate_user(self, username: str, password: str) -> str:
        user = get_user_by_username(username)
        
        # Se o usuário não existir, informe credenciais inválidas
        if not user:
            raise ValueError("Credenciais inválidas")
        
        # Se o status do usuário for diferente de 'active', retorna a mensagem específica
        if user.get("status") != "active": 
            raise ValueError("O usuário está inativo! Contatar o administrador ou o suporte para mais informações")
        
        # Verifica se a senha é válida
        if not self.verify_password(password, user.get("password")):
            raise ValueError("Credenciais inválidas")
        
        # Cria o token de acesso e o retorna
        token = create_access_token(data={
            "sub": user["username"],
            "role": user.get("role", "user_level_1")
        })
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

        email = decrypt_email(user.get("email"))

        if status == "active":
            send_active_user_email_ses(email, username)
        elif status == "inactive":
            send_inactive_user_email_ses(email, username)
        
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
        update_user(user)
        
    def send_password_reset_email(self, email: str, background_tasks) -> None:
        """
        Busca o usuário pelo e-mail, gera um token de reset e enfileira o envio do e-mail.
        """
        email = email.lower().strip()
        
        email_hash = get_email_hash(email)
        user = get_user_by_email_hash(email_hash)
        if not user:
            raise ValueError("Usuário não encontrado")
        
        reset_token = create_access_token(data={"sub": user["username"]})
        reset_link = f"{settings.FRONTEND_URL}/reset-password?token={reset_token}"
        background_tasks.add_task(send_reset_password_email_ses, email, user["username"], reset_link)
