from dotenv import find_dotenv

from pydantic import BaseSettings, Field


class DatabaseSettings(BaseSettings):
    dbname: str = Field(..., env='DB_NAME')
    user: str = ...
    password: str = ...
    host: str = ...
    port: int = ...

    class Config:
        env_prefix = 'db_'
        env_file = find_dotenv()
        env_file_encoding = 'utf-8'


class ElasticSettings(BaseSettings):
    host: str = ...
    port: int = ...

    class Config:
        env_prefix = 'es_'
        env_file = find_dotenv()
        env_file_encoding = 'utf-8'


database_settings = DatabaseSettings()
elastic_settings = ElasticSettings()
