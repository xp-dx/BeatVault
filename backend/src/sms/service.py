from twilio.rest import Client
from . import utils as _utils
from src.celery import redis as _redis
from .. import config as _global_config
from random import randint

# Конфиг Twilio (из переменных окружения)
# account_sid = "YOUR_ACCOUNT_SID"
# auth_token = "YOUR_AUTH_TOKEN"
# twilio_phone = "+1234567890"  # Номер Twilio


async def generate_and_store_code(phone: str, expire_seconds: int = 300) -> str:
    """Генерирует и сохраняет код подтверждения в Redis"""
    code = str(randint(1000, 9999))  # 4-значный код
    await _redis.redis_client.setex(f"sms_verify:{phone}", expire_seconds, code)
    return code


async def verify_sms_code(phone: str, code: str) -> bool:
    """Проверяет код подтверждения"""
    stored_code = await _redis.redis_client.get(f"sms_verify:{phone}")
    return stored_code and stored_code.decode() == code


async def send_sms(phone: str, message: str):
    """Заглушка для отправки SMS (реализуйте интеграцию с вашим SMS-шлюзом)"""
    # Реальная реализация будет зависеть от вашего SMS-провайдера
    # Например, для Twilio:
    from twilio.rest import Client

    client = Client(_global_config.TWILIO_SID, _global_config.TWILIO_TOKEN)
    client.messages.create(body=message, to=phone, from_=_global_config.TWILIO_PHONE)
    print(f"SMS to {phone}: {message}")  # Для тестирования
