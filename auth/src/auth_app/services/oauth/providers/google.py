from http import HTTPStatus
from urllib.parse import urlencode

import httpx

from auth_app.core.config import settings
from auth_app.errors.services.oauth import ProviderExchangeError, ProviderInfoError, ProviderRequiresRedirectUrl

from .base import OAuthProviderInterface


class OAuthGoogleProvider(OAuthProviderInterface):
    def get_oauth_url(self, redirect_url: str | None = None) -> str:
        if not redirect_url:
            raise ProviderRequiresRedirectUrl

        oauth_url = "https://accounts.google.com/o/oauth2/v2/auth"
        params = {
            "client_id": settings.oauth.google.client_id,
            "redirect_uri": redirect_url,
            "response_type": "code",
            "scope": "https://www.googleapis.com/auth/userinfo.email",
            "access_type": "offline",
        }
        url = f"{oauth_url}?{urlencode(params)}"
        return url

    async def exchange_token(self, code: str, redirect_url: str | None = None) -> str:
        if not redirect_url:
            raise ProviderRequiresRedirectUrl

        exchange_url = "https://oauth2.googleapis.com/token"
        params = {
            "client_id": settings.oauth.google.client_id,
            "client_secret": settings.oauth.google.client_secret,
            "code": code,
            "grant_type": "authorization_code",
            "redirect_uri": redirect_url,
        }
        url = f"{exchange_url}?{urlencode(params)}"
        async with httpx.AsyncClient() as client:
            response = await client.post(url)
        access_token = response.json().get("access_token")
        if not access_token:
            raise ProviderExchangeError

        return access_token

    async def get_user_info(self, access_token: str) -> dict:
        """Return user info.

        Returns
        -------
            {
                "picture": "",
                "verified_email": true,
                "id": "",
                "email": ""
            }
        """
        get_user_info_url = "https://www.googleapis.com/oauth2/v2/userinfo"
        headers = {"Authorization": f"Bearer {access_token}"}
        async with httpx.AsyncClient() as client:
            response = await client.get(get_user_info_url, headers=headers)

        if not response.status_code == HTTPStatus.OK:
            raise ProviderInfoError

        info = response.json()
        return info
