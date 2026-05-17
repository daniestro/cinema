import logging
import uuid
from logging import Logger

import jwt
from email_validator import EmailNotValidError
from fastapi import Depends
from pydantic import EmailStr, validate_email

from auth_app.errors.external import InvalidEmail, UserNotFound
from auth_app.errors.services import (
    InvalidEmailOrPassword,
    WeakPassword,
)
from auth_app.external.login_history_repository import LoginRecordRepository, get_login_record_repository
from auth_app.models.domain.login_record import LoginRecord
from auth_app.services.token_blacklist_service import TokenBlacklistService, get_token_blacklist_service
from auth_app.services.user_service import UserService, get_user_service

from .hash_service import HashService, get_hash_service
from .jwt_service import JWTService, get_jwt_service
from .misc import JWTPair, generate_jwt, validate_password


class AuthService:
    def __init__(
        self,
        user_service: UserService,
        login_history_repository: LoginRecordRepository,
        jwt_service: JWTService,
        hash_service: HashService,
        token_blacklist_service: TokenBlacklistService,
        logger: Logger,
    ) -> None:
        self.user_service = user_service
        self.jwt_service = jwt_service
        self.hash_service = hash_service
        self.login_history_repository = login_history_repository
        self.token_blacklist_service = token_blacklist_service
        self.logger = logger

    async def sign_up(self, email: EmailStr, password: str) -> bool:
        """Register new user.

        Raises
        ------
            WeakPassword
            InvalidEmail
            AlreadyTakenEmail
        """
        if not validate_password(password):
            raise WeakPassword

        try:
            validate_email(email)
        except EmailNotValidError:
            raise InvalidEmail

        await self.user_service.create(email, password)

        self.logger.info("Successfully sign up user with email=%s", email)
        return True

    async def sign_in(
        self,
        email: EmailStr,
        password: str,
        user_agent: str,
        ip: str,
    ) -> JWTPair:
        """Sign in user.

        Raises
        ------
            InvalidEmailOrPassword
        """
        try:
            user = await self.user_service.get_by_email(email)
        except UserNotFound:
            raise InvalidEmailOrPassword

        role_names = [role.name for role in user.roles]

        if not self.hash_service.verify(password, user.hashed_password):
            raise InvalidEmailOrPassword

        jwt = generate_jwt(self.jwt_service, str(user.id), user.email, role_names)

        await self.login_history_repository.create_record(
            user_id=user.id,
            user_agent=user_agent,
            ip=ip,
            access_jti=jwt.jti.access,
            refresh_jti=jwt.jti.refresh,
        )

        self.logger.info("Successfully sign in user with email=%s", email)
        return jwt.tokens

    async def update(
        self,
        old_email: EmailStr,
        old_password: str,
        new_email: EmailStr | None = None,
        new_password: str | None = None,
    ) -> bool:
        """Update user.

        Raises
        ------
            UserNotFound
            InvalidPassword
        """
        try:
            user = await self.user_service.get_by_email(old_email)
        except UserNotFound:
            raise InvalidEmailOrPassword

        if not self.hash_service.verify(old_password, user.hashed_password):
            raise InvalidEmailOrPassword

        await self.user_service.update(user.id, new_email, new_password)

        self.logger.info("Successfully updated user with id=%s", old_email)
        return True

    async def logout(self, access_token: str, refresh_token: str) -> bool:
        """Put access and refresh token to blacklist."""
        await self.token_blacklist_service.put(access_token)
        await self.token_blacklist_service.put(refresh_token)
        return True

    async def refresh(self, refresh_token: str) -> JWTPair:
        """Refresh access token.

        Puts previous refresh token to black list.
        """
        await self._check_blacklist(refresh_token)
        await self.token_blacklist_service.put(refresh_token)
        access_token = self.jwt_service.refresh_token(refresh_token)

        content = self.jwt_service.decode_access_token(access_token)
        refresh_token = self.jwt_service.encode_refresh_token(
            content["sub"],
            content["email"],
            content["roles"],
        )

        return JWTPair(access_token, refresh_token)

    async def get_login_history(
        self,
        access_token: str,
        limit: int,
        offset: int,
    ) -> list[LoginRecord]:
        """Get user account login history.

        Raises
        ------
            UserNotFound
        """
        await self._check_blacklist(access_token)
        user_id = self.jwt_service.decode_access_token(access_token)["sub"]

        history = await self.login_history_repository.get_login_records(
            user_id=uuid.UUID(user_id),
            limit=limit,
            offset=offset,
        )
        self.logger.info("Got history for user with id=%s", user_id)
        return history

    async def _check_blacklist(self, token: str) -> None:
        if await self.token_blacklist_service.get(token):
            raise jwt.InvalidTokenError


def get_auth_service(
    user_service: UserService = Depends(get_user_service),
    jwt_service: JWTService = Depends(get_jwt_service),
    login_history_repository: LoginRecordRepository = Depends(get_login_record_repository),
    token_blacklist_service: TokenBlacklistService = Depends(get_token_blacklist_service),
    hash_service: HashService = Depends(get_hash_service),
) -> AuthService:
    logger = logging.getLogger(__name__)
    return AuthService(
        user_service=user_service,
        jwt_service=jwt_service,
        login_history_repository=login_history_repository,
        hash_service=hash_service,
        token_blacklist_service=token_blacklist_service,
        logger=logger,
    )
