import pytest
from fastapi import FastAPI, status
from fastapi.testclient import TestClient
from unittest.mock import patch
from app.api.user_routes import router as user_router
from app.core.auth import get_admin_user, get_current_user
from unittest.mock import ANY
from app.domain.user_model import UserCreate

# Cria uma instância do FastAPI para teste e inclui o router real com prefixo "/api"
app = FastAPI()
app.include_router(user_router, prefix="/api")

# Sobrescreve a dependência get_admin_user para sempre retornar um admin
def fake_admin_user():
    return {"sub": "admin", "role": "administrator"}

app.dependency_overrides[get_admin_user] = fake_admin_user

# Para endpoints que usam get_current_user, podemos definir um usuário padrão se necessário.
app.dependency_overrides[get_current_user] = lambda: {"sub": "user", "role": "user_level_1"}

client = TestClient(app)

# ================================
# Testes para a rota /register
# ================================

def test_register_success():
    with patch("app.api.user_routes.auth_service.create_user") as mock_create:
        # Simula que a criação do usuário ocorreu sem erros.
        response = client.post(
            "/api/register",
            json={"username": "foo", "password": "bar123456", "email": "foo@example.com"} # NOSONAR
        )
        
        # Verifica a resposta da API
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == {"message": "Usuário registrado com sucesso"}
        
        # Verifica se o método create_user foi chamado com o objeto UserCreate correto
        expected_user_data = UserCreate(
            username="foo",
            password="bar123456",
            email="foo@example.com"
        )
        mock_create.assert_called_once_with(expected_user_data)

def test_register_value_error():
    with patch("app.api.user_routes.auth_service.create_user") as mock_create:
        mock_create.side_effect = ValueError("Usuário já está em uso")
        response = client.post(
            "/api/register",
            json={"username": "foo", "password": "bar123456", "email": "foo@example.com"} # NOSONAR
        )
        assert response.status_code == 400
        assert "Usuário já está em uso" in response.json()["detail"]

# ================================
# Testes para a rota /login
# ================================

def test_login_success():
    with patch("app.api.user_routes.auth_service.authenticate_user") as mock_auth:
        mock_auth.return_value = "dummy_token"
        response = client.post(
            "/api/login",
            json={"username": "foo", "password": "bar"} # NOSONAR
        )
        assert response.status_code == status.HTTP_200_OK
        json_data = response.json()
        assert json_data["access_token"] == "dummy_token"
        assert json_data["token_type"] == "bearer"
        mock_auth.assert_called_once_with("foo", "bar")

def test_login_value_error():
    with patch("app.api.user_routes.auth_service.authenticate_user") as mock_auth:
        mock_auth.side_effect = ValueError("Credenciais inválidas")
        response = client.post(
            "/api/login",
            json={"username": "foo", "password": "wrong"} # NOSONAR
        )
        assert response.status_code == 401
        assert "Credenciais inválidas" in response.json()["detail"]

# ================================
# Teste para a rota /users (list_users)
# ================================

def test_list_users_success():
    with patch("app.api.user_routes.auth_service.get_all_users") as mock_get:
        mock_get.return_value = [{"username": "foo"}, {"username": "bar"}]
        response = client.get("/api/users", headers={"Authorization": "Bearer dummy_token"})
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == [{"username": "foo"}, {"username": "bar"}]
        mock_get.assert_called_once()

def test_list_users_exception():
    with patch("app.api.user_routes.auth_service.get_all_users") as mock_get:
        mock_get.side_effect = Exception("Erro no banco")
        response = client.get("/api/users", headers={"Authorization": "Bearer dummy_token"})
        assert response.status_code == 500
        assert "Erro no banco" in response.json()["detail"]

# ================================
# Testes para a rota /users/{username}/activate
# ================================

def test_activate_user_success():
    with patch("app.api.user_routes.auth_service.update_user_status") as mock_update:
        response = client.post("/api/users/someuser/activate", headers={"Authorization": "Bearer dummy_token"})
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == {"message": "Usuário someuser ativado com sucesso"}
        mock_update.assert_called_once_with("someuser", "active")

