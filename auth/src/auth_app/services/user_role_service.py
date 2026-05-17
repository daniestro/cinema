import logging
import uuid
from logging import Logger

from fastapi import Depends

from auth_app.errors.external import UserAlreadyHasRole, UserDoesNotHaveRole
from auth_app.external import UserRepository, get_user_repository
from auth_app.external.role_repository import RoleRepository, get_role_repository
from auth_app.external.user_role_repository import UserRoleRepository, get_user_role_repository
from auth_app.models.domain import Role
from auth_app.models.domain.user import User


class UserRoleService:
    def __init__(
        self,
        user_repository: UserRepository,
        role_repository: RoleRepository,
        user_role_repository: UserRoleRepository,
        logger: Logger,
    ):
        self.user_repository = user_repository
        self.role_repository = role_repository
        self.user_role_repository = user_role_repository
        self.logger = logger

    async def get_user_roles(self, user_id: uuid.UUID) -> list[Role]:
        role_list = await self.user_role_repository.get_user_roles(user_id)
        return role_list

    async def get_users_by_role(
        self,
        role_name: str,
        offset: int,
        limit: int,
    ) -> list[User]:
        user_list = await self.user_role_repository.get_users_by_role(
            role_name=role_name,
            limit=limit,
            offset=offset,
        )
        print(user_list)
        return user_list

    async def set_user_role(
        self,
        user_id: uuid.UUID,
        role_id: uuid.UUID,
    ):
        user = await self.user_repository.get(user_id)
        role = await self.role_repository.get(role_id)
        role_list = await self.user_role_repository.get_user_roles(user.id)
        if role in role_list:
            raise UserAlreadyHasRole
        await self.user_role_repository.set_user_role(user, role)
        self.logger.info('Successfully set role_id="%s" to user_id=%s', role.id, user.id)

    async def delete_user_role(
        self,
        user_id: uuid.UUID,
        role_id: uuid.UUID,
    ):
        user = await self.user_repository.get(user_id)
        role = await self.role_repository.get(role_id)
        role_list = await self.user_role_repository.get_user_roles(user.id)
        if role not in role_list:
            raise UserDoesNotHaveRole
        await self.user_role_repository.delete_user_role(user, role)
        self.logger.info('Successfully remove role_id="%s" from user_id=%s', role.id, user.id)


def get_user_role_service(
    user_repository: UserRepository = Depends(get_user_repository),
    role_repository: RoleRepository = Depends(get_role_repository),
    user_role_repository: UserRoleRepository = Depends(get_user_role_repository),
) -> UserRoleService:
    logger = logging.getLogger(__name__)
    return UserRoleService(
        user_repository=user_repository,
        role_repository=role_repository,
        user_role_repository=user_role_repository,
        logger=logger,
    )
