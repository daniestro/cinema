from http import HTTPStatus

import pytest
from functional.testdata.enums import AuthEndPoint

from tests.functional.fixtures.api_fixtures import Response

from .misc import generate_user

pytestmark = pytest.mark.asyncio


async def test_sign_up(make_post_request):
    user = generate_user()
    response: Response = await make_post_request(AuthEndPoint.SIGN_UP, data=user)

    assert response.status == HTTPStatus.CREATED, response.body


async def test_invalid_email(make_post_request):
    user = generate_user()
    user["email"] = "test"
    response: Response = await make_post_request(AuthEndPoint.SIGN_UP, data=user)

    assert response.status == HTTPStatus.UNPROCESSABLE_ENTITY, response.body


async def test_short_password(make_post_request):
    user = generate_user()
    user["password"] = "123"
    response: Response = await make_post_request(AuthEndPoint.SIGN_UP, data=user)

    assert response.status == HTTPStatus.UNPROCESSABLE_ENTITY, response.body


async def test_weak_password(make_post_request):
    user = generate_user()
    user["password"] = "12345678"
    response: Response = await make_post_request(AuthEndPoint.SIGN_UP, data=user)

    assert response.status == HTTPStatus.UNPROCESSABLE_ENTITY, response.body


async def test_already_taken_email(make_post_request):
    user = generate_user()
    await make_post_request(AuthEndPoint.SIGN_UP, data=user)
    response: Response = await make_post_request(AuthEndPoint.SIGN_UP, data=user)

    assert response.status == HTTPStatus.CONFLICT, response.body
