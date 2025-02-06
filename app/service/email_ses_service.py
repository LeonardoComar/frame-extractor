# app/service/email_ses_service.py
from botocore.exceptions import ClientError
from app.repository.email_ses_repository import get_email_ses_client

def send_reset_password_email_ses(email_to: str, username: str, reset_link: str):
    subject = "Recuperação de Senha"
    body_text = f"Olá {username},\n\nClique no link para recuperar sua senha: {reset_link}"
    
    try:
        ses_client = get_email_ses_client()
        response = ses_client.send_email(
            Source="noreply@frameextractor.com",
            Destination={
                "ToAddresses": [email_to],
            },
            Message={
                "Subject": {
                    "Data": subject,
                    "Charset": "UTF-8"
                },
                "Body": {
                    "Text": {
                        "Data": body_text,
                        "Charset": "UTF-8"
                    }
                }
            }
        )
        return response
    except ClientError as e:
        raise Exception(f"Erro ao enviar e-mail via SES: {e.response['Error']['Message']}")
    

def send_file_url_email_ses(email_to: str, username: str, file_url: str):    
    subject = "Processamento de vídeo finalizado!"
    body_text = f"Olá {username},\n\nObrigado por utilizar a plataforma Frame Extractor! O seu arquivo já está pronto, acesse o link para fazer download do seu arquivo ZIP: {file_url}"
    
    try:
        ses_client = get_email_ses_client()
        response = ses_client.send_email(
            Source="noreply@frameextractor.com",
            Destination={
                "ToAddresses": [email_to],
            },
            Message={
                "Subject": {
                    "Data": subject,
                    "Charset": "UTF-8"
                },
                "Body": {
                    "Text": {
                        "Data": body_text,
                        "Charset": "UTF-8"
                    }
                }
            }
        )
        return response
    except ClientError as e:
        raise Exception(f"Erro ao enviar e-mail via SES: {e.response['Error']['Message']}")
