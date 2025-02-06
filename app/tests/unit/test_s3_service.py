import pytest
from botocore.exceptions import ClientError  # Usaremos ClientError para simular erro
from fastapi import HTTPException
from app.service.s3_service import upload_to_s3, list_user_frame_archives, delete_s3_file
from app.core.config import settings
from unittest.mock import MagicMock, patch

# --- Teste para upload_to_s3 ---
def test_upload_to_s3_success():
    dummy_file_path = "/tmp/dummy.zip"
    dummy_key = "testuser/dummy.zip"
    fake_url = f"{settings.AWS_S3_PUBLIC_URL}/{settings.AWS_S3_BUCKET_NAME}/{dummy_key}"
    dummy_client = MagicMock()
    with patch("app.service.s3_service.get_s3_client", return_value=dummy_client):
        dummy_client.upload_file.return_value = None
        result = upload_to_s3(dummy_file_path, dummy_key)
        assert result == fake_url
        dummy_client.upload_file.assert_called_once_with(dummy_file_path, settings.AWS_S3_BUCKET_NAME, dummy_key)

def test_upload_to_s3_error():
    dummy_file_path = "/tmp/dummy.zip"
    dummy_key = "testuser/dummy.zip"
    dummy_client = MagicMock()
    error = ClientError({"Error": {"Message": "Upload failed"}}, "UploadFile")
    with patch("app.service.s3_service.get_s3_client", return_value=dummy_client):
        dummy_client.upload_file.side_effect = error
        with pytest.raises(HTTPException) as exc_info:
            upload_to_s3(dummy_file_path, dummy_key)
        assert "Erro ao enviar" in str(exc_info.value)

# --- Teste para list_user_frame_archives ---
def test_list_user_frame_archives_success():
    dummy_client = MagicMock()
    dummy_response = {
        "Contents": [
            {"Key": "testuser/file1.zip"},
            {"Key": "testuser/file2.zip"},
            {"Key": "testuser/notzip.txt"}
        ]
    }
    with patch("app.service.s3_service.get_s3_client", return_value=dummy_client):
        dummy_client.list_objects_v2.return_value = dummy_response
        archives = list_user_frame_archives("testuser")
        expected = [
            f"{settings.AWS_S3_PUBLIC_URL}/{settings.AWS_S3_BUCKET_NAME}/testuser/file1.zip",
            f"{settings.AWS_S3_PUBLIC_URL}/{settings.AWS_S3_BUCKET_NAME}/testuser/file2.zip"
        ]
        assert archives == expected

def test_list_user_frame_archives_no_contents():
    dummy_client = MagicMock()
    with patch("app.service.s3_service.get_s3_client", return_value=dummy_client):
        dummy_client.list_objects_v2.return_value = {}
        archives = list_user_frame_archives("testuser")
        assert archives == []

def test_list_user_frame_archives_error():
    dummy_client = MagicMock()
    # Simula erro usando ClientError, que aceita os argumentos corretos.
    error = ClientError({"Error": {"Message": "List error"}}, "ListObjects")
    with patch("app.service.s3_service.get_s3_client", return_value=dummy_client):
        dummy_client.list_objects_v2.side_effect = error
        with pytest.raises(HTTPException) as exc_info:
            list_user_frame_archives("testuser")
        assert "Erro ao listar arquivos de frames para" in str(exc_info.value)

# --- Testes para delete_s3_file ---
def test_delete_s3_file_success():
    dummy_client = MagicMock()
    with patch("app.service.s3_service.get_s3_client", return_value=dummy_client):
        dummy_client.delete_object.return_value = {}
        delete_s3_file("testuser/dummy.zip")
        dummy_client.delete_object.assert_called_once_with(Bucket=settings.AWS_S3_BUCKET_NAME, Key="testuser/dummy.zip")

def test_delete_s3_file_nosuchkey():
    # Definir uma exceção dummy que herda de Exception para simular NoSuchKey
    class DummyNoSuchKey(Exception):
        pass

    dummy_client = MagicMock()
    dummy_client.exceptions = type("DummyExceptions", (), {"NoSuchKey": DummyNoSuchKey})
    dummy_client.delete_object.side_effect = DummyNoSuchKey("Not found")
    with patch("app.service.s3_service.get_s3_client", return_value=dummy_client):
        with pytest.raises(HTTPException) as exc_info:
            delete_s3_file("testuser/dummy.zip")
        assert "Arquivo não encontrado" in str(exc_info.value)

