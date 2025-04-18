import secrets
import io
import qrcode
from redis.asyncio import Redis

from src.celery.celery_app import celery_app

from . import service as _qr_service


@celery_app.task
async def generate_login_qr_task(qr_client: Redis, user_id: str = None):
    """Генерирует QR-код для входа и сохраняет токен в Redis"""
    token = secrets.token_urlsafe(32)

    # Сохраняем токен в Redis
    await _qr_service.store_qr_token(
        qr_client,
        token,
        {
            "status": "pending",
            "user_id": str(user_id) if user_id else "",
            "authenticated": "false",
        },
    )

    # Генерируем URL для входа
    login_url = f"http://127.0.0.1:8000/auth-via-qr/?token={token}"

    # Создаем QR-код
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(login_url)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")

    # Сохраняем изображение в байты
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)

    return {"token": token, "qr_image": buf.getvalue(), "login_url": login_url}


@celery_app.task
async def verify_qr_token_task(token: str):
    """Проверяет статус токена QR-кода"""
    data = await _qr_service.get_qr_token_data(token)
    if not data:
        return {"status": "invalid", "message": "Token not found"}

    return {
        "status": data.get("status", "pending"),
        "user_id": data.get("user_id", ""),
        "authenticated": data.get("authenticated", "false"),
    }


@celery_app.task
async def authenticate_via_qr_task(qr_client: Redis, token: str):
    """Аутентифицирует пользователя через QR-код"""
    data = await _qr_service.get_qr_token_data(qr_client, token)
    if not data:
        return {"status": "error", "message": "Invalid token"}

    # Обновляем статус токена
    await _qr_service.store_qr_token(
        qr_client,
        token,
        {"status": "authenticated", "user_id": str(1), "authenticated": "true"},
    )

    return {"status": "success", "user_id": 1}
