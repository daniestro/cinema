import logging
import uuid
from logging import Logger

from fastapi import Depends
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from auth_app.db.sqlalchemy import get_async_session
from auth_app.models.domain import Role, User


class UserRoleRepository:
    def __init__(self, session: AsyncSession, logger: Logger) -> None:
        self.session = session
        self.logger = logger

    async def get_user_roles(self, user_id: uuid.UUID) -> list[Role]:
        result = await self.session.execute(select(Role).where(Role.users.any(User.id == user_id)))
        return result.scalars().all()

    async def get_users_by_role(
        self,
        role_name: str,
        limit: int,
        offset: int,
    ) -> list[User]:
        result = await self.session.execute(
            select(User).where(User.roles.any(Role.name == role_name)).limit(limit).offset(offset),
        )
        return result.scalars().all()

    async def set_user_role(self, user: User, role: Role) -> User:
        """Set a role to a user."""
        user.roles.append(role)
        self.session.add(user)
        await self.session.commit()
        return user

    async def delete_user_role(self, user: User, role: Role) -> User:
        """Remove user role."""
        user.roles.remove(role)
        self.session.add(user)
        await self.session.commit()
        return user


async def get_user_role_repository(
    session: AsyncSession = Depends(get_async_session),
) -> UserRoleRepository:
    logger = logging.getLogger(__name__)
    return UserRoleRepository(session=session, logger=logger)
