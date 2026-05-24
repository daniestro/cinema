from functools import lru_cache
from typing import Optional

from elasticsearch import AsyncElasticsearch, NotFoundError
from fastapi import Depends
from redis.asyncio import Redis

from db.elastic import get_elastic
from db.redis import get_redis
from models.film import Film, DetailFilm, FilmListPage
from .common import RedisService, BaseService
from .abstract import AbstractDataStorage


class FilmService(AbstractDataStorage):
    async def get_by_id(self, film_id) -> Optional[DetailFilm]:
        try:
            doc = await self.storage_service.get(index='movies', id=film_id)
        except NotFoundError:
            return None
        return DetailFilm(**doc['_source'])

    async def get_list(self, genre_id, query, sort, page, page_size) -> Optional[FilmListPage]:

        match_query = {
            'match': {
                'title': {
                    'query': query,
                    'fuzziness': 'auto'
                }
            }
        } if query else {'match_all': {}}

        genre_query = {
            'nested': {
                'path': 'genre',
                'query': {
                    'bool': {
                        'must': [{'term': {'genre.id': genre_id}}] if genre_id else []
                    }
                }
            }
        }

        body = {
            'query': {'bool': {'must': [match_query, genre_query]}},
            'size': page_size,
            'from': (page - 1) * page_size
        }

        if sort:
            sign = sort[0] == '-'
            sort = sort[1:] if sign else sort
            if sort == 'imdb_rating':
                body['sort'] = {'imdb_rating': {'order': 'desc' if sign else 'asc'}}

        try:
            doc = await self.storage_service.search(index='movies', body=body)
        except NotFoundError:
            return None

        items = []
        for film_data in doc['hits']['hits']:
            fp = film_data['_source']
            items.append(Film(
                id=fp['id'],
                title=fp['title'],
                imdb_rating=fp['imdb_rating'],
                poster_url=fp.get('poster_url'),
            ))

        total_raw = doc['hits'].get('total', 0)
        total = total_raw['value'] if isinstance(total_raw, dict) else int(total_raw)

        if not items:
            return None
        return FilmListPage(items=items, total=total)


@lru_cache()
def get_film_service(
        redis: Redis = Depends(get_redis),
        elastic: AsyncElasticsearch = Depends(get_elastic)
) -> BaseService:
    return BaseService(RedisService(redis), FilmService(elastic))

