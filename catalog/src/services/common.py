from typing import Optional, TypeVar, Callable, Union

from orjson import loads, dumps

from core.config import settings
from pydantic import BaseModel
from .abstract import AbstractCacheStorage, AbstractDataStorage

T = TypeVar('T', bound=BaseModel)


class RedisService(AbstractCacheStorage):
    async def data_from_cache(self, key: str):
        data = await self.cache_service.get(key)
        if not data:
            return None
        data = loads(data)
        if isinstance(data, list):
            data = [loads(el) for el in data]
        return data

    async def put_data_to_cache(self, key: str, data):
        data = dumps([el.json() for el in data]).decode() if isinstance(data, list) else data.json()
        await self.cache_service.set(key, data, settings.REDIS_CACHE_EXP_SECS)


class BaseService:
    def __init__(self, cache_service: AbstractCacheStorage, storage_service: AbstractDataStorage):
        self.cache_service = cache_service
        self.storage_service = storage_service

    async def _get_data_from_cache_or_storage(self, elastic_get_func: Callable, *args) \
            -> Optional[Union[list[T], T]]:
        key = '_'.join([str(el) for el in [self.storage_service.__class__.__name__, elastic_get_func.__name__, *args]])
        data = await self.cache_service.data_from_cache(key)
        if not data:
            data = await elastic_get_func(*args)
            if not data:
                return None
            await self.cache_service.put_data_to_cache(key, data)
        return data

    async def get_by_id(self, *args):
        return await self._get_data_from_cache_or_storage(
            self.storage_service.get_by_id, *args
        )

    async def get_list(self, *args):
        return await self._get_data_from_cache_or_storage(
            self.storage_service.get_list, *args
        )
