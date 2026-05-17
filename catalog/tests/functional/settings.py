from pydantic import BaseSettings
from dotenv import find_dotenv

from testdata.es_mapping import mappings


class TestSettings(BaseSettings):
    ES_MAPPINGS: dict = mappings

    # Настройки Redis
    REDIS_HOST: str = 'redis'
    REDIS_PORT: int = 6379
    REDIS_CACHE_EXP_SECS: int = 300

    # Настройки Elasticsearch
    ELASTIC_HOST: str = 'elasticsearch'
    ELASTIC_PORT: int = 9200

    SERVICE_URL: str = 'http://nginx:80'

    class Config:
        env_file = find_dotenv()
        env_file_encoding = 'utf-8'


test_settings = TestSettings()
