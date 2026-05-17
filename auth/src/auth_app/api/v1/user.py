import uuid
from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, Path, Response
from pydantic import EmailStr

from auth_app.api.pagination import Pagination
from auth_app.api.role_check import RequireRole
from auth_app.models.dto import UserInfoSchema
from auth_app.models.dto.user import UserSignUpSchema
from auth_app.services.user_service import UserService, get_user_service

router = APIRouter(dependencies=[Depends(RequireRole({"admin", "service"}))])


@router.post(
    "/",
    status_code=HTTPStatus.CREATED,
    tags=["Пользователь"],
    description="Создание пользователя",
    summary="Создание пользователя",
    response_model=UserInfoSchema,
)
async def create_user(
    user_sign_up: UserSignUpSchema,
    user_service: UserService = Depends(get_user_service),
) -> UserInfoSchema:
    result = await user_service.create(user_sign_up.email, user_sign_up.password)

    return UserInfoSchema(**result.dict())


@router.get(
    "/",
    status_code=HTTPStatus.OK,
    tags=["Пользователь"],
    description="Получение списка пользователей",
    summary="Получить список пользователей",
    response_model=list[UserInfoSchema],
)
async def get_user_list(
    pagination: Pagination = Depends(),
    user_service: UserService = Depends(get_user_service),
) -> list[UserInfoSchema]:
    result = await user_service.get_list(pagination.limit, pagination.offset)

    return [UserInfoSchema(**user.dict()) for user in result]


@router.get(
    "/{user_id}/",
    status_code=HTTPStatus.OK,
    tags=["Пользователь"],
    description="Получение информации по пользователю",
    summary="Получить информацию по пользователю",
    response_model=UserInfoSchema,
)
async def get_user(
    user_id: Annotated[
        uuid.UUID,
        Path(description="Идентификатор пользователя"),
    ],
    user_service: UserService = Depends(get_user_service),
) -> UserInfoSchema:
    result = await user_service.get(user_id)

    return UserInfoSchema(**result.dict())


@router.patch(
    "/{user_id}/",
    status_code=HTTPStatus.OK,
    tags=["Пользователь"],
    description="Изменение данных пользователя",
    summary="Изменение данных пользователя",
    response_model=UserInfoSchema,
)
async def update_user(
    user_id: Annotated[
        uuid.UUID,
        Path(
            title="идентификатор пользователя",
            description="Идентификатор пользователя",
        ),
    ],
    email: EmailStr | None = None,
    password: str | None = None,
    user_service: UserService = Depends(get_user_service),
) -> UserInfoSchema:
    result = await user_service.update(user_id, email, password)

    return UserInfoSchema(**result.dict())


@router.delete(
    "/{user_id}/",
    status_code=HTTPStatus.OK,
    tags=["Пользователь"],
    description="Удаление пользователя",
    summary="Удаление пользователя",
    response_class=Response,
)
async def delete_user(
    user_id: Annotated[
        uuid.UUID,
        Path(
            title="идентификатор пользователя",
            description="Идентификатор пользователя",
        ),
    ],
    user_service: UserService = Depends(get_user_service),
):
    await user_service.delete(user_id)
    return Response(status_code=HTTPStatus.OK)
