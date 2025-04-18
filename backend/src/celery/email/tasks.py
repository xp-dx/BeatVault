from src.celery.celery_app import celery_app
from . import service as _email_service


@celery_app.task
async def send_confirmation_email_async(email: str, confirmation_url: str):
    subject = "Подтверждение регистрации"
    body = f"Для подтверждения регистрации перейдите по ссылке: {confirmation_url}"
    await _email_service.send_email(email, subject, body)
    return f"Confirmation email sent to {email}"


@celery_app.task
async def send_password_reset_email_async(email: str, reset_url: str):
    subject = "Password Reset Request"
    body = f"Click to reset your password: {reset_url}"
    await _email_service.send_email(email, subject, body)
    return f"Reset email sent to {email}"
