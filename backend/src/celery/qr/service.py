from redis.asyncio import Redis

from datetime import timedelta, datetime
from random import randint
from jose import jwt
from src import config as _global_config


def create_confirmation_token(email: str):
    expires = datetime.now() + timedelta(minutes=int(_global_config.JWT_EXPIRE_MINUTES))
    to_encode = {"sub": email, "exp": expires}
    return jwt.encode(
        to_encode, _global_config.JWT_SECRET_KEY, algorithm=_global_config.JWT_ALGORITHM
    )


async def generate_code(
    qr_client: Redis,
    phone: str,
    expire_seconds: int = 300,
) -> str:
    """Генерирует 4-значный код и сохраняет в Redis."""
    code = str(randint(10000, 99999))
    await qr_client.setex(f"phone_verify:{phone}", expire_seconds, code)
    return code


async def store_qr_token(
    qr_client: Redis,
    token: str,
    user_data: dict,
    expire_minutes: int = 5,
):
    """Сохраняет токен QR-кода в Redis с указанным временем жизни"""
    await qr_client.hset(f"qr:{token}", mapping=user_data)
    await qr_client.expire(f"qr:{token}", timedelta(minutes=expire_minutes))


async def get_qr_token_data(
    qr_client: Redis,
    token: str,
) -> dict:
    """Получает данные по токену QR-кода"""
    return await qr_client.hgetall(f"qr:{token}")


async def delete_qr_token(
    qr_client: Redis,
    token: str,
):
    """Удаляет токен QR-кода"""
    await qr_client.delete(f"qr:{token}")
