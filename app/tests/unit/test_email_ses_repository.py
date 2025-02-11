import pytest
from botocore.exceptions import ClientError
from app.repository.email_ses_repository import get_email_ses_client, verify_ses_email_identity
from app.core.config import settings
from unittest.mock import patch, MagicMock

# Testa get_email_ses_client
def test_get_email_ses_client():
    with patch("app.repository.email_ses_repository.boto3.client", return_value="dummy_ses_client") as mock_boto:
        client = get_email_ses_client()
        assert client == "dummy_ses_client"
        mock_boto.assert_called_once_with(
            "ses",
            endpoint_url=settings.AWS_SES_ENDPOINT,
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_DEFAULT_REGION
        )

# Função dummy que simula um cliente SES com e-mail já verificado
def dummy_ses_client_already_verified():
    dummy = MagicMock()
    dummy.list_verified_email_addresses.return_value = {"VerifiedEmailAddresses": ["noreply@frameextractor.com"]}
    dummy.verify_email_identity.return_value = None
    return dummy

# Função dummy que simula um cliente SES sem o e-mail verificado
def dummy_ses_client_not_verified():
    dummy = MagicMock()
    dummy.list_verified_email_addresses.return_value = {"VerifiedEmailAddresses": []}
    dummy.verify_email_identity.return_value = None
    return dummy

# Função dummy que simula um erro ao listar e-mails verificados
def dummy_ses_client_error():
    dummy = MagicMock()
    dummy.list_verified_email_addresses.side_effect = ClientError(
        {"Error": {"Message": "Error listing", "Code": "SomeError"}}, "list_verified_email_addresses"
    )
    return dummy

# Testa verify_ses_email_identity quando o e-mail já está verificado
def test_verify_ses_email_identity_already_verified(capfd):
    with patch("app.repository.email_ses_repository.get_email_ses_client", return_value=dummy_ses_client_already_verified()):
        verify_ses_email_identity()
        captured = capfd.readouterr().out
        assert "já está verificado" in captured

# Testa verify_ses_email_identity quando o e-mail não está verificado
def test_verify_ses_email_identity_not_verified(capfd):
    dummy_client = dummy_ses_client_not_verified()
    with patch("app.repository.email_ses_repository.get_email_ses_client", return_value=dummy_client):
        verify_ses_email_identity()
        dummy_client.verify_email_identity.assert_called_once_with(EmailAddress="noreply@frameextractor.com")
        captured = capfd.readouterr().out
        assert "verificado com sucesso" in captured

# Testa verify_ses_email_identity quando ocorre um erro
def test_verify_ses_email_identity_error():
    with patch("app.repository.email_ses_repository.get_email_ses_client", return_value=dummy_ses_client_error()):
        with pytest.raises(ClientError) as excinfo:
            verify_ses_email_identity()
        assert "Error listing" in str(excinfo.value)
