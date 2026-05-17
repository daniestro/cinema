from auth_app.errors.services.oauth import ProviderNotFoundError

from .enums import OauthProvider
from .providers import (
    OAuthGoogleProvider,
    OAuthProviderInterface,
    OAuthYandexProvider,
)

provider_names: dict[str, OAuthProviderInterface] = {
    OauthProvider.GOOGLE: OAuthGoogleProvider(),  # type: ignore
    OauthProvider.YANDEX: OAuthYandexProvider(),
}


def get_oauth_provider(name: str) -> OAuthProviderInterface:
    provider = provider_names.get(name)
    if not provider:
        raise ProviderNotFoundError
    return provider
