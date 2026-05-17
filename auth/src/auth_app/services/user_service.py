import logging
import uuid
from logging import Logger

from fastapi import Depends
from pydantic import EmailStr

from auth_app.external.user_repository import (
    UserRepository,
    get_user_repository,
)
from auth_app.models.domain.user import User

from .hash_service import HashService, get_hash_service


class UserService:
    def __init__(
        self,
        user_repository: UserRepository,
        hash_service: HashService,
        logger: Logger,
    ) -> None:
        self.user_repository = user_repository
        self.hash_service = hash_service
        self.logger = logger

    async def get(self, user_id: uuid.UUID) -> User:
        """Get user by id.

        Raises
        ------
            UserNotFound
        """
        user = await self.user_repository.get(user_id)
        return user

    async def get_by_email(self, user_email: EmailStr) -> User:
        """Get user by email.

        Raises
        ------
            UserNotFound
        """
        user = await self.user_repository.get_by_email(user_email)
        return user

    async def get_list(self, limit: int, offset: int) -> list[User]:
        """Get user list."""
        user = await self.user_repository.get_list(limit, offset)
        return user

    async def create(self, email: EmailStr, password: str) -> User:
        """Create new user.

        Raises
        ------
            AlreadyTakenEmail
        """
        hashed_password = self.hash_service.hash(password)

        result = await self.user_repository.create(email, hashed_password)

        self.logger.info(f"Successfully sign up user: {email}")
        return result

    async def update(
        self,
        user_id: uuid.UUID,
        new_email: EmailStr | None = None,
        new_password: str | None = None,
    ) -> User:
        """Update user.

        Raises
        ------
            UserNotFound
        """
        if new_password:
            hashed_password = self.hash_service.hash(new_password)
        else:
            hashed_password = None

        user = await self.user_repository.update(user_id, new_email, hashed_password)

        self.logger.info(f"Successfully updated user: {user_id}")
        return user

    async def delete(
        self,
        user_id: uuid.UUID,
    ) -> bool:
        """Delete user.

        Raises
        ------
            UserNotFound
        """
        result = await self.user_repository.delete(user_id)

        self.logger.info(f"Successfully deleted user: {user_id}")
        return result


def get_user_service(
    user_repository: UserRepository = Depends(get_user_repository),
    hash_service: HashService = Depends(get_hash_service),
) -> UserService:
    logger = logging.getLogger(__name__)
    return UserService(
        user_repository=user_repository,
        hash_service=hash_service,
        logger=logger,
    )
