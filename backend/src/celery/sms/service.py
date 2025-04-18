import redis
from twilio.rest import Client
from random import randint
import src.config as _global_config


async def generate_and_store_code(
    sms_client: redis.Redis,
    phone: str,
    expire_seconds: int = 300,
) -> str:
    """Генерирует и сохраняет код подтверждения в Redis"""
    code = str(randint(1000, 9999))  # 4-значный код
    await sms_client.setex(f"sms_verify:{phone}", expire_seconds, code)
    return code


async def verify_sms_code(sms_client: redis.Redis, phone: str, code: str) -> bool:
    """Проверяет код подтверждения"""
    stored_code = await sms_client.get(f"sms_verify:{phone}")
    return stored_code and stored_code.decode() == code


async def send_sms(phone: str, message: str):
    """Заглушка для отправки SMS (реализуйте интеграцию с вашим SMS-шлюзом)"""
    client = Client(_global_config.TWILIO_SID, _global_config.TWILIO_TOKEN)
    client.messages.create(body=message, to=phone, from_=_global_config.TWILIO_PHONE)
    print(f"SMS to {phone}: {message}")  # Для тестирования
