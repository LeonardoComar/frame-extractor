import pytest
from fastapi.testclient import TestClient
from fastapi import HTTPException, status
from unittest.mock import patch
from app.main import app
from app.core.auth import get_current_user

# Sobrescreva a dependência de autenticação para os testes:
def fake_current_user():
    # Usuário logado válido para exclusão: "testuser"
    return {"sub": "testuser", "email": "testuser@example.com", "role": "user_level_1"}

app.dependency_overrides[get_current_user] = fake_current_user

client = TestClient(app)

# --- Teste de exclusão com sucesso ---
def test_delete_archive_success():
    # Patch na função delete_s3_file utilizada no endpoint, simulando sucesso
    with patch("app.api.frame_routes.delete_s3_file") as mock_delete:
        response = client.delete("/api/testuser/delete-frame-archive/arquivo.txt")
        assert response.status_code == status.HTTP_200_OK, f"Status code inesperado: {response.status_code}"
        assert response.json() == {"message": "Arquivo 'arquivo.txt' removido com sucesso!"}
        # Verifica que a função foi chamada com a chave "testuser/arquivo.txt"
        mock_delete.assert_called_once_with("testuser/arquivo.txt")

# --- Teste para usuário não autorizado (tentando excluir arquivo de outro usuário) ---
def test_delete_archive_unauthorized():
    # Sobrescreve a dependência de autenticação para simular um usuário diferente
    def fake_current_user_other():
        return {"sub": "outro_usuario", "email": "outro@example.com", "role": "user_level_1"}
    app.dependency_overrides[get_current_user] = fake_current_user_other
    
    response = client.delete("/api/testuser/delete-frame-archive/arquivo.txt")
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert "Acesso negado" in response.json()["detail"]
    
    # Restaura a dependência para os demais testes
    app.dependency_overrides[get_current_user] = fake_current_user

# --- Teste para exceção interna na exclusão (ex: erro no S3) ---
def test_delete_archive_exception():
    # Patch na função delete_s3_file para que ela levante uma exceção genérica
    with patch("app.api.frame_routes.delete_s3_file") as mock_delete:
        mock_delete.side_effect = Exception("Delete error")
        response = client.delete("/api/testuser/delete-frame-archive/arquivo.txt")
        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert "Erro ao tentar remover o arquivo: Delete error" in response.json()["detail"]
