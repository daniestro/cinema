import uuid
from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, Path, Response

from auth_app.api.pagination import Pagination
from auth_app.api.role_check import RequireRole
from auth_app.models.dto import RoleCreateSchema, RoleUpdateSchema
from auth_app.models.dto.role import RoleInfoSchema
from auth_app.services.role_service import RoleService, get_role_service

router = APIRouter(dependencies=[Depends(RequireRole({"admin", "service"}))])


@router.post(
    "/",
    status_code=HTTPStatus.OK,
    tags=["Роль"],
    description="Создание новой роли",
    summary="Создать роль",
    response_model=RoleInfoSchema,
)
async def create_role(
    role: RoleCreateSchema = Depends(),
    role_service: RoleService = Depends(get_role_service),
) -> RoleInfoSchema:
    role_ = await role_service.create(name=role.name, description=role.description)
    return RoleInfoSchema(**role_.dict())


@router.get(
    "/",
    status_code=HTTPStatus.OK,
    tags=["Роль"],
    description="Получение списка ролей",
    summary="Получить список ролей",
    response_model=list[RoleInfoSchema],
)
async def get_role_list(
    pagination: Pagination = Depends(),
    role_service: RoleService = Depends(get_role_service),
) -> list[RoleInfoSchema]:
    result = await role_service.get_list(pagination.limit, pagination.offset)
    return [RoleInfoSchema(**role.dict()) for role in result]


@router.get(
    "/{role_id}/",
    status_code=HTTPStatus.OK,
    tags=["Роль"],
    description="Получение роли по идентификатору",
    summary="Получить роль по идентификатору",
    response_model=RoleInfoSchema,
)
async def get_role_by_id(
    role_id: Annotated[uuid.UUID, Path(title="идентификатор роли", description="Идентификатор роли")],
    role_service: RoleService = Depends(get_role_service),
) -> RoleInfoSchema:
    role = await role_service.get(role_id)
    return RoleInfoSchema(**role.dict())


@router.put(
    "/{role_id}/",
    status_code=HTTPStatus.OK,
    tags=["Роль"],
    description="Обновление роли",
    summary="Обновить роль",
    response_model=RoleInfoSchema,
)
async def update_role(
    role_id: Annotated[uuid.UUID, Path(title="идентификатор роли", description="Идентификатор роли")],
    role: RoleUpdateSchema = Depends(),
    role_service: RoleService = Depends(get_role_service),
):
    role_ = await role_service.update(role_id, role.name, role.description)
    return RoleInfoSchema(**role_.dict())


@router.delete(
    "/{role_id}/",
    status_code=HTTPStatus.OK,
    tags=["Роль"],
    description="Удаление роли",
    summary="Удалить роль",
    response_class=Response,
)
async def delete_role(
    role_id: Annotated[uuid.UUID, Path(title="идентификатор роли", description="Идентификатор роли")],
    role_service: RoleService = Depends(get_role_service),
):
    await role_service.delete(role_id)
    return Response(status_code=HTTPStatus.OK)
