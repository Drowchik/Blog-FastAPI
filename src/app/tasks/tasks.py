import smtplib
from pydantic import EmailStr
from src.app.tasks.celery import celery
from src.app.tasks.email_templates import create_confirmation_template
from src.app.core.config import settings


@celery.task
def send_confirmation_email(
    user: dict,
    email_to: EmailStr
):
    msg_content = create_confirmation_template(user, email_to)
    
    with smtplib.SMTP_SSL(settings.smtp_host, settings.smtp_port) as server:
        server.login(settings.email, settings.password)
        server.send_message(msg_content)