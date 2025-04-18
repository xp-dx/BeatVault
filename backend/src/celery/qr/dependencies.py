from fastapi import Depends
from src.celery.redis_manager import redis_manager


async def get_qr_client():
    return redis_manager._qr_client
