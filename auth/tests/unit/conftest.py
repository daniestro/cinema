from datetime import timedelta

import pytest
from auth_app.services.jwt_service import JWTService

from .misc import get_rsa


@pytest.fixture(scope="session")
def get_jwt_service():
    def _inner(lifetime: timedelta, refresh_lifetime: timedelta) -> JWTService:
        rsa = get_rsa()
        return JWTService(
            private_key=rsa.private,
            public_key=rsa.public,
            access_token_lifetime=lifetime,
            refresh_token_lifetime=refresh_lifetime,
        )

    return _inner
