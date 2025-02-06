import pytest
from app.main import app

@pytest.fixture(scope="session", autouse=True)
def setup_app_dependencies():
    """
    Configura dependências como tabelas DynamoDB, bucket S3 e SES identity antes dos testes.
    """
    with app.lifespan_context():
        yield