def test_activate_user_value_error():
    with patch("app.api.user_routes.auth_service.update_user_status") as mock_update:
        mock_update.side_effect = ValueError("Usuário não encontrado")
        response = client.post("/api/users/someuser/activate", headers={"Authorization": "Bearer dummy_token"})
        assert response.status_code == 404
        assert "Usuário não encontrado" in response.json()["detail"]

def test_activate_user_exception():
    with patch("app.api.user_routes.auth_service.update_user_status") as mock_update:
        mock_update.side_effect = Exception("Erro no update")
        response = client.post("/api/users/someuser/activate", headers={"Authorization": "Bearer dummy_token"})
        assert response.status_code == 500
        assert "Erro no update" in response.json()["detail"]

# ================================
# Testes para a rota /users/{username}/deactivate
# ================================

def test_deactivate_user_success():
    with patch("app.api.user_routes.auth_service.update_user_status") as mock_update:
        response = client.post("/api/users/someuser/deactivate", headers={"Authorization": "Bearer dummy_token"})
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == {"message": "Usuário someuser inativado com sucesso"}
        mock_update.assert_called_once_with("someuser", "inactive")

def test_deactivate_user_value_error():
    with patch("app.api.user_routes.auth_service.update_user_status") as mock_update:
        mock_update.side_effect = ValueError("Usuário não encontrado")
        response = client.post("/api/users/someuser/deactivate", headers={"Authorization": "Bearer dummy_token"})
        assert response.status_code == 404
        assert "Usuário não encontrado" in response.json()["detail"]

def test_deactivate_user_exception():
    with patch("app.api.user_routes.auth_service.update_user_status") as mock_update:
        mock_update.side_effect = Exception("Erro no update")
        response = client.post("/api/users/someuser/deactivate", headers={"Authorization": "Bearer dummy_token"})
        assert response.status_code == 500
        assert "Erro no update" in response.json()["detail"]

# ================================
# Testes para a rota /forgot-password
# ================================

def test_forgot_password_success():
    with patch("app.api.user_routes.auth_service.send_password_reset_email") as mock_send:
        mock_send.return_value = None  # Simula sucesso
        response = client.post("/api/forgot-password", json={"email": "foo@example.com"})
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == {"message": "Email para recuperação de senha enviado com sucesso"}
        mock_send.assert_called_once_with("foo@example.com", ANY)  # ANY se não queremos verificar o background_tasks

def test_forgot_password_value_error():
    with patch("app.api.user_routes.auth_service.send_password_reset_email") as mock_send:
        mock_send.side_effect = ValueError("Usuário não encontrado")
        response = client.post("/api/forgot-password", json={"email": "notfound@example.com"})
        assert response.status_code == 404
        assert "Usuário não encontrado" in response.json()["detail"]

def test_forgot_password_exception():
    with patch("app.api.user_routes.auth_service.send_password_reset_email") as mock_send:
        mock_send.side_effect = Exception("Erro ao enviar email")
        response = client.post("/api/forgot-password", json={"email": "foo@example.com"})
        assert response.status_code == 500
        assert "Erro ao enviar email" in response.json()["detail"]

# ================================
# Testes para a rota /reset-password
# ================================

def test_reset_password_success():
    with patch("app.api.user_routes.auth_service.reset_password") as mock_reset:
        mock_reset.return_value = None  # Simula sucesso
        response = client.post("/api/reset-password", json={"token": "dummy_token", "new_password": "newPass123"})
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == {"message": "Senha redefinida com sucesso"}
        mock_reset.assert_called_once_with("dummy_token", "newPass123")

def test_reset_password_value_error():
    with patch("app.api.user_routes.auth_service.reset_password") as mock_reset:
        mock_reset.side_effect = ValueError("Token inválido")
        response = client.post("/api/reset-password", json={"token": "bad_token", "new_password": "newPass123"})
        assert response.status_code == 400
        assert "Token inválido" in response.json()["detail"]

def test_reset_password_exception():
    with patch("app.api.user_routes.auth_service.reset_password") as mock_reset:
        mock_reset.side_effect = Exception("Erro no reset")
        response = client.post("/api/reset-password", json={"token": "any_token", "new_password": "newPass123"})
        assert response.status_code == 500
        assert "Erro no reset" in response.json()["detail"]
