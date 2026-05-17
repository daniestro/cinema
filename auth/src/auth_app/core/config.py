from datetime import timedelta
from logging import config as logging_config
from pathlib import Path
from typing import ClassVar

from pydantic import Field, PostgresDsn
from pydantic_settings import BaseSettings, SettingsConfigDict

from .logger import get_logging_settings


class JaegerSettings(BaseSettings):
    host: str = Field()
    port: int = Field()

    model_config = SettingsConfigDict(env_prefix="auth_jaeger_", env_file=".env")


class RedisSettings(BaseSettings):
    host: str = Field()
    port: int = Field()

    model_config = SettingsConfigDict(env_prefix="auth_redis_", env_file=".env")


class PostgresSettings(BaseSettings):
    user: str = Field()
    password: str = Field()
    host: str = Field()
    port: int = Field()
    db: str = Field()

    model_config = SettingsConfigDict(env_prefix="auth_postgres_", env_file=".env")


class GoogleOAuthSettings(BaseSettings):
    client_id: str = Field()
    client_secret: str = Field()

    model_config = SettingsConfigDict(env_prefix="auth_google_", env_file=".env")


class YandexOAuthSettings(BaseSettings):
    client_id: str = Field()
    client_secret: str = Field()

    model_config = SettingsConfigDict(env_prefix="auth_yandex_", env_file=".env")


class OAuthSettings(BaseSettings):
    google: ClassVar = GoogleOAuthSettings()
    yandex: ClassVar = YandexOAuthSettings()


class ServiceAccountSettings(BaseSettings):
    file_path: Path | None = Field(None)

    model_config = SettingsConfigDict(env_prefix="auth_accounts_", env_file=".env")


class Settings(BaseSettings):
    project_name: str = Field()
    project_root_url: str = Field("")
    jaeger: ClassVar = JaegerSettings()
    redis: ClassVar = RedisSettings()
    db: ClassVar = PostgresSettings()
    oauth: ClassVar = OAuthSettings()
    service_account_settings: ClassVar = ServiceAccountSettings()
    database_dsn: PostgresDsn = PostgresDsn.build(
        scheme="postgresql+asyncpg",
        username=db.user,
        password=db.password,
        host=db.host,
        port=db.port,
    )
    rsa_public_path: Path = Field()
    rsa_private_path: Path = Field()

    logging_level: str = Field("INFO")
    console_logging_level: str = Field("DEBUG")
    debug_mode: bool = Field(False)

    access_token_lifetime: timedelta = Field(timedelta(hours=6))
    refresh_token_lifetime: timedelta = Field(timedelta(hours=6))

    request_limit_per_minute: int = Field(60)

    debug: bool = Field(False)

    model_config = SettingsConfigDict(env_prefix="auth_", env_file=".env")


BASE_DIR = Path(__file__).parent.parent
settings = Settings()  # type: ignore

logging_config.dictConfig(
    get_logging_settings(
        settings.logging_level,
        settings.console_logging_level,
    ),
)
