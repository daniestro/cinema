import logging
import uuid
from logging import Logger

from fastapi import Depends
from pydantic import EmailStr
from sqlalchemy.exc import IntegrityError, NoResultFound
from sqlalchemy.orm import selectinload
from sqlmodel import delete, select
from sqlmodel.ext.asyncio.session import AsyncSession

from auth_app.errors.external import AlreadyTakenEmail, UserNotFound

from ..db.sqlalchemy import get_async_session
from ..models.domain.user import User


class UserRepository:
    def __init__(self, session: AsyncSession, logger: Logger) -> None:
        self.session = session
        self.logger = logger

    async def create(
        self,
        email: str,
        hashed_password: str,
    ) -> User:
        """Create user.

        Raises
        ------
            AlreadyTakenEmail
        """
        user = User(email=email, hashed_password=hashed_password)

        try:
            self.session.add(user)
            await self.session.commit()
            await self.session.refresh(user)
            self.logger.info(f"Created user {user.id}")
        except IntegrityError:
            raise AlreadyTakenEmail(email)
        return user

    async def get(self, user_id: uuid.UUID) -> User:
        """Get user.

        Raises
        ------
            UserNotFound
        """
        result = await self.session.execute(select(User).where(User.id == user_id).options(selectinload(User.roles)))
        try:
            return result.scalar_one()
        except NoResultFound:
            raise UserNotFound(user_id)

    async def get_by_email(self, user_email: EmailStr) -> User:
        """Get user by email.

        Raises
        ------
            UserNotFound
        """
        result = await self.session.execute(
            select(User)  #
            .where(User.email == user_email)  #
            .options(selectinload(User.roles)),
        )
        try:
            return result.scalar_one()
        except NoResultFound:
            raise UserNotFound(user_email)

    async def get_list(self, limit: int, offset: int) -> list[User]:
        """Get user list."""
        result = await self.session.execute(select(User).limit(limit).offset(offset))
        return result.scalars().all()

    async def delete(self, user_id: uuid.UUID) -> bool:
        """Delete user.

        Raises
        ------
            UserNotFound
        """
        result = await self.session.execute(delete(User).where(User.id == user_id).returning(User.id))
        try:
            deleted_id = result.scalar_one()
        except NoResultFound:
            raise UserNotFound(user_id)

        await self.session.commit()
        self.logger.info(f"Deleted user {user_id}")
        return True if deleted_id else False

    async def update(
        self,
        user_id: uuid.UUID,
        email: str | None = None,
        hashed_password: str | None = None,
    ) -> User:
        """Update already existing user.

        Raises
        ------
            UserNotFound
        """
        statement = select(User).where(User.id == user_id)
        result = await self.session.execute(statement)
        try:
            user = result.scalar_one()
        except NoResultFound:
            raise UserNotFound(user_id)

        if email:
            user.email = email
        elif hashed_password:
            user.hashed_password = hashed_password

        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)
        self.logger.info(f"Updated user {user.id}")

        return user


def get_user_repository(session: AsyncSession = Depends(get_async_session)) -> UserRepository:
    logger = logging.getLogger(__name__)
    return UserRepository(session=session, logger=logger)
