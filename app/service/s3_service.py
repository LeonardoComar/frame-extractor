# app/service/s3_service.py
import boto3
from botocore.exceptions import BotoCoreError, ClientError
import os
from fastapi import HTTPException

def upload_to_s3(file_path, s3_key, bucket_name="frames-bucket"):
    try:
        # Inicializar o cliente S3
        s3_client = boto3.client(
            "s3",
            endpoint_url=os.getenv("AWS_S3_ENDPOINT", "http://localstack:4566"),  # LocalStack
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID", "test"),
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY", "test"),
        )

        # Fazer upload do arquivo
        s3_client.upload_file(file_path, bucket_name, s3_key)

        # Retornar a URL pública do arquivo
        bucket_url = os.getenv("AWS_S3_PUBLIC_URL", f"http://localhost:4566/{bucket_name}")
        file_url = f"{bucket_url}/{s3_key}"
        return file_url
    except (BotoCoreError, ClientError) as e:
        raise HTTPException(status_code=500, detail=f"Erro ao enviar arquivo para o S3: {str(e)}")
