import aioredis
import pytest_asyncio
from functional.settings import test_settings


@pytest_asyncio.fixture(scope="function")
async def redis_client():
    redis = await aioredis.from_url(f"redis://{test_settings.redis_host}:{test_settings.redis_port}")
    await redis.flushall(asynchronous=True)
    yield redis
    await redis.close()
