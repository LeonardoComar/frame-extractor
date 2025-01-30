# app/service/s3_service.py
import boto3
from botocore.exceptions import BotoCoreError, ClientError
from fastapi import HTTPException
from app.core.config import settings  # Importação das configurações centralizadas

def upload_to_s3(file_path: str, s3_key: str, bucket_name: str = settings.AWS_S3_BUCKET_NAME) -> str:
    try:
        # Configurar cliente S3 usando as variáveis do settings
        s3_client = boto3.client(
            "s3",
            endpoint_url=settings.AWS_S3_ENDPOINT,
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_DEFAULT_REGION  # Adicionado região da configuração
        )

        # Fazer upload do arquivo
        s3_client.upload_file(file_path, bucket_name, s3_key)

        # Construir URL conforme configurações
        file_url = f"{settings.AWS_S3_PUBLIC_URL}/{bucket_name}/{s3_key}"
        
        return file_url
        
    except (BotoCoreError, ClientError) as e:
        error_msg = f"Erro ao enviar {s3_key} para {bucket_name}: {str(e)}"
        raise HTTPException(status_code=500, detail=error_msg)