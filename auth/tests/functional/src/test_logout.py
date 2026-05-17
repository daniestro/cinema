from http import HTTPStatus

import pytest
from functional.testdata.enums import AuthEndPoint

from tests.functional.fixtures.api_fixtures import Response

from .misc import generate_user

pytestmark = pytest.mark.asyncio


async def test_logout(make_post_request, make_get_request):
    """Проверяется возможность выйти из аккаунта.

    1. Аккаунт создается
    2. Логин
    3. Выход
    4. Попытка получить данные по старому токену
    """
    user = generate_user()
    await make_post_request(AuthEndPoint.SIGN_UP, data=user)
    response: Response
    response = await make_post_request(AuthEndPoint.SIGN_IN, data=user)

    cookies = {
        "access_token": response.cookies.get("access_token").value,
        "refresh_token": response.cookies.get("access_token").value,
    }

    response = await make_post_request(AuthEndPoint.LOGOUT, cookies=cookies)

    assert response.status == HTTPStatus.OK, response.body

    response = await make_get_request(AuthEndPoint.LOGIN_HISTORY, cookies=cookies)

    assert response.status == HTTPStatus.UNAUTHORIZED, response.body


async def test_logout_invalid_token(make_post_request):
    cookies = {
        "access_token": "opachki",
        "refresh_token": "opachki",
    }
    response: Response = await make_post_request(AuthEndPoint.LOGOUT, cookies=cookies)

    assert response.status == HTTPStatus.UNAUTHORIZED, response.body
