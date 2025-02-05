import pytest
from botocore.exceptions import ClientError
from app.repository.s3_repository import get_s3_client, create_s3_bucket
from app.core.config import settings
from unittest.mock import MagicMock, patch

# Testa a função get_s3_client
def test_get_s3_client():
    with patch("app.repository.s3_repository.boto3.client", return_value="dummy_s3_client") as mock_boto:
        client = get_s3_client()
        assert client == "dummy_s3_client"
        mock_boto.assert_called_once_with(
            "s3",
            endpoint_url=settings.AWS_S3_ENDPOINT,
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_DEFAULT_REGION
        )

# Testa create_s3_bucket para o caminho de sucesso
def test_create_s3_bucket_success(capfd):
    dummy_client = MagicMock()
    with patch("app.repository.s3_repository.get_s3_client", return_value=dummy_client):
        create_s3_bucket()
        dummy_client.create_bucket.assert_called_once_with(Bucket=settings.AWS_S3_BUCKET_NAME)
        dummy_client.put_bucket_versioning.assert_called_once_with(
            Bucket=settings.AWS_S3_BUCKET_NAME,
            VersioningConfiguration={'Status': 'Enabled'}
        )
        captured = capfd.readouterr().out
        assert f"Bucket S3 '{settings.AWS_S3_BUCKET_NAME}' criado com sucesso" in captured

# Testa create_s3_bucket quando o bucket já existe
def test_create_s3_bucket_already_exists(capfd):
    dummy_client = MagicMock()
    error = ClientError({"Error": {"Code": "BucketAlreadyOwnedByYou", "Message": "Bucket already exists"}}, "CreateBucket")
    dummy_client.create_bucket.side_effect = error
    with patch("app.repository.s3_repository.get_s3_client", return_value=dummy_client):
        create_s3_bucket()
        captured = capfd.readouterr().out
        assert f"Bucket '{settings.AWS_S3_BUCKET_NAME}' já existe" in captured

# Testa create_s3_bucket para outro tipo de erro
def test_create_s3_bucket_other_error():
    dummy_client = MagicMock()
    error = ClientError({"Error": {"Code": "SomeOtherError", "Message": "Creation error"}}, "CreateBucket")
    dummy_client.create_bucket.side_effect = error
    with patch("app.repository.s3_repository.get_s3_client", return_value=dummy_client):
        with pytest.raises(ClientError) as exc_info:
            create_s3_bucket()
        assert "Creation error" in str(exc_info.value)
