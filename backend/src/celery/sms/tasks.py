from src.celery.celery_app import celery_app
from . import service as _sms_service


@celery_app.task
async def send_phone_confirmation_sms_async(phone: str):
    """Отправляет SMS с кодом подтверждения"""
    code = await _sms_service.generate_and_store_code(phone)
    message = f"Ваш код подтверждения: {code}"
    await _sms_service.send_sms(phone, message)
    return f"Confirmation SMS sent to {phone}"
