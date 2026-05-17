from redis import Redis

from settings import test_settings
from utils.helpers import backoff


@backoff('redis')
def redis_connection(client: Redis):
    return client.ping()


if __name__ == '__main__':
    redis_client = Redis(
        host=test_settings.REDIS_HOST,
        port=test_settings.REDIS_PORT
    )
    redis_connection(redis_client)
