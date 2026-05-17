from http import HTTPStatus

from fastapi import APIRouter, Depends, Request, Response

from auth_app.api.pagination import Pagination
from auth_app.api.role_check import get_current_user
from auth_app.models.domain.user import User
from auth_app.models.dto import LoginRecordSchema, UserSignInSchema, UserSignUpSchema
from auth_app.models.dto.user import UserInfoSchema
from auth_app.services.auth_service import AuthService, get_auth_service

router = APIRouter()


@router.post(
    "/signup/",
    status_code=HTTPStatus.CREATED,
    tags=["auth"],
    description="Регистрация нового пользователя",
    summary="Регистрация нового пользователя",
    response_class=Response,
)
async def sign_up(
    user_sign_up: UserSignUpSchema,
    auth_service: AuthService = Depends(get_auth_service),
):
    await auth_service.sign_up(user_sign_up.email, user_sign_up.password)
    return Response(status_code=HTTPStatus.CREATED)


@router.post(
    "/signin/",
    status_code=HTTPStatus.OK,
    tags=["auth"],
    description="Логин пользователя",
    summary="Логин пользователя",
    response_class=Response,
)
async def sign_in(
    user_sign_in: UserSignInSchema,
    request: Request,
    auth_service: AuthService = Depends(get_auth_service),
) -> Response:
    response = Response(status_code=HTTPStatus.OK)
    ip = request.client.host
    user_agent = request.headers.get("User-Agent")
    tokens = await auth_service.sign_in(
        email=user_sign_in.email,
        password=user_sign_in.password,
        user_agent=user_agent,
        ip=ip,
    )

    response.set_cookie("access_token", tokens.access, httponly=True, secure=True)
    response.set_cookie("refresh_token", tokens.refresh, httponly=True, secure=True)

    return response


@router.post(
    "/logout/",
    status_code=HTTPStatus.OK,
    tags=["auth"],
    description="Выйти из аккаунта",
    summary="Выйти из аккаунта",
    response_class=Response,
    dependencies=[Depends(get_current_user)],
)
async def logout(
    request: Request,
    auth_service: AuthService = Depends(get_auth_service),
):
    access_token = request.cookies.get("access_token")
    refresh_token = request.cookies.get("refresh_token")
    await auth_service.logout(access_token, refresh_token)
    return Response(status_code=HTTPStatus.OK)


@router.post(
    "/refresh/",
    status_code=HTTPStatus.OK,
    tags=["auth"],
    description="Выпуск нового access-токена",
    summary="Выпуск нового access-токена",
    response_class=Response,
)
async def refresh(
    request: Request,
    auth_service: AuthService = Depends(get_auth_service),
) -> Response:
    response = Response(status_code=HTTPStatus.OK)
    refresh_token = request.cookies.get("refresh_token")
    tokens = await auth_service.refresh(refresh_token)

    response.set_cookie("access_token", tokens.access, httponly=True, secure=True)
    response.set_cookie("refresh_token", tokens.refresh, httponly=True, secure=True)

    return response


@router.get(
    "/login_history/",
    status_code=HTTPStatus.OK,
    tags=["auth"],
    description="Просмотр истории входов",
    summary="Просмотр истории входов",
    response_model=list[LoginRecordSchema],
    dependencies=[Depends(get_current_user)],
)
async def get_login_history(
    request: Request,
    pagination: Pagination = Depends(),
    auth_service: AuthService = Depends(get_auth_service),
) -> list[LoginRecordSchema]:
    access_token = request.cookies.get("access_token")
    records = await auth_service.get_login_history(
        access_token=access_token,
        limit=pagination.limit,
        offset=pagination.offset,
    )

    return [LoginRecordSchema(**record.dict()) for record in records]


@router.get(
    "/me/",
    status_code=HTTPStatus.OK,
    tags=["auth"],
    description="Получить информацию о себе",
    dependencies=[Depends(get_current_user)],
    response_model=UserInfoSchema,
)
async def me(
    user: User = Depends(get_current_user),
) -> UserInfoSchema:
    return UserInfoSchema(**user.dict())
