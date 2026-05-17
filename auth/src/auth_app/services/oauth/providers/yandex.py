from http import HTTPStatus
from urllib.parse import urlencode

import httpx

from auth_app.core.config import settings
from auth_app.errors.services.oauth import ProviderExchangeError, ProviderInfoError, ProviderRequiresRedirectUrl

from .base import OAuthProviderInterface


class OAuthYandexProvider(OAuthProviderInterface):
    def get_oauth_url(self, redirect_url: str | None = None) -> str:
        oauth_url = "https://oauth.yandex.ru/authorize"
        params = {
            "client_id": settings.oauth.yandex.client_id,
            "redirect_uri": redirect_url,
            "response_type": "code",
            "scope": "login:email",
        }
        url = f"{oauth_url}?{urlencode(params)}"
        return url

    async def exchange_token(self, code: str, redirect_url: str | None = None) -> str:
        if not redirect_url:
            raise ProviderRequiresRedirectUrl

        exchange_url = "https://oauth.yandex.ru/token"
        body = {
            "client_id": settings.oauth.yandex.client_id,
            "client_secret": settings.oauth.yandex.client_secret,
            "code": code,
            "grant_type": "authorization_code",
        }
        async with httpx.AsyncClient() as client:
            response = await client.post(exchange_url, data=body)

        access_token = response.json().get("access_token")
        if not access_token:
            raise ProviderExchangeError
        return access_token

    async def get_user_info(self, access_token: str) -> dict:
        """Return user info.

        Returns
        -------
        {
            "login": "",
            "old_social_login": "",
            "default_email": "",
            "id": "",
            "client_id": "",
            "emails": [
                "",
                ""
            ],
            "psuid": ""
        }
        """
        get_user_info_url = "https://login.yandex.ru/info"
        headers = {"Authorization": f"OAuth {access_token}"}
        async with httpx.AsyncClient() as client:
            response = await client.get(get_user_info_url, headers=headers)

        if not response.status_code == HTTPStatus.OK:
            raise ProviderInfoError

        info = response.json()
        return info
