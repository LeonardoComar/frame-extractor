from botocore.exceptions import BotoCoreError, ClientError
from fastapi import HTTPException
from app.core.config import settings
from app.repository.s3_repository import get_s3_client

def upload_to_s3(file_path: str, s3_key: str, bucket_name: str = settings.AWS_S3_BUCKET_NAME) -> str:
    try:
        # Configurar cliente S3
        s3_client = get_s3_client()
        # Fazer upload do arquivo
        s3_client.upload_file(file_path, bucket_name, s3_key)

        # Construir URL
        file_url = f"{settings.AWS_S3_PUBLIC_URL}/{bucket_name}/{s3_key}"
        
        return file_url
        
    except (BotoCoreError, ClientError) as e:
        error_msg = f"Erro ao enviar {s3_key} para {bucket_name}: {str(e)}"
        raise HTTPException(status_code=500, detail=error_msg)
    
def list_user_frame_archives(username: str) -> list:
    try:
        s3_client = get_s3_client()
        # Prefixo para localizar arquivos do usuário
        prefix = f"{username}/"

        # Listar objetos no bucket com prefixo
        response = s3_client.list_objects_v2(
            Bucket=settings.AWS_S3_BUCKET_NAME,
            Prefix=prefix
        )

        # Verificar se existem objetos
        if 'Contents' not in response:
            return []

        # Filtrar apenas arquivos .zip e gerar URLs
        frame_archives = [
            f"{settings.AWS_S3_PUBLIC_URL}/{settings.AWS_S3_BUCKET_NAME}/{obj['Key']}"
            for obj in response['Contents']
            if obj['Key'].endswith('.zip')
        ]

        return frame_archives

    except (BotoCoreError, ClientError) as e:
        error_msg = f"Erro ao listar arquivos de frames para {username}: {str(e)}"
        raise HTTPException(status_code=500, detail=error_msg)

def delete_s3_file(s3_key: str, bucket_name: str = settings.AWS_S3_BUCKET_NAME) -> None:
    s3_client = get_s3_client()
    try:
        # Excluir o arquivo do S3
        s3_client.delete_object(Bucket=bucket_name, Key=s3_key)
    except s3_client.exceptions.NoSuchKey:
        raise HTTPException(status_code=404, detail="Arquivo não encontrado.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao excluir o arquivo: {str(e)}")