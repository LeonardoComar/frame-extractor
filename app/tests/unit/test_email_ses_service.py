import pytest
from botocore.exceptions import ClientError
from app.service.email_ses_service import (
    send_reset_password_email_ses,
    send_file_url_email_ses
)
from unittest.mock import patch

# --- Dummy SES Client para caminho de sucesso ---
class DummySESClientSuccess:
    def send_email(self, **kwargs):
        # Retorna um dicionário simulando uma resposta de sucesso
        return {"MessageId": "dummy_message_id"}

def dummy_get_email_ses_client_success():
    return DummySESClientSuccess()

# --- Dummy SES Client para caminho de erro ---
class DummySESClientError:
    def send_email(self, **kwargs):
        raise ClientError(
            {"Error": {"Message": "Email send failed", "Code": "ErrorCode"}},
            "send_email"
        )

def dummy_get_email_ses_client_error():
    return DummySESClientError()

# Testa o envio de email de reset com sucesso
def test_send_reset_password_email_ses_success():
    # Patch no local onde a função é usada
    with patch("app.service.email_ses_service.get_email_ses_client", dummy_get_email_ses_client_success):
        response = send_reset_password_email_ses(
            email_to="test@example.com",
            username="testuser",
            reset_link="http://reset.link"
        )
        assert response["MessageId"] == "dummy_message_id"

# Testa o envio de email de reset quando ocorre um erro
def test_send_reset_password_email_ses_error():
    with patch("app.service.email_ses_service.get_email_ses_client", dummy_get_email_ses_client_error):
        with pytest.raises(Exception) as exc_info:
            send_reset_password_email_ses(
                email_to="test@example.com",
                username="testuser",
                reset_link="http://reset.link"
            )
        assert "Erro ao enviar e-mail via SES: Email send failed" in str(exc_info.value)

# Testa o envio de email com o link do arquivo com sucesso
def test_send_file_url_email_ses_success():
    with patch("app.service.email_ses_service.get_email_ses_client", dummy_get_email_ses_client_success):
        response = send_file_url_email_ses(
            email_to="test@example.com",
            username="testuser",
            file_url="http://file.url"
        )
        assert response["MessageId"] == "dummy_message_id"

# Testa o envio de email com o link do arquivo quando ocorre erro
def test_send_file_url_email_ses_error():
    with patch("app.service.email_ses_service.get_email_ses_client", dummy_get_email_ses_client_error):
        with pytest.raises(Exception) as exc_info:
            send_file_url_email_ses(
                email_to="test@example.com",
                username="testuser",
                file_url="http://file.url"
            )
        assert "Erro ao enviar e-mail via SES: Email send failed" in str(exc_info.value)
