from random import randint
import redis

# Подключение к Redis
redis_client = redis.Redis(host="localhost", port=6379, db=0)


def generate_code(phone: str, expire_seconds: int = 300) -> str:
    """Генерирует 4-значный код и сохраняет в Redis."""
    code = str(randint(10000, 99999))  # Например, 4 цифры
    redis_client.setex(f"phone_verify:{phone}", expire_seconds, code)
    return code
