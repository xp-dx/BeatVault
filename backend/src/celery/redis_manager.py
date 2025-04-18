# src/celery/redis_manager.py
from redis.asyncio import Redis
from .. import config as _global_config


class RedisManager:
    def __init__(self):
        self._email_client: Redis | None = None

    async def init(self):
        self._email_client = await Redis.from_url(
            f"redis://{_global_config.REDIS_HOST}:{_global_config.REDIS_PORT}/2"
        )

    @property
    def email_client(self):
        if not self._email_client:
            raise RuntimeError("RedisManager not initialized")
        return self._email_client

    async def close(self):
        if self._email_client:
            await self._email_client.close()


redis_manager = RedisManager()
