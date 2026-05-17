from http import HTTPStatus

import pytest
from functional.testdata.enums import AuthEndPoint

from tests.functional.fixtures.api_fixtures import Response

from .misc import generate_user

pytestmark = pytest.mark.asyncio


async def test_refresh_token(make_post_request):
    user = generate_user()
    await make_post_request(AuthEndPoint.SIGN_UP, data=user)
    response: Response = await make_post_request(AuthEndPoint.SIGN_IN, data=user)

    cookies = {"refresh_token": response.cookies.get("refresh_token").value}

    response: Response = await make_post_request(AuthEndPoint.REFRESH, cookies=cookies)

    assert response.status == HTTPStatus.OK, response.body
    assert response.cookies.get("access_token")
    assert response.cookies.get("refresh_token")
