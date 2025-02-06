import pytest
from fastapi import HTTPException
from app.service.auth_service import AuthService
from app.repository.dynamodb_repository import add_user, get_user_by_username, update_user, get_all_users, get_user_by_email
from app.core.jwt import create_access_token, verify_access_token
from app.domain.user_model import User
from unittest.mock import patch, MagicMock

auth_service = AuthService()

# --- Testes para create_user ---
def test_create_user_success():
    with patch("app.service.auth_service.get_user_by_username", return_value=None) as mock_get_user, \
         patch("app.service.auth_service.add_user") as mock_add_user:
        auth_service.create_user("foo", "bar", "foo@example.com")
        mock_get_user.assert_called_once_with("foo")
        mock_add_user.assert_called_once()
        
def test_create_user_existing():
    with patch("app.service.auth_service.get_user_by_username", return_value={"username": "foo"}):
        with pytest.raises(ValueError) as exc_info:
            auth_service.create_user("foo", "bar", "foo@example.com")
        assert "Usuário já está em uso" in str(exc_info.value)

# --- Testes para authenticate_user ---
def test_authenticate_user_success():
    dummy_user = {"username": "foo", "password": "$2b$12$dummyhash", "role": "administrator"}
    with patch("app.service.auth_service.get_user_by_username", return_value=dummy_user), \
         patch("app.service.auth_service.AuthService.verify_password", return_value=True) as mock_verify:
        token = auth_service.authenticate_user("foo", "bar")
        payload = verify_access_token(token)
        assert payload["sub"] == "foo"
        assert payload["role"] == "administrator"
        mock_verify.assert_called_once_with("bar", dummy_user["password"])

def test_authenticate_user_invalid():
    with patch("app.service.auth_service.get_user_by_username", return_value=None):
        with pytest.raises(ValueError) as exc_info:
            auth_service.authenticate_user("foo", "bar")
        assert "Credenciais inválidas" in str(exc_info.value)

# --- Testes para get_all_users ---
def test_get_all_users():
    with patch("app.service.auth_service.get_all_users", return_value=[{"username": "foo"}]) as mock_all:
        users = auth_service.get_all_users()
        assert users == [{"username": "foo"}]
        mock_all.assert_called_once()

# --- Testes para update_user_status ---
def test_update_user_status_success():
    dummy_user = {"username": "foo", "status": "inactive"}
    with patch("app.service.auth_service.get_user_by_username", return_value=dummy_user) as mock_get, \
         patch("app.service.auth_service.update_user") as mock_update:
        auth_service.update_user_status("foo", "active")
        assert dummy_user["status"] == "active"
        mock_get.assert_called_once_with("foo")
        mock_update.assert_called_once_with("foo", dummy_user)

def test_update_user_status_invalid_status():
    with pytest.raises(ValueError) as exc_info:
        auth_service.update_user_status("foo", "invalid")
    assert "Status deve ser 'active' ou 'inactive'" in str(exc_info.value)

def test_update_user_status_user_not_found():
    with patch("app.service.auth_service.get_user_by_username", return_value=None):
        with pytest.raises(ValueError) as exc_info:
            auth_service.update_user_status("foo", "active")
        assert "Usuário foo não encontrado" in str(exc_info.value)

# --- Testes para reset_password ---
def test_reset_password_success():
    dummy_user = {"username": "foo", "password": "$2b$12$oldhash"}
    dummy_token = create_access_token({"sub": "foo"})
    with patch("app.service.auth_service.get_user_by_username", return_value=dummy_user) as mock_get, \
         patch("app.service.auth_service.update_user") as mock_update:
        auth_service.reset_password(dummy_token, "newpass")
        mock_get.assert_called_once_with("foo")
        mock_update.assert_called_once_with("foo", dummy_user)

def test_reset_password_invalid_token():
    with pytest.raises(ValueError) as exc_info:
        auth_service.reset_password("bad_token", "newpass")
    assert "Token inválido" in str(exc_info.value)

# --- Testes para send_password_reset_email ---
def test_send_password_reset_email_success():
    dummy_user = {"username": "foo", "email": "foo@example.com"}
    with patch("app.service.auth_service.get_user_by_email", return_value=dummy_user) as mock_get_email, \
         patch("app.service.auth_service.create_access_token", side_effect=create_access_token) as mock_create_token:
        dummy_background = MagicMock()
        auth_service.send_password_reset_email("foo@example.com", dummy_background)
        mock_get_email.assert_called_once_with("foo@example.com")
        dummy_background.add_task.assert_called_once()
        
def test_send_password_reset_email_user_not_found():
    with patch("app.service.auth_service.get_user_by_email", return_value=None):
        with pytest.raises(ValueError) as exc_info:
            auth_service.send_password_reset_email("notfound@example.com", MagicMock())
        assert "Usuário não encontrado" in str(exc_info.value)
