import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.core.auth import get_current_user
from app.core.config import settings
from unittest.mock import patch

def fake_current_user():
    return {"sub": "testuser", "email": "testuser@example.com", "role": "user_level_1"}

app.dependency_overrides[get_current_user] = fake_current_user

client = TestClient(app)

def test_list_frame_archives_success():
    """
    Testa o caminho feliz: um usuário logado "testuser" solicita a listagem
    de seus arquivos, e o serviço retorna uma lista de URLs para os arquivos .zip.
    """
    expected_archives = [
        f"{settings.AWS_S3_PUBLIC_URL}/{settings.AWS_S3_BUCKET_NAME}/testuser/file1.zip",
        f"{settings.AWS_S3_PUBLIC_URL}/{settings.AWS_S3_BUCKET_NAME}/testuser/file2.zip",
    ]
    
    # Patch na função list_user_frame_archives usada no endpoint (no namespace do router)
    with patch("app.api.frame_routes.list_user_frame_archives", return_value=expected_archives) as mock_list:
        response = client.get("/api/testuser/list-frame-archives")
        assert response.status_code == 200, f"Status code inesperado: {response.status_code}"
        json_data = response.json()
        assert "archives" in json_data, "Campo 'archives' não encontrado na resposta"
        assert json_data["archives"] == expected_archives
        mock_list.assert_called_once_with("testuser")

def test_list_frame_archives_unauthorized():
    """
    Testa que um usuário logado com um 'sub' diferente do parâmetro da URL
    não pode acessar os arquivos de outro usuário, retornando 403.
    """
    # Sobrescreve get_current_user para simular um usuário diferente (ex: "otheruser")
    def fake_current_user_other():
        return {"sub": "otheruser", "email": "otheruser@example.com", "role": "user_level_1"}
    
    app.dependency_overrides[get_current_user] = fake_current_user_other
    response = client.get("/api/testuser/list-frame-archives")
    assert response.status_code == 403, f"Esperado 403, obtido {response.status_code}"
    assert "Acesso negado" in response.json()["detail"]

    app.dependency_overrides[get_current_user] = fake_current_user

def test_list_frame_archives_exception():
    """
    Testa que, se a função list_user_frame_archives lançar uma exceção, o endpoint
    retorna 500 com a mensagem de erro apropriada.
    """
    with patch("app.api.frame_routes.list_user_frame_archives", side_effect=Exception("List error")) as mock_list:
        response = client.get("/api/testuser/list-frame-archives")
        assert response.status_code == 500, f"Esperado 500, obtido {response.status_code}"
        assert "An error occurred: List error" in response.json()["detail"]
        mock_list.assert_called_once_with("testuser")
