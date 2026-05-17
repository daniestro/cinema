from http import HTTPStatus

import pytest
from functional.testdata.enums import AuthEndPoint

from tests.functional.fixtures.api_fixtures import Response

from .misc import generate_user

pytestmark = pytest.mark.asyncio


async def test_sign_in(make_post_request):
    user = generate_user()
    await make_post_request(AuthEndPoint.SIGN_UP, data=user)

    response: Response = await make_post_request(AuthEndPoint.SIGN_IN, data=user)

    assert response.status == HTTPStatus.OK, response.body
    assert response.cookies.get("access_token")
    assert response.cookies.get("refresh_token")


async def test_incorrect_password(make_post_request):
    user = generate_user()
    await make_post_request(AuthEndPoint.SIGN_UP, data=user)

    user["password"] = "1234567"
    response: Response = await make_post_request(AuthEndPoint.SIGN_IN, data=user)

    assert response.status == HTTPStatus.UNAUTHORIZED, response.body


async def test_incorrect_email(make_post_request):
    user = generate_user()
    await make_post_request(AuthEndPoint.SIGN_UP, data=user)

    user["email"] = "opa@mail.ru"
    response: Response = await make_post_request(AuthEndPoint.SIGN_IN, data=user)

    assert response.status == HTTPStatus.UNAUTHORIZED, response.body
