# src/redis.py
from redis.asyncio import Redis
from src.config import REDIS_URL

redis_client = Redis.from_url(REDIS_URL)
