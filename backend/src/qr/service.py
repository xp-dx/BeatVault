# from src.celery import redis as _redis
# from datetime import timedelta


# async def store_qr_token(token: str, user_data: dict, expire_minutes: int = 5):
#     """Сохраняет токен QR-кода в Redis с указанным временем жизни"""
#     await _redis.redis_client.hset(f"qr:{token}", mapping=user_data)
#     await _redis.redis_client.expire(f"qr:{token}", timedelta(minutes=expire_minutes))


# async def get_qr_token_data(token: str) -> dict:
#     """Получает данные по токену QR-кода"""
#     return await _redis.redis_client.hgetall(f"qr:{token}")


# async def delete_qr_token(token: str):
#     """Удаляет токен QR-кода"""
#     await _redis.redis_client.delete(f"qr:{token}")
