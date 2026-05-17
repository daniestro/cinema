from logging import config as logging_config

from pydantic import BaseSettings
from dotenv import find_dotenv

from core.logger import LOGGING


logging_config.dictConfig(LOGGING)


class Settings(BaseSettings):
    PROJECT_NAME: str = 'movies'
    PROJECT_ROOT_URL: str = ''

    REDIS_HOST: str = 'redis'
    REDIS_PORT: int = 6379
    REDIS_CACHE_EXP_SECS: int = 300

    ELASTIC_HOST: str = 'elasticsearch'
    ELASTIC_PORT: int = 9200

    # JWT теперь RS256 с публичным ключом auth (он же docker secret)
    jwt_algorithm: str = 'RS256'
    rsa_public_path: str = '/run/secrets/rsa_public'

    jaeger_agent_host_name: str = 'jaeger'
    jaeger_agent_port: int = 6831

    class Config:
        env_file = find_dotenv()
        env_file_encoding = 'utf-8'


settings = Settings()
