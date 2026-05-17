import uuid
from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, Path

from auth_app.api.pagination import Pagination
from auth_app.api.role_check import RequireRole
from auth_app.models.dto import UserRoleSchema
from auth_app.models.dto.role import RoleInfoSchema
from auth_app.models.dto.user import UserInfoSchema
from auth_app.services.user_role_service import UserRoleService, get_user_role_service

router = APIRouter(dependencies=[Depends(RequireRole({"admin", "service"}))])


@router.get(
    "/user/{user_id}/",
    status_code=HTTPStatus.OK,
    tags=["Роль-Пользователь"],
    description="Получение ролей пользователя",
    summary="Получить роли пользователя",
    response_model=list[RoleInfoSchema],
)
async def get_user_roles(
    user_id: Annotated[
        uuid.UUID,
        Path(title="идентификатор пользователя", description="Идентификатор пользователя"),
    ],
    user_role_service: UserRoleService = Depends(get_user_role_service),
) -> list[RoleInfoSchema]:
    role_list = await user_role_service.get_user_roles(user_id)
    return [RoleInfoSchema(**role_.model_dump()) for role_ in role_list]


@router.get(
    "/{role_name}/user",
    status_code=HTTPStatus.OK,
    tags=["Роль-Пользователь"],
    description="Получение списка пользователей по роли",
    summary="Получение списка пользователей по роли",
    response_model=list[UserInfoSchema],
)
async def get_user_by_role_name(
    role_name: str = Path(description="Slug роли"),
    pagination: Pagination = Depends(),
    user_role_service: UserRoleService = Depends(get_user_role_service),
) -> list[UserInfoSchema]:
    result = await user_role_service.get_users_by_role(
        role_name=role_name,
        limit=pagination.limit,
        offset=pagination.offset,
    )
    return [UserInfoSchema(**user.model_dump()) for user in result]


@router.post(
    "/user/",
    status_code=HTTPStatus.OK,
    tags=["Роль-Пользователь"],
    description="Назначение роли пользователю",
    summary="Назначить роль пользователю",
    response_model=list[RoleInfoSchema],
)
async def set_user_role(
    user_role: UserRoleSchema,
    user_role_service: UserRoleService = Depends(get_user_role_service),
) -> list[RoleInfoSchema]:
    await user_role_service.set_user_role(user_role.user_id, user_role.role_id)
    user_roles = await user_role_service.get_user_roles(user_role.user_id)

    return [RoleInfoSchema(**role.dict()) for role in user_roles]


@router.post(
    "/user/remove/",
    status_code=HTTPStatus.OK,
    tags=["Роль-Пользователь"],
    description="Удаление роли пользователю",
    summary="Удалить роль у пользователя",
    response_model=list[RoleInfoSchema],
)
async def delete_user_role(
    user_role: UserRoleSchema,
    user_role_service: UserRoleService = Depends(get_user_role_service),
):
    await user_role_service.delete_user_role(user_role.user_id, user_role.role_id)
    user_roles = await user_role_service.get_user_roles(user_role.user_id)
    return [RoleInfoSchema(**role.dict()) for role in user_roles]
