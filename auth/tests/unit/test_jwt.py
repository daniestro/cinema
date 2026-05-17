import time
import uuid
from datetime import timedelta

import pytest
from auth_app.errors.services import InvalidTokenError
from auth_app.errors.services.main import ExpiredJwtError
from auth_app.services.jwt_service import JWTService


def test_encode(get_jwt_service):
    jwt_service: JWTService = get_jwt_service(timedelta(seconds=30), timedelta(seconds=30))
    user_id = str(uuid.uuid4())
    token = jwt_service.encode_access_token(user_id, "email@mail.ru", ["sample"])

    assert user_id == jwt_service.decode_access_token(token)["sub"]


def test_invalid_token(get_jwt_service):
    jwt_service: JWTService = get_jwt_service(timedelta(seconds=30), timedelta(seconds=30))
    user_id = str(uuid.uuid4())
    token = jwt_service.encode_access_token(user_id, "email@mail.ru", ["sample"])

    with pytest.raises(InvalidTokenError):
        jwt_service.decode_access_token(token + "1")


def test_expired_token(get_jwt_service):
    jwt_service: JWTService = get_jwt_service(timedelta(microseconds=1), timedelta(seconds=30))
    user_id = str(uuid.uuid4())
    token = jwt_service.encode_access_token(user_id, "email@mail.ru", ["sample"])

    time.sleep(1)

    with pytest.raises(ExpiredJwtError):
        jwt_service.decode_access_token(token)


def test_refresh_token(get_jwt_service):
    jwt_service: JWTService = get_jwt_service(timedelta(seconds=30), timedelta(seconds=30))
    user_id = str(uuid.uuid4())
    refresh_token = jwt_service.encode_refresh_token(user_id, "email@mail.ru", ["sample"])

    new_token = jwt_service.refresh_token(refresh_token)

    assert jwt_service.decode_access_token(new_token)["sub"] == user_id


def test_expired_refresh_token(get_jwt_service):
    jwt_service: JWTService = get_jwt_service(timedelta(microseconds=1), timedelta(microseconds=1))
    user_id = str(uuid.uuid4())
    refresh_token = jwt_service.encode_refresh_token(user_id, "email@mail.ru", ["sample"])

    time.sleep(1)

    with pytest.raises(ExpiredJwtError):
        jwt_service.refresh_token(refresh_token)
