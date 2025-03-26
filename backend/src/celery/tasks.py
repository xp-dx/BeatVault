from random import randint
import aiosmtplib
import asyncio

from email.mime.text import MIMEText
from src.celery import celery_app
from src.config import SMTP_HOST, SMTP_PASSWORD, SMTP_PORT, SMTP_USER

from . import redis as _redis


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


# @celery_app.task
# async def send_password_reset_code_async(email: str):
#     # Генерируем 6-значный код
#     reset_code = str(randint(100000, 999999))

#     # Сохраняем код в Redis с TTL 15 минут
#     await _redis.redis_client.setex(f"password_reset:{email}", 900, reset_code)

#     subject = "Код для смены пароля"
#     body = f"Ваш код для смены пароля: {reset_code}\nКод действителен 15 минут."


#     await send_email(email, subject, body)
#     return f"Password reset code sent to {email}"
# @celery_app.task
# async def send_password_reset_code_async(email: str):
#     try:
#         reset_code = str(randint(100000, 999999))
#         await _redis.redis_client.setex(f"password_reset:{email}", 900, reset_code)

#         subject = "Код для смены пароля"
#         body = f"Ваш код: {reset_code}"
#         await send_email(email, subject, body)


#         return {"status": "success", "email": email}  # Явный возврат результата
#     except Exception as e:
#         return {"status": "error", "error": str(e)}
@celery_app.task
async def send_password_reset_email_async(email: str, reset_url: str):
    subject = "Password Reset Request"
    body = f"Click to reset your password: {reset_url}"
    await send_email(email, subject, body)
