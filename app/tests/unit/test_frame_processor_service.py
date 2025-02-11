import os
import zipfile
from io import BytesIO
import pytest
from fastapi import HTTPException
from unittest.mock import patch, MagicMock
import boto3
from app.service.frame_processor_service import process_video
from app.core.cryptography import get_email_hash, encrypt_email

# Classe dummy para simular um UploadFile
class DummyUploadFile:
    def __init__(self, filename, content):
        self.filename = filename
        self.file = BytesIO(content)

def dummy_upload_to_s3(file_path, s3_key):
    return f"http://fake-s3.com/{s3_key}"

def dummy_get_user_by_username(username):
    email = f"{username}@example.com"
    email_encrypt = encrypt_email(email)
    return {
        "username": username,
        "email": email_encrypt,
        "email_hash": get_email_hash(email)
    }

# Teste do caminho feliz para process_video
@patch("boto3.client")  # Bloqueia o S3 real
def test_process_video_success(mock_boto_client):
    # Mocka boto3 S3 client
    mock_s3 = MagicMock()
    mock_boto_client.return_value = mock_s3
    
    dummy_file = DummyUploadFile("video.mp4", b"fake video content")
    dummy_interval = 5
    dummy_username = "testuser"

    # Cria um objeto dummy para background_tasks
    dummy_background = MagicMock()

    with patch("app.service.frame_processor_service.upload_to_s3", side_effect=dummy_upload_to_s3) as mock_upload, \
         patch("app.service.frame_processor_service.get_user_by_username", side_effect=dummy_get_user_by_username) as mock_get_user, \
         patch("app.service.frame_processor_service.ffmpeg.input") as mock_ffmpeg_input, \
         patch("zipfile.ZipFile.write", return_value=None):

        # Simula o pipeline do ffmpeg
        fake_run = MagicMock(return_value=(b"stdout", b"stderr"))
        mock_ffmpeg = MagicMock()
        mock_ffmpeg.filter.return_value.output.return_value.run = fake_run
        mock_ffmpeg_input.return_value = mock_ffmpeg

        # Simula que existem frames extraídos
        with patch("os.listdir", return_value=["frame_0001.jpg", "frame_0002.jpg"]):
            file_url = process_video(dummy_file, dummy_interval, dummy_username, background_tasks=dummy_background)
            assert file_url.startswith("http://fake-s3.com/")
            mock_upload.assert_called_once()
            mock_get_user.assert_called_once_with(dummy_username)
            dummy_background.add_task.assert_called_once()
            args, _ = dummy_background.add_task.call_args
            from app.service.email_ses_service import send_file_url_email_ses
            assert args[0] == send_file_url_email_ses
            assert args[1] == f"{dummy_username}@example.com"
            assert args[2] == dummy_username
            assert args[3] == file_url

# Teste para o caso em que nenhum frame é extraído
def test_process_video_no_frames():
    dummy_file = DummyUploadFile("video.mp4", b"fake video content")
    with patch("app.service.frame_processor_service.ffmpeg.input") as mock_ffmpeg_input, \
         patch("os.listdir", return_value=[]):
        
        fake_run = MagicMock(return_value=(b"stdout", b"stderr"))
        mock_ffmpeg = MagicMock()
        mock_ffmpeg.filter.return_value.output.return_value.run = fake_run
        mock_ffmpeg_input.return_value = mock_ffmpeg

        with pytest.raises(HTTPException) as exc_info:
            process_video(dummy_file, 5, "testuser", background_tasks=MagicMock())
        assert "Nenhum frame foi extraído do vídeo." in str(exc_info.value)

# Testa exceção genérica durante o processamento
def test_process_video_generic_exception():
    dummy_file = DummyUploadFile("video.mp4", b"fake video content")
    with patch("app.service.frame_processor_service.ffmpeg.input", side_effect=Exception("FFmpeg error")):
        with pytest.raises(HTTPException) as exc_info:
            process_video(dummy_file, 5, "testuser", background_tasks=MagicMock())
        assert "Erro durante o processamento: FFmpeg error" in str(exc_info.value)
