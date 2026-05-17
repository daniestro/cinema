import pytest
from typing import Optional

import aiohttp
from elasticsearch import AsyncElasticsearch
from redis.asyncio import Redis
from orjson import loads

from settings import test_settings
from utils.helpers import get_es_bulk_query


@pytest.fixture
def es_write_data(elasticsearch_session: AsyncElasticsearch):
    async def inner(data: list[dict], es_index: str):
        bulk_query = get_es_bulk_query(data, es_index)
        response = await elasticsearch_session.bulk(bulk_query, refresh=True)
        if response['errors']:
            raise Exception('Ошибка записи данных в Elasticsearch')
    return inner


@pytest.fixture
def cleanup(elasticsearch_session: AsyncElasticsearch, redis_session: Redis):
    async def inner(indices_names: list[str]):
        await elasticsearch_session.delete_by_query(index=indices_names, body={"query": {"match_all": {}}})
        await redis_session.flushall()

    return inner


@pytest.fixture
def make_get_request():
    async def inner(endpoint: str, query_data: dict) -> tuple[int, list | dict]:
        url = test_settings.SERVICE_URL + '/api/v1' + endpoint
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=query_data) as response:
                body = await response.json()
                status = response.status
                return status, body

    return inner


@pytest.fixture
def get_data_from_cache(redis_session: Redis):
    async def inner(key: str) -> Optional[list[dict] | list]:
        data = await redis_session.get(key)
        if not data:
            return None
        data = loads(data)
        if isinstance(data, list):
            data = [loads(el) for el in data]
        return data

    return inner
