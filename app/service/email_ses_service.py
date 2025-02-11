from botocore.exceptions import ClientError
from app.exceptions.email_send_error import EmailSendError
from app.repository.email_ses_repository import get_email_ses_client

def _send_email(email_to: str, subject: str, body_text: str):
    """
    Função auxiliar que centraliza o envio de e-mails via SES.
    """
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
        raise EmailSendError(f"Erro ao enviar e-mail via SES: {e.response['Error']['Message']}")

def send_reset_password_email_ses(email_to: str, username: str, reset_link: str):
    subject = "Recuperação de Senha"
    body_text = (
        f"Olá {username},\n\n"
        f"Clique no link para recuperar sua senha: {reset_link}"
    )
    return _send_email(email_to, subject, body_text)

def send_file_url_email_ses(email_to: str, username: str, file_url: str):
    subject = "Processamento de vídeo finalizado!"
    body_text = (
        f"Olá {username},\n\n"
        f"Obrigado por utilizar a plataforma Frame Extractor! "
        f"O seu arquivo já está pronto, acesse o link para fazer download do seu arquivo ZIP: {file_url}"
    )
    return _send_email(email_to, subject, body_text)

def send_active_user_email_ses(email_to: str, username: str):
    subject = "Usuário ativado!"
    body_text = (
        f"Olá {username},\n\n"
        f"A sua conta no Frame Extractor foi ativada."
    )
    return _send_email(email_to, subject, body_text)

def send_inactive_user_email_ses(email_to: str, username: str):
    subject = "Usuário inativado!"
    body_text = (
        f"Olá {username},\n\n"
        f"A sua conta no Frame Extractor foi inativada."
    )
    return _send_email(email_to, subject, body_text)
