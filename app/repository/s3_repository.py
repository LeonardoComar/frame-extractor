import boto3
from botocore.exceptions import ClientError
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

def create_s3_bucket():
    """
    Cria o bucket S3 se não existir, usando as configurações do ambiente.
    """
    s3_client = get_s3_client()
    bucket_name = settings.AWS_S3_BUCKET_NAME
    
    try:
        s3_client.create_bucket(
            Bucket=bucket_name
        )
        print(f"Bucket S3 '{bucket_name}' criado com sucesso")
        
        s3_client.put_bucket_versioning(
            Bucket=bucket_name,
            VersioningConfiguration={'Status': 'Enabled'}
        )
        
    except ClientError as e:
        if e.response['Error']['Code'] == 'BucketAlreadyOwnedByYou':
            print(f"Bucket '{bucket_name}' já existe")
        else:
            print(f"Erro ao criar bucket S3: {e}")
            raise