from functools import lru_cache
from typing import Optional, Union

from elasticsearch import AsyncElasticsearch, NotFoundError
from fastapi import Depends
from redis.asyncio import Redis

from db.elastic import get_elastic
from db.redis import get_redis

from .abstract import AbstractDataStorage
from .common import RedisService, BaseService
from models.person import PersonWithFilms
from models.film import Film, DetailFilm


class PersonService(AbstractDataStorage):
    async def get_by_id(self, persons_id: str) -> Optional[PersonWithFilms]:
        return await self._get_person_from_elastic([persons_id], True)

    async def get_list(self, person_id: str, query: str, page: int, page_size: int):
        # Если передан ID персоны, то отдаем список его фильмов
        if person_id:
            return await self._get_person_films_from_elastic(person_id)

        # Поиск персон query
        return await self._get_person_search_from_elastic(query, page, page_size)

    async def _get_person_films_raw(self, person_ids: list[str]) -> Optional[list[DetailFilm]]:
        search_query = {
            'bool': {
                'should': [
                    {'nested': {
                        'path': 'actors',
                        'query': {'terms': {'actors.id': person_ids}}
                    }},
                    {'nested': {
                        'path': 'writers',
                        'query': {'terms': {'writers.id': person_ids}}
                    }},
                    {'nested': {
                        'path': 'directors',
                        'query': {'terms': {'directors.id': person_ids}}
                    }}
                ]
            }
        }
        body = {
            'query': search_query,
            'size': 1000
        }
        try:
            search_response = await self.storage_service.search(index='movies', body=body)
        except NotFoundError:
            return None

        return [DetailFilm(**hit['_source']) for hit in search_response['hits']['hits']]

    async def _get_person_from_elastic(self, persons_ids: list[str], one_person_return=True) -> Optional[Union[PersonWithFilms, list[PersonWithFilms]]]:
        detailed_films = await self._get_person_films_raw(persons_ids)

        if not detailed_films:
            return None

        persons = []
        for person_id in persons_ids:
            person_data = {
                'id': person_id,
                'full_name': '',
                'films': []
            }

            for detailed_film in detailed_films:
                if not isinstance(detailed_film, dict):
                    detailed_film = detailed_film.dict()

                film = {
                    'uuid': detailed_film['uuid'],
                    'roles': []
                }

                roles_fields = {
                    'actors': 'actor',
                    'writers': 'writer',
                    'directors': 'director'
                }

                for role_filed in roles_fields:
                    for person in detailed_film[role_filed]:
                        if str(person['uuid']) == str(person_id):
                            film['roles'].append(roles_fields[role_filed])
                            if not person_data['full_name']:
                                person_data['full_name'] = person['full_name']

                if film['roles']:
                    person_data['films'].append(film)

            persons.append(person_data)

        if one_person_return:
            return PersonWithFilms(**persons[0])

        return [PersonWithFilms(**person) for person in persons]

    async def _get_person_films_from_elastic(self, person_id: str) -> Optional[list[Film]]:
        detailed_films = await self._get_person_films_raw([person_id])

        if not detailed_films:
            return None

        films = []
        for detailed_film in detailed_films:
            if not isinstance(detailed_film, dict):
                detailed_film = detailed_film.dict()
            films.append(
                Film(
                    id=detailed_film['uuid'],
                    title=detailed_film['title'],
                    imdb_rating=detailed_film['imdb_rating']
                )
            )

        return films

    async def _get_person_search_from_elastic(self, query: str, page: int, page_size: int) -> Optional[PersonWithFilms]:

        match_query = {
            'match': {
                'full_name': {
                    'query': query,
                    'fuzziness': 'auto'
                }
            }
        } if query else {'match_all': {}}

        body = {
            'query': match_query,
            'size': page_size,
            'from': (page - 1) * page_size
        }

        try:
            doc = await self.storage_service.search(index='persons', body=body)
        except NotFoundError:
            return None

        persons_ids = [hit['_id'] for hit in doc['hits']['hits']]

        return await self._get_person_from_elastic(persons_ids, False)


@lru_cache()
def get_person_service(
        redis: Redis = Depends(get_redis),
        elastic: AsyncElasticsearch = Depends(get_elastic),
) -> BaseService:
    return BaseService(RedisService(redis), PersonService(elastic))
