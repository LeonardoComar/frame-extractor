# app/exceptions/email_send_error.py

class EmailSendError(Exception):
    """
    Exceção levantada quando ocorre um erro ao enviar e-mail via SES.
    """
    pass
