# app/tests/test_frame_routes.py
import pytest
from fastapi.testclient import TestClient
from fastapi import UploadFile
from unittest.mock import Mock, patch
from app.main import app  # Ajuste o import conforme sua estrutura
from app.core.auth import get_current_user

# Fixture para mockar a autenticação
@pytest.fixture(autouse=True)
def mock_auth():
    async def mock_get_current_user():
        return {"sub": "test_user"}
    
    # Sobrescreve a dependência de autenticação
    app.dependency_overrides[get_current_user] = mock_get_current_user
    yield
    app.dependency_overrides = {}

# Fixture para o cliente de teste
@pytest.fixture
def client():
    return TestClient(app)

# Fixture para mockar o process_video
@pytest.fixture
def mock_process_video():
    with patch("app.api.frame_routes.process_video") as mock:
        yield mock

def test_process_video_success(client, mock_process_video):
    # Configura o mock
    mock_process_video.return_value = "http://fake-url.com/file.mp4"
    
    # Simula um arquivo e dados de formulário
    file_content = b"fake video content"
    files = {"file": ("test.mp4", file_content, "video/mp4")}
    data = {"interval": 5}

    response = client.post("/api/process-video", files=files, data=data)
    
    # Verificações
    assert response.status_code == 200
    assert response.json() == {
        "message": "Arquivo processado e salvo com sucesso!",
        "file_url": "http://fake-url.com/file.mp4"
    }
    mock_process_video.assert_called_once()

def test_process_video_missing_file(client):
    response = client.post("/api/process-video", data={"interval": 5})
    assert response.status_code == 422  # Falha na validação

def test_process_video_invalid_interval(client):
    files = {"file": ("test.mp4", b"content", "video/mp4")}
    response = client.post("/api/process-video", files=files, data={"interval": "invalid"})
    assert response.status_code == 422

def test_process_video_service_error(client, mock_process_video):
    mock_process_video.side_effect = Exception("Erro catastrófico")
    files = {"file": ("test.mp4", b"content", "video/mp4")}
    response = client.post("/api/process-video", files=files, data={"interval": 5})
    assert response.status_code == 500
    assert "An error occurred" in response.json()["detail"]

def test_process_video_unauthorized():
    # Teste sem mock de autenticação
    with TestClient(app) as raw_client:
        app.dependency_overrides = {}  # Remove os mocks
        response = raw_client.post("/api/process-video")
        assert response.status_code == 401

# Adicione esta fixture para mockar o list_user_frame_archives
@pytest.fixture
def mock_list_archives():
    with patch("app.api.frame_routes.list_user_frame_archives") as mock:
        yield mock

# Testes para a rota de listagem
def test_list_archives_success(client, mock_list_archives):
    # Configuração do mock
    mock_data = ["archive1.mp4", "archive2.mp4"]
    mock_list_archives.return_value = mock_data
    
    # Usuário deve ser o mesmo do mock de autenticação ("test_user")
    response = client.get("/api/test_user/list-frame-archives")
    
    assert response.status_code == 200
    assert response.json() == {"archives": mock_data}
    mock_list_archives.assert_called_once_with("test_user")

def test_list_archives_unauthorized(client):
    # Tenta acessar com usuário diferente do autenticado
    response = client.get("/api/other_user/list-frame-archives")
    
    assert response.status_code == 403
    assert "Acesso negado" in response.json()["detail"]

def test_list_archives_unauthenticated():
    with TestClient(app) as raw_client:
        app.dependency_overrides = {}
        response = raw_client.get("/api/test_user/list-frame-archives")
        assert response.status_code == 401

def test_list_archives_service_error(client, mock_list_archives):
    mock_list_archives.side_effect = Exception("Erro no S3")
    
    response = client.get("/api/test_user/list-frame-archives")
    
    assert response.status_code == 500
    assert "An error occurred" in response.json()["detail"]

# Fixture para mockar o delete_s3_file
@pytest.fixture
def mock_delete_s3():
    with patch("app.api.frame_routes.delete_s3_file") as mock:
        yield mock

# Testes para a rota DELETE
def test_delete_archive_success(client, mock_delete_s3):
    response = client.delete("/api/test_user/delete-frame-archive/arquivo.txt")
    
    assert response.status_code == 200
    assert response.json() == {"message": "Arquivo 'arquivo.txt' removido com sucesso!"}
    mock_delete_s3.assert_called_once_with("test_user/arquivo.txt")

def test_delete_archive_unauthorized_user(client):
    response = client.delete("/api/other_user/delete-frame-archive/arquivo.txt")
    
    assert response.status_code == 403
    assert "Acesso negado" in response.json()["detail"]

def test_delete_archive_unauthenticated():
    with TestClient(app) as raw_client:
        app.dependency_overrides = {}
        response = raw_client.delete("/api/test_user/delete-frame-archive/arquivo.txt")
        assert response.status_code == 401

def test_delete_archive_service_error(client, mock_delete_s3):
    mock_delete_s3.side_effect = Exception("Erro de conexão com S3")
    
    response = client.delete("/api/test_user/delete-frame-archive/arquivo.txt")
    
    assert response.status_code == 500
    assert "Erro ao tentar remover o arquivo" in response.json()["detail"]

def test_delete_archive_special_chars(client, mock_delete_s3):
    response = client.delete("/api/test_user/delete-frame-archive/arquivo%20com%20espaço.txt")
    
    assert response.status_code == 200
    mock_delete_s3.assert_called_once_with("test_user/arquivo com espaço.txt")