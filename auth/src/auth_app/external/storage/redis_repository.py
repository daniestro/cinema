from datetime import timedelta
from functools import lru_cache
from typing import Any

from fastapi import Depends
from redis.asyncio import Redis

from auth_app.db.redis import get_redis

from .base import BaseStorageRepository


class RedisStorageRepository(BaseStorageRepository):
    def __init__(self, redis: Redis) -> None:
        self.redis = redis

    async def get(self, key: Any) -> Any:
        return await self.redis.get(key)

    async def put(self, key: Any, value: Any, expires_in: timedelta) -> None:
        await self.redis.set(
            key,
            value,
            expires_in,
        )


@lru_cache()
def get_storage_repository(redis: Redis = Depends(get_redis)) -> RedisStorageRepository:
    return RedisStorageRepository(redis)
