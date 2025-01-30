# app/repository/s3_repository.py
import boto3
from app.core.config import settings

def get_s3_client():
    """
    Inicializa e retorna o cliente S3 configurado.
    """
    return boto3.client(
        "s3",
        endpoint_url=settings.AWS_S3_ENDPOINT,
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        region_name=settings.AWS_DEFAULT_REGION
    )
