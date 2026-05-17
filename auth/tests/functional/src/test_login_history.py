from http import HTTPStatus

import pytest
from functional.testdata.enums import AuthEndPoint

from tests.functional.fixtures.api_fixtures import Response

from .misc import generate_user

pytestmark = pytest.mark.asyncio


async def test_login_history(make_get_request, make_post_request):
    user = generate_user()
    await make_post_request(AuthEndPoint.SIGN_UP, data=user)

    await make_post_request(AuthEndPoint.SIGN_IN, data=user)
    await make_post_request(AuthEndPoint.SIGN_IN, data=user)
    response: Response = await make_post_request(AuthEndPoint.SIGN_IN, data=user)

    cookies = {"access_token": response.cookies.get("access_token").value}
    payload = {"limit": 10, "offset": 0}

    response: Response = await make_get_request(AuthEndPoint.LOGIN_HISTORY, cookies=cookies, data=payload)

    assert response.status == HTTPStatus.OK, response.body

    assert len(response.body) == 3
