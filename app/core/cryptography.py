from cryptography.fernet import Fernet
from app.core.config import settings

key = settings.FERNET_KEY
cipher_suite = Fernet(key.encode())

def encrypt_email(email: str) -> str:
    """Criptografa o email."""
    return cipher_suite.encrypt(email.encode()).decode()

def decrypt_email(encrypted_email: str) -> str:
    """Descriptografa o email."""
    return cipher_suite.decrypt(encrypted_email.encode()).decode()

def get_email_hash(email: str) -> str:
    """Gera um hash SHA256 do email."""
    import hashlib
    return hashlib.sha256(email.encode()).hexdigest()

def decrypt_email_hash(email_hash: str, encrypted_email: str) -> str: # NOSONAR
    """
    Descriptografa o e-mail criptografado.
    """
    return decrypt_email(encrypted_email)
