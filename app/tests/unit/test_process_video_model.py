# test_process_video_model.py

import io
import pytest
from fastapi import UploadFile, HTTPException
from app.domain.process_video_model import ProcessVideoInput

def create_dummy_upload_file(filename: str, size: int, content: bytes = b"dummy content") -> UploadFile:
    """
    Cria um objeto UploadFile usando um BytesIO para simular o arquivo.
    Adiciona um atributo 'size' para testes de validação.
    """
    file_like = io.BytesIO(content)
    upload_file = UploadFile(filename=filename, file=file_like)
    # Adiciona o atributo 'size' para simular o tamanho do arquivo
    upload_file.size = size
    return upload_file

def test_valid_input():
    """
    Testa o cenário em que o arquivo e o intervalo são válidos.
    """
    # Arquivo com extensão permitida (.mp4) e tamanho pequeno (500 bytes)
    dummy_file = create_dummy_upload_file("video.mp4", size=500)
    interval = 5
    model_instance = ProcessVideoInput.as_form(file=dummy_file, interval=interval)
    assert model_instance.interval == interval
    assert model_instance.file == dummy_file

def test_invalid_interval():
    """
    Testa a validação do intervalo: deve ser maior que 0.
    """
    dummy_file = create_dummy_upload_file("video.mp4", size=500)
    invalid_interval = 0  # Intervalo inválido

    with pytest.raises(HTTPException) as exc_info:
        ProcessVideoInput.as_form(file=dummy_file, interval=invalid_interval)
    
    assert exc_info.value.status_code == 422
    assert "O intervalo deve ser maior que 0" in str(exc_info.value.detail)

def test_invalid_file_extension():
    """
    Testa a validação da extensão do arquivo.
    """
    # Arquivo com extensão inválida (.txt não é permitido)
    dummy_file = create_dummy_upload_file("video.txt", size=500)
    interval = 5

    with pytest.raises(HTTPException) as exc_info:
        ProcessVideoInput.as_form(file=dummy_file, interval=interval)
    
    assert exc_info.value.status_code == 422
    assert "Formato de arquivo não suportado. Use MP4, MOV ou AVI." in str(exc_info.value.detail)

def test_invalid_file_size():
    """
    Testa a validação do tamanho do arquivo.
    """
    # Define o tamanho como 1GB + 1 byte para forçar a falha
    oversized = (1 * 1024 * 1024 * 1024) + 1
    dummy_file = create_dummy_upload_file("video.mp4", size=oversized)
    interval = 5

    with pytest.raises(HTTPException) as exc_info:
        ProcessVideoInput.as_form(file=dummy_file, interval=interval)
    
    assert exc_info.value.status_code == 422
    assert "O tamanho do arquivo excede o limite permitido de 1GB." in str(exc_info.value.detail)
