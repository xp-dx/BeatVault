from fastapi import Depends
from src.celery.redis_manager import redis_manager


async def get_sms_client():
    return redis_manager.sms_client
