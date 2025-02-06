import pytest
from app.repository.dynamodb_repository import create_users_table
from app.repository.s3_repository import create_s3_bucket
from app.repository.email_ses_repository import verify_ses_email_identity

@pytest.fixture(scope="session", autouse=True)
def setup_app_dependencies():
    """
    Configura dependências como tabelas DynamoDB, bucket S3 e SES Identity antes dos testes.
    """
    # Configure os recursos necessários antes dos testes
    create_users_table()
    create_s3_bucket()
    verify_ses_email_identity()
