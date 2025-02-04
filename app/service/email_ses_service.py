# app/email_ses.py
from botocore.exceptions import ClientError
from app.repository.email_ses_repository import get_email_ses_client

def send_reset_password_email_ses(email_to: str, username: str, reset_link: str):
    subject = "Recuperação de Senha"
    body_text = f"Olá {username},\n\nClique no link para recuperar sua senha: {reset_link}"
    
    try:
        ses_client = get_email_ses_client()  # Obter o cliente configurado
        response = ses_client.send_email(
            Source="noreply@frameextractor.com",  # Utilize um e-mail verificado ou um valor dummy para testes
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
