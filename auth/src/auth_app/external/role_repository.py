import logging
import uuid
from logging import Logger

from fastapi import Depends
from sqlalchemy.exc import IntegrityError, NoResultFound
from sqlmodel import delete, select
from sqlmodel.ext.asyncio.session import AsyncSession

from auth_app.db.sqlalchemy import get_async_session
from auth_app.errors.external import RoleAlreadyExists, RoleNotFound
from auth_app.models.domain import Role


class RoleRepository:
    def __init__(self, session: AsyncSession, logger: Logger) -> None:
        self.session = session
        self.logger = logger

    async def create(
        self,
        name: str,
        description: str,
    ) -> Role:
        """Create a role."""
        role = Role(name=name, description=description)
        try:
            self.session.add(role)
            await self.session.commit()
            await self.session.refresh(role)
            self.logger.info("Created role with id=%s", role.id)
        except IntegrityError:
            raise RoleAlreadyExists(name)
        return role

    async def get(self, role_id: uuid.UUID) -> Role:
        """Get a role.

        Raises
        ------
            RoleNotFound: role does not exist
        """
        result = await self.session.execute(select(Role).where(Role.id == role_id))
        try:
            return result.scalar_one()
        except NoResultFound:
            raise RoleNotFound(role_id)

    async def get_by_name(self, role_name: str) -> Role:
        """Get a role.

        Raises
        ------
            RoleNotFound: role does not exist
        """
        result = await self.session.execute(select(Role).where(Role.name == role_name))
        try:
            return result.scalar_one()
        except NoResultFound:
            raise RoleNotFound(role_name)

    async def get_list(self, limit: int, offset: int) -> list[Role]:
        """Get role list."""
        result = await self.session.execute(
            select(Role)  #
            .order_by(Role.name.asc())  #
            .limit(limit)  #
            .offset(offset),  #
        )
        return result.scalars().all()

    async def delete(self, role_id: uuid.UUID) -> bool:
        """Delete a role.

        Raises
        ------
            RoleNotFound: role does not exist
        """
        result = await self.session.execute(delete(Role).where(Role.id == role_id).returning(Role.id))
        try:
            deleted_id = result.scalar_one()
        except NoResultFound:
            raise RoleNotFound(role_id)

        await self.session.commit()
        self.logger.info("Deleted role with id=%s", role_id)
        return True if deleted_id else False

    async def update(
        self,
        role_id: uuid.UUID,
        name: str | None = None,
        description: str | None = None,
    ) -> Role:
        """Update already existing role.

        Raises
        ------
            RoleNotFound: role does not exist
        """
        statement = select(Role).where(Role.id == role_id)
        result = await self.session.execute(statement)
        try:
            role = result.scalar_one()
        except NoResultFound:
            raise RoleNotFound(role_id)
        if name:
            role.name = name
        if description:
            role.description = description

        self.session.add(role)
        await self.session.commit()
        await self.session.refresh(role)
        self.logger.info("Updated role with id=%s", role.id)
        return role


async def get_role_repository(session: AsyncSession = Depends(get_async_session)) -> RoleRepository:
    logger = logging.getLogger(__name__)
    return RoleRepository(session=session, logger=logger)
