import pytest
from pydantic import ValidationError
from app.domain.user_model import UserCreate, User, UserLogin, PasswordResetRequest, PasswordReset

def test_user_create_valid():
    # Testa a criação de um UserCreate válido
    user = UserCreate(
        username="testuser",
        email="test@example.com",
        password="password123",
        status="active",
        role="user_level_1"
    )
    assert user.username == "testuser"
    assert user.email == "test@example.com"
    assert user.password == "password123"
    assert user.status == "active"
    assert user.role == "user_level_1"

def test_user_create_missing_fields():
    # Testa a criação de um UserCreate com campos faltantes
    with pytest.raises(ValidationError):
        UserCreate(
            username="testuser",
            email="test@example.com"
            # password está faltando
        )

def test_user_create_invalid_email():
    # Testa a criação de um UserCreate com email inválido
    with pytest.raises(ValidationError):
        UserCreate(
            username="testuser",
            email="invalid-email",
            password="password123"
        )

def test_user_create_short_password():
    # Testa a criação de um UserCreate com senha muito curta
    with pytest.raises(ValidationError):
        UserCreate(
            username="testuser",
            email="test@example.com",
            password="short"  # Senha com menos de 8 caracteres
        )

def test_user_create_invalid_status():
    # Testa a criação de um UserCreate com status inválido
    with pytest.raises(ValidationError):
        UserCreate(
            username="testuser",
            email="test@example.com",
            password="password123",
            status="invalid_status"  # Status inválido
        )

def test_user_create_default_values():
    # Testa os valores padrão de status e role
    user = UserCreate(
        username="testuser",
        email="test@example.com",
        password="password123"
    )
    assert user.status == "active"
    assert user.role == "user_level_1"

def test_user_valid():
    # Testa a criação de um User válido
    user = User(
        username="testuser",
        email="test@example.com",
        email_hash="hashed_email",
        hashed_password="hashed_password_123",
        status="active",
        role="user_level_1"
    )
    assert user.username == "testuser"
    assert user.email == "test@example.com"
    assert user.email_hash == "hashed_email"
    assert user.hashed_password == "hashed_password_123"
    assert user.status == "active"
    assert user.role == "user_level_1"

def test_user_invalid_status():
    # Testa a criação de um User com status inválido
    with pytest.raises(ValidationError):
        User(
            username="testuser",
            email="test@example.com",
            hashed_password="hashed_password_123",
            status="invalid_status"  # Status inválido
        )

def test_user_default_values():
    # Testa os valores padrão de status e role
    user = User(
        username="testuser",
        email="test@example.com",
        email_hash="hashed_email",
        hashed_password="hashed_password_123"
    )
    assert user.status == "active"
    assert user.role == "user_level_1"

def test_user_login_valid():
    # Testa a criação de um UserLogin válido
    user_login = UserLogin(
        username="testuser",
        password="password123"
    )
    assert user_login.username == "testuser"
    assert user_login.password == "password123"

def test_user_login_missing_fields():
    # Testa a criação de um UserLogin com campos faltantes
    with pytest.raises(ValidationError):
        UserLogin(
            username="testuser"
            # password está faltando
        )

def test_password_reset_request_valid():
    # Testa a criação de um PasswordResetRequest válido
    reset_request = PasswordResetRequest(
        email="test@example.com"
    )
    assert reset_request.email == "test@example.com"

def test_password_reset_request_invalid_email():
    # Testa a criação de um PasswordResetRequest com email inválido
    with pytest.raises(ValidationError):
        PasswordResetRequest(
            email="invalid-email"
        )

def test_password_reset_valid():
    # Testa a criação de um PasswordReset válido
    reset = PasswordReset(
        token="reset_token_123",
        new_password="new_password_123"
    )
    assert reset.token == "reset_token_123"
    assert reset.new_password == "new_password_123"

def test_password_reset_short_password():
    # Testa a criação de um PasswordReset com senha muito curta
    with pytest.raises(ValidationError):
        PasswordReset(
            token="reset_token_123",
            new_password="short"  # Senha com menos de 8 caracteres
        )