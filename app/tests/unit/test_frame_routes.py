import pytest
from fastapi import FastAPI, HTTPException, status
from fastapi.testclient import TestClient
from unittest.mock import patch, ANY
from app.api.frame_routes import router as frame_router
from app.core.auth import get_current_user

# Cria um app de teste e inclui o router real com prefixo "/api"
app = FastAPI()
app.include_router(frame_router, prefix="/api")

# Sobrescreve a dependência get_current_user para testes, simulando um usuário logado
def fake_current_user():
    return {"sub": "testuser", "role": "administrator"}

app.dependency_overrides[get_current_user] = fake_current_user

client = TestClient(app)

# --- Testes para a rota POST /process-video ---
def test_process_video_success():
    # Simula um arquivo enviado via form
    class DummyUploadFile:
        def __init__(self, filename, content):
            self.filename = filename
            self.file = content  # O conteúdo pode ser um objeto com método read()
        def read(self):
            return self.file.read()
    
    # Cria um objeto similar ao UploadFile
    from io import BytesIO
    
    # Cria um objeto que simula o ProcessVideoInput (note que na rota essa classe é utilizada via Depends)
    # Vamos simular a chamada ao process_video, que é a função que efetivamente faz o processamento.
    with patch("app.api.frame_routes.process_video", return_value="http://fake-s3-url.com/file.zip") as mock_process:
        # Envie uma requisição multipart/form-data
        files = {"file": ("video.mp4", b"fake video content", "video/mp4")}
        data = {"interval": 5}
        response = client.post("/api/process-video", files=files, data=data)
        
        assert response.status_code == 200
        json_data = response.json()
        assert json_data["message"] == "Arquivo processado e salvo com sucesso!"
        assert json_data["file_url"] == "http://fake-s3-url.com/file.zip"
        mock_process.assert_called_once()
        
def test_process_video_exception():
    with patch("app.api.frame_routes.process_video") as mock_process:
        mock_process.side_effect = Exception("Processing error")
        files = {"file": ("video.mp4", b"fake video content", "video/mp4")}
        data = {"interval": 5}
        response = client.post("/api/process-video", files=files, data=data)
        # O caminho de exceção genérica deve retornar 500
        assert response.status_code == 500
        assert "Erro interno: Processing error" in response.json()["detail"]

# --- Testes para a rota GET /{username}/list-frame-archives ---
def test_list_frame_archives_success():
    with patch("app.api.frame_routes.list_user_frame_archives", return_value=["url1", "url2"]) as mock_list:
        response = client.get("/api/testuser/list-frame-archives")
        assert response.status_code == 200
        json_data = response.json()
        assert "archives" in json_data
        assert json_data["archives"] == ["url1", "url2"]
        mock_list.assert_called_once_with("testuser")

def test_list_frame_archives_unauthorized():
    # Simula um usuário logado com "sub" diferente do parâmetro
    app.dependency_overrides[get_current_user] = lambda: {"sub": "otheruser", "role": "administrator"}
    response = client.get("/api/testuser/list-frame-archives")
    assert response.status_code == 403
    assert "Acesso negado" in response.json()["detail"]
    # Restaura o usuário padrão
    app.dependency_overrides[get_current_user] = fake_current_user

def test_list_frame_archives_exception():
    with patch("app.api.frame_routes.list_user_frame_archives") as mock_list:
        mock_list.side_effect = Exception("List error")
        response = client.get("/api/testuser/list-frame-archives")
        assert response.status_code == 500
        assert "An error occurred: List error" in response.json()["detail"]

# --- Testes para a rota DELETE /{username}/delete-frame-archive/{filename} ---
def test_delete_frame_archive_success():
    with patch("app.api.frame_routes.delete_s3_file") as mock_delete:
        response = client.delete("/api/testuser/delete-frame-archive/testfile.txt")
        assert response.status_code == 200
        assert response.json() == {"message": "Arquivo 'testfile.txt' removido com sucesso!"}
        mock_delete.assert_called_once_with("testuser/testfile.txt")

def test_delete_frame_archive_unauthorized():
    # Simula um usuário logado diferente do informado na rota
    app.dependency_overrides[get_current_user] = lambda: {"sub": "otheruser", "role": "administrator"}
    response = client.delete("/api/testuser/delete-frame-archive/testfile.txt")
    assert response.status_code == 403
    assert "Acesso negado" in response.json()["detail"]
    app.dependency_overrides[get_current_user] = fake_current_user

def test_delete_frame_archive_exception():
    with patch("app.api.frame_routes.delete_s3_file") as mock_delete:
        mock_delete.side_effect = Exception("Delete error")
        response = client.delete("/api/testuser/delete-frame-archive/testfile.txt")
        assert response.status_code == 500
        assert "Erro ao tentar remover o arquivo: Delete error" in response.json()["detail"]
