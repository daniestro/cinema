from functools import lru_cache
from typing import Optional

from elasticsearch import AsyncElasticsearch, NotFoundError
from fastapi import Depends
from redis.asyncio import Redis

from db.elastic import get_elastic
from db.redis import get_redis
from .common import BaseService, RedisService
from .abstract import AbstractDataStorage
from models.genre import Genre


class GenreService(AbstractDataStorage):
    async def get_by_id(self, genre_id) -> Optional[Genre]:
        try:
            doc = await self.storage_service.get(index='genres', id=genre_id)
        except NotFoundError:
            return None
        return Genre(**doc['_source'])

    async def get_list(self) -> Optional[list[Genre]]:
        search_body = {'size': 100}
        try:
            doc = await self.storage_service.search(index='genres', body=search_body)
        except NotFoundError:
            return None

        result = []
        for genre_data in doc['hits']['hits']:
            result.append(Genre(**genre_data['_source']))

        return result


@lru_cache()
def get_genre_service(
        redis: Redis = Depends(get_redis),
        elastic: AsyncElasticsearch = Depends(get_elastic),
) -> BaseService:
    return BaseService(RedisService(redis), GenreService(elastic))
