from logging import Logger

from auth_app.external.login_history_repository import LoginRecordRepository
from auth_app.external.socialnet_repository import SocialnetRepository
from auth_app.services.jwt_service import JWTService
from auth_app.services.user_service import UserService

from .interface import OAuthServiceInterface


class OAuthBaseService(OAuthServiceInterface):
    def __init__(
        self,
        user_service: UserService,
        login_history_repository: LoginRecordRepository,
        socialnet_repository: SocialnetRepository,
        jwt_service: JWTService,
        logger: Logger,
    ) -> None:
        self.user_service = user_service
        self.jwt_service = jwt_service
        self.login_history_repository = login_history_repository
        self.logger = logger
        self.socalnet_repository = socialnet_repository
