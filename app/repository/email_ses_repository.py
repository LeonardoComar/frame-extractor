# app/repository/email_ses_repository.py
import boto3
from botocore.exceptions import ClientError
from app.core.config import settings

def get_email_ses_client():
    """
    Inicializa e retorna o cliente SES configurado.
    """
    return boto3.client(
        "ses",
        endpoint_url=settings.AWS_SES_ENDPOINT,
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        region_name=settings.AWS_DEFAULT_REGION
    )

def verify_ses_email_identity():
    """
    Verifica o e-mail no SES para ambiente local.
    """
    ses_client = get_email_ses_client()
    email = "noreply@frameextractor.com"  # E-mail padrão para ambiente local
    
    try:
        # Verifica se o e-mail já está verificado
        response = ses_client.list_verified_email_addresses()
        if email not in response['VerifiedEmailAddresses']:
            ses_client.verify_email_identity(EmailAddress=email)
            print(f"E-mail {email} verificado com sucesso no SES")
        else:
            print(f"E-mail {email} já está verificado")
            
    except ClientError as e:
        if e.response['Error']['Code'] == 'AlreadyExists':
            print(f"E-mail {email} já está verificado")
        else:
            print(f"Erro ao verificar e-mail no SES: {e}")
            raise