from random import randint
import aiosmtplib
import asyncio


import secrets
import qrcode
import io

from email.mime.text import MIMEText
from src.sms import service as _sms_service
from src.qr import service as _qr_service
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


@celery_app.task
async def send_phone_confirmation_sms_async(phone: str):
    """Отправляет SMS с кодом подтверждения"""
    code = await _sms_service.generate_and_store_code(phone)
    message = f"Ваш код подтверждения: {code}"
    await _sms_service.send_sms(phone, message)
    return f"Confirmation SMS sent to {phone}"


# @celery_app.task
# async def send_phone_notification_sms_async(phone: str, message: str):
#     """Отправляет произвольное SMS-уведомление"""
#     await _sms_service.send_sms(phone, message)
#     return f"Notification SMS sent to {phone}"


# @celery_app.task
# def send_sms_async(phone: str):
#     _sms_service.send_sms_code(phone)
#     return f"Code sent to {to}"


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


# @celery_app.task
# async def generate_login_qr_task(user_id: str = None):
#     """Генерирует QR-код для входа и сохраняет токен в Redis"""
#     token = secrets.token_urlsafe(32)

#     # Сохраняем токен в Redis
#     await _qr_service.store_qr_token(
#         token,
#         {
#             "status": "pending",
#             "user_id": str(user_id) if user_id else "",
#             "authenticated": "false",
#         },
#     )

#     # Генерируем URL для входа
#     login_url = f"http://127.0.0.1:8000/auth-via-qr/?token={token}"

#     # Создаем QR-код
#     qr = qrcode.QRCode(
#         version=1,
#         error_correction=qrcode.constants.ERROR_CORRECT_L,
#         box_size=10,
#         border=4,
#     )
#     qr.add_data(login_url)
#     qr.make(fit=True)

#     img = qr.make_image(fill_color="black", back_color="white")

#     # Сохраняем изображение в байты
#     buf = io.BytesIO()
#     img.save(buf, format="PNG")
#     buf.seek(0)

#     return {"token": token, "qr_image": buf.getvalue(), "login_url": login_url}


# @celery_app.task
# async def verify_qr_token_task(token: str):
#     """Проверяет статус токена QR-кода"""
#     data = await _qr_service.get_qr_token_data(token)
#     if not data:
#         return {"status": "invalid", "message": "Token not found"}

#     return {
#         "status": data.get("status", "pending"),
#         "user_id": data.get("user_id", ""),
#         "authenticated": data.get("authenticated", "false"),
#     }


# @celery_app.task
# async def authenticate_via_qr_task(token: str, user_id: str):
#     """Аутентифицирует пользователя через QR-код"""
#     data = await _qr_service.get_qr_token_data(token)
#     if not data:
#         return {"status": "error", "message": "Invalid token"}

#     # Обновляем статус токена
#     await _qr_service.store_qr_token(
#         token,
#         {"status": "authenticated", "user_id": str(user_id), "authenticated": "true"},
#     )

#     return {"status": "success", "user_id": user_id}
