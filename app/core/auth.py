from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from app.core.jwt import verify_access_token

# OAuth2PasswordBearer é a classe que extrai o token automaticamente do cabeçalho 'Authorization'
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

# Função para verificar o token e obter os dados do usuário
def get_current_user(token: str = Depends(oauth2_scheme)):
    payload = verify_access_token(token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token or expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return payload  # Retorna o payload, que contém as informações do usuário
