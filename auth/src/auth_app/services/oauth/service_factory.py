import logging
from typing import Callable

from fastapi import Depends

from auth_app.errors.services.oauth import ProviderNotFoundError
from auth_app.external.login_history_repository import (
    LoginRecordRepository,
    get_login_record_repository,
)
from auth_app.external.socialnet_repository import (
    SocialnetRepository,
    get_socialnet_repository,
)
from auth_app.services.jwt_service import JWTService, get_jwt_service
from auth_app.services.user_service import UserService, get_user_service

from .enums import OauthProvider
from .services import OAuthBaseService, OAuthGoogleService, OAuthYandexService

services: dict[str, type[OAuthBaseService]] = {
    OauthProvider.GOOGLE: OAuthGoogleService,  # type: ignore
    OauthProvider.YANDEX: OAuthYandexService,
}


def get_oauth_service_factory(
    user_service: UserService = Depends(get_user_service),
    jwt_service: JWTService = Depends(get_jwt_service),
    login_history_repository: LoginRecordRepository = Depends(get_login_record_repository),
    socialnet_repository: SocialnetRepository = Depends(get_socialnet_repository),
) -> Callable[[str], OAuthBaseService]:
    def _oauth_factory(name: str) -> OAuthBaseService:
        logger = logging.getLogger(__name__)
        service = services.get(name)
        if not service:
            raise ProviderNotFoundError

        return service(
            user_service=user_service,
            jwt_service=jwt_service,
            login_history_repository=login_history_repository,
            logger=logger,
            socialnet_repository=socialnet_repository,
        )

    return _oauth_factory
