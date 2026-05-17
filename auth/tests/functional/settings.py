from pathlib import Path

from pydantic import BaseSettings, Field

BASE_DIR = Path(__file__).parent.parent


class TestSettings(BaseSettings):
    service_url: str = Field()

    redis_host: str = Field()
    redis_port: int = Field()

    class Config:
        env_file = ".env"
        env_prefix = "auth_"


test_settings = TestSettings()
