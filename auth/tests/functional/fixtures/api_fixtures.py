from dataclasses import dataclass
from http.cookies import SimpleCookie
from typing import Any

import aiohttp
import pytest
from functional.settings import test_settings


@dataclass
class Response:
    body: Any
    status: int
    cookies: SimpleCookie
    headers: dict


async def get_response(client_response: aiohttp.ClientResponse) -> Response:
    try:
        body = await client_response.json()
    except aiohttp.ContentTypeError:
        body = None
    return Response(
        body=body,
        status=client_response.status,
        cookies=client_response.cookies,
        headers=client_response.headers,
    )


@pytest.fixture
def make_post_request():
    async def inner(url: str, data: dict | None = None, cookies: dict | None = None) -> Response:
        session = aiohttp.ClientSession(cookies=cookies)

        url = f"{test_settings.service_url}{url}"
        async with session.post(url, json=data) as response:
            _response = await get_response(response)
            await session.close()
            return _response

    return inner


@pytest.fixture
def make_get_request():
    async def inner(url: str, data: dict | None = None, cookies: dict | None = None):
        session = aiohttp.ClientSession(cookies=cookies)
        url = f"{test_settings.service_url}{url}"
        async with session.get(url, json=data) as response:
            _response = await get_response(response)
            await session.close()
            return _response

    return inner
