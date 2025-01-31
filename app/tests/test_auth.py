import pytest
from fastapi import FastAPI, Depends, status, HTTPException
from fastapi.testclient import TestClient
from unittest.mock import patch
from app.core.auth import get_current_user, oauth2_scheme

app = FastAPI()

@app.get("/protected-route")
async def protected_route(current_user: dict = Depends(get_current_user)):
    return {"user": current_user}

client = TestClient(app)

def test_oauth2_scheme_configuration():
    """Testa se o esquema OAuth2 está configurado corretamente"""
    # Acesso correto para versões recentes do FastAPI
    assert oauth2_scheme.model.flows.password.tokenUrl == "login"  # <-- Correção aqui
    assert oauth2_scheme.scheme_name == "OAuth2PasswordBearer"

def test_valid_token_authentication():
    """Testa autenticação com token válido"""
    test_payload = {"sub": "test_user"}
    
    with patch("app.core.auth.verify_access_token") as mock_verify:  # Caminho corrigido
        mock_verify.return_value = test_payload
        
        response = client.get(
            "/protected-route",
            headers={"Authorization": "Bearer valid_token"}
        )
        
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == {"user": test_payload}

def test_token_verification_error_propagation():
    """Testa propagação de erros na verificação do token"""
    with patch("app.core.auth.verify_access_token") as mock_verify:  # Caminho corrigido
        mock_verify.side_effect = Exception("Erro interno na verificação")
        
        response = client.get(
            "/protected-route",
            headers={"Authorization": "Bearer error_token"}
        )
        
        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert "Authentication error" in response.json()["detail"]