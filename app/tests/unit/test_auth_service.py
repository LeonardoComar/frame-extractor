import pytest
from fastapi import HTTPException
from app.service.user_service import UserService
from app.repository.dynamodb_repository import add_user, get_user_by_username, update_user, get_all_users, get_user_by_email_hash
from app.core.jwt import create_access_token, verify_access_token
from app.domain.user_model import User, UserCreate
from unittest.mock import patch, MagicMock
from app.core.cryptography import decrypt_email, encrypt_email
import hashlib

user_service = UserService()

# --- Testes para create_user ---
def test_create_user_success():
    user_data = UserCreate(
        username="Foo",
        password="bar123456", # NOSONAR
        email="foo@example.com"
    )

    # Simulação do hash direto do e-mail esperado
    expected_email_hash = hashlib.sha256(user_data.email.encode()).hexdigest()

    with patch("app.service.user_service.get_user_by_username", return_value=None) as mock_get_user, \
         patch("app.service.user_service.get_user_by_email_hash", return_value=None) as mock_get_email, \
         patch("app.service.user_service.add_user"):

        user_service.create_user(user_data)

    # Verifica se get_user_by_username foi chamado com o username em minúsculas
    mock_get_user.assert_called_once_with("foo")

    # Verifica que get_user_by_email_hash foi chamado com o hash correto do e-mail
    mock_get_email.assert_called_once_with(expected_email_hash)

        
def test_create_user_existing():
    user_data = UserCreate(
        username="Foo",
        password="bar123456", # NOSONAR
        email="foo@example.com"
    )

    with patch("app.service.user_service.get_user_by_username", return_value={"username": "foo"}):
        with pytest.raises(ValueError) as exc_info:
            user_service.create_user(user_data)
        assert "Usuário já está em uso" in str(exc_info.value)

def test_create_user_existing_email():
    # Cria um objeto UserCreate para o teste
    user_data = UserCreate(
        username="testuser",
        email="test@example.com",
        password="password123",
        status="active",
        role="user_level_1"
    )
    
    # Mock do retorno para get_user_by_username (usuário não existe)
    mock_get_user = patch(
        "app.service.user_service.get_user_by_username",
        return_value=None
    )

    # Mock do retorno para get_user_by_email_hash (email já existe)
    mock_get_email = patch(
        "app.service.user_service.get_user_by_email_hash",
        return_value={"email": encrypt_email("test@example.com")}
    )

    with mock_get_user, mock_get_email:
        with pytest.raises(ValueError) as exc_info:
            # Tenta criar um usuário com email já existente
            user_service.create_user(user_data)
        assert "Email já está em uso" in str(exc_info.value)
    
    with mock_get_user, mock_get_email:
        with pytest.raises(ValueError) as exc_info:
            user_service.create_user(user_data)
        assert "Email já está em uso" in str(exc_info.value)

def test_create_user_existing_email_case_insensitive():
    user_data = UserCreate(
        username="Foo",
        password="bar123456", # NOSONAR
        email="foo@example.com"
    )

    with patch("app.service.user_service.get_user_by_username", return_value=None), \
         patch("app.service.user_service.get_user_by_email_hash", return_value={"email": "foo@example.com"}):
        
        with pytest.raises(ValueError) as exc_info:
            user_service.create_user(user_data)
        assert "Email já está em uso" in str(exc_info.value)

# --- Testes para authenticate_user ---
def test_authenticate_user_success():
    dummy_user = {
        "username": "foo",
        "password": "$2b$12$dummyhash", # NOSONAR
        "role": "administrator",
        "status": "active"
    }
    with patch("app.service.user_service.get_user_by_username", return_value=dummy_user), \
         patch("app.service.user_service.UserService.verify_password", return_value=True) as mock_verify:
        token = user_service.authenticate_user("foo", "bar")
        payload = verify_access_token(token)
        assert payload["sub"] == "foo"
        assert payload["role"] == "administrator"
        mock_verify.assert_called_once_with("bar", dummy_user["password"])

def test_authenticate_user_invalid():
    with patch("app.service.user_service.get_user_by_username", return_value=None):
        with pytest.raises(ValueError) as exc_info:
            user_service.authenticate_user("foo", "bar")
        assert "Credenciais inválidas" in str(exc_info.value)

def test_authenticate_user_inactive():
    dummy_user = {
        "username": "foo",
        "password": "$2b$12$dummyhash", # NOSONAR
        "role": "administrator",
        "status": "inactive"
    }
    with patch("app.service.user_service.get_user_by_username", return_value=dummy_user), \
         patch("app.service.user_service.UserService.verify_password", return_value=True):
        with pytest.raises(ValueError) as exc_info:
            user_service.authenticate_user("foo", "bar")
    assert "O usuário está inativo! Contatar o administrador ou o suporte para mais informações" in str(exc_info.value)

# --- Testes para get_all_users ---
def test_get_all_users():
    with patch("app.service.user_service.get_all_users", return_value=[{"username": "foo"}]) as mock_all:
        users = user_service.get_all_users()
        assert users == [{"username": "foo"}]
        mock_all.assert_called_once()

def test_update_user_status_invalid_status():
    with pytest.raises(ValueError) as exc_info:
        user_service.update_user_status("foo", "invalid")
    assert "Status deve ser 'active' ou 'inactive'" in str(exc_info.value)

def test_update_user_status_user_not_found():
    with patch("app.service.user_service.get_user_by_username", return_value=None):
        with pytest.raises(ValueError) as exc_info:
            user_service.update_user_status("foo", "active")
        assert "Usuário foo não encontrado" in str(exc_info.value)

def test_reset_password_invalid_token():
    with pytest.raises(ValueError) as exc_info:
        user_service.reset_password("bad_token", "newpass")
    assert "Token inválido" in str(exc_info.value)

# --- Testes para send_password_reset_email ---
def test_send_password_reset_email_success():
    dummy_user = {"username": "foo", "email": "foo@example.com"}

    # Calcula o hash esperado do e-mail diretamente
    expected_email_hash = hashlib.sha256(dummy_user["email"].encode()).hexdigest()

    with patch("app.service.user_service.get_user_by_email_hash", return_value=dummy_user) as mock_get_email, \
         patch("app.service.user_service.create_access_token", side_effect=create_access_token):

        dummy_background = MagicMock()
        user_service.send_password_reset_email("foo@example.com", dummy_background)

    # Verifica se get_user_by_email_hash foi chamado com o hash correto
    mock_get_email.assert_called_once_with(expected_email_hash)

        
def test_send_password_reset_email_user_not_found():
    with patch("app.service.user_service.get_user_by_email_hash", return_value=None):
        with pytest.raises(ValueError) as exc_info:
            user_service.send_password_reset_email("notfound@example.com", MagicMock())
        assert "Usuário não encontrado" in str(exc_info.value)
