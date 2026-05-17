import time

import pytest
import asyncio
import pytest_asyncio
from elasticsearch import AsyncElasticsearch
from redis.asyncio import Redis

from settings import test_settings
from testdata.es_mapping import mappings


@pytest.fixture(scope="session")
def event_loop():
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()

    yield loop

    loop.close()


@pytest_asyncio.fixture(scope='session', autouse=True)
async def elasticsearch_session():
    es_client = AsyncElasticsearch(hosts=f'{test_settings.ELASTIC_HOST}:{test_settings.ELASTIC_PORT}',
                                   validate_cert=False,
                                   use_ssl=False)

    for key, value in mappings.items():
        await es_client.indices.create(index=key, body=value)

    yield es_client

    for key in mappings:
        await es_client.indices.delete(index=key, ignore_unavailable=True)

    await es_client.close()


@pytest_asyncio.fixture(scope='session', autouse=True)
async def redis_session():
    redis_client = Redis(host=test_settings.REDIS_HOST, port=test_settings.REDIS_PORT)

    yield redis_client

    await redis_client.close()


@pytest.fixture(autouse=True)
def slow_down_tests():
    yield
    time.sleep(1)
