import aiosmtplib
import asyncio
from email.mime.text import MIMEText
from src.celery import celery_app
from src.config import SMTP_HOST, SMTP_PASSWORD, SMTP_PORT, SMTP_USER


async def send_email(to: str, subject: str, body: str):
    """Функция для отправки письма."""
    message = MIMEText(body)
    message["From"] = SMTP_USER
    message["To"] = to
    message["Subject"] = subject

    await aiosmtplib.send(
        message,
        hostname=SMTP_HOST,
        port=SMTP_PORT,
        username=SMTP_USER,
        password=SMTP_PASSWORD,
        use_tls=True,
    )


@celery_app.task
async def send_confirmation_email_async(to: str, confirmation_url: str):
    subject = "Подтверждение регистрации"
    body = f"Для подтверждения регистрации перейдите по ссылке: {confirmation_url}"
    await send_email(to, subject, body)
    return f"Confirmation email sent to {to}"
