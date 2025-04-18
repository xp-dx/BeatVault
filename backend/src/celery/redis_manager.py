# src/celery/redis_manager.py
from redis.asyncio import Redis
from .. import config as _global_config


class RedisManager:
    def __init__(self):
        self._sms_client: Redis | None = None
        self._qr_client: Redis | None = None
        self._email_client: Redis | None = None

    async def init(self):
        """Явная инициализация клиентов"""
        self._sms_client = await Redis.from_url(
            f"redis://{_global_config.REDIS_HOST}:{_global_config.REDIS_PORT}/2"
        )
        self._qr_client = await Redis.from_url(
            f"redis://{_global_config.REDIS_HOST}:{_global_config.REDIS_PORT}/3"
        )
        self._email_client = await Redis.from_url(
            f"redis://{_global_config.REDIS_HOST}:{_global_config.REDIS_PORT}/4"
        )

    @property
    def sms_client(self):
        if not self._sms_client:
            raise RuntimeError("RedisManager not initialized")
        return self._sms_client

    @property
    def qr_client(self):
        if not self._qr_client:
            raise RuntimeError("RedisManager not initialized")
        return self._qr_client

    @property
    def email_client(self):
        if not self._email_client:
            raise RuntimeError("RedisManager not initialized")
        return self._email_client

    async def close(self):
        if self._sms_client:
            await self._sms_client.close()
        if self._qr_client:
            await self._qr_client.close()
        if self._email_client:
            await self._email_client.close()


redis_manager = RedisManager()
