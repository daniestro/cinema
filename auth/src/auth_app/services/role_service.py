import logging
import uuid
from logging import Logger

from fastapi import Depends

from auth_app.external.role_repository import (
    RoleRepository,
    get_role_repository,
)
from auth_app.models.domain import Role


class RoleService:
    def __init__(
        self,
        role_repository: RoleRepository,
        logger: Logger,
    ):
        self.role_repository = role_repository
        self.logger = logger

    async def create(self, name: str, description: str) -> Role:
        role = await self.role_repository.create(name, description)
        self.logger.info("Successfully create role with id=%s", role.id)
        return role

    async def get(self, role_id: uuid.UUID) -> Role:
        role = await self.role_repository.get(role_id)
        self.logger.info("Successfully get role with id=%s", role.id)
        return role

    async def get_by_name(self, role_name: str) -> Role:
        role = await self.role_repository.get_by_name(role_name)
        self.logger.info("Successfully get role with name=%s", role.id)
        return role

    async def get_list(self, limit: int, offset: int) -> list[Role]:
        role_list = await self.role_repository.get_list(limit, offset)
        self.logger.info("Successfully get role list")
        return role_list

    async def delete(self, role_id: uuid.UUID):
        await self.role_repository.delete(role_id)
        self.logger.info("Successfully delete role with id=%s", role_id)

    async def update(self, role_id: uuid.UUID, name: str, description: str) -> Role:
        role = await self.role_repository.update(role_id, name, description)
        self.logger.info("Successfully update role with id=%s", role_id)
        return role


def get_role_service(
    role_repository: RoleRepository = Depends(get_role_repository),
) -> RoleService:
    logger = logging.getLogger(__name__)
    return RoleService(role_repository=role_repository, logger=logger)
