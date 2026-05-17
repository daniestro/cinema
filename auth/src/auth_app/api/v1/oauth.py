from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, Path, Query, Request, Response

from auth_app.api.role_check import get_current_user
from auth_app.external.socialnet_repository import SocialnetRepository, get_socialnet_repository
from auth_app.external.user_socialnet_repository import UserSocialnetRepository, get_user_socialnet_repository
from auth_app.models.domain.user import User
from auth_app.models.dto.socialnet import SocialNetSchema
from auth_app.services.oauth import get_oauth_provider, get_oauth_service_factory
from auth_app.services.oauth.enums import OauthProvider
from auth_app.services.oauth.services import OAuthServiceInterface

router = APIRouter()


@router.get(
    "/{provider_name}/auth",
    status_code=HTTPStatus.OK,
    tags=["oauth"],
    description="OAuth",
    summary="OAuth",
)
async def oauth_auth(
    request: Request,
    provider_name: Annotated[str, Path(enum=list(OauthProvider))],  # type: ignore
) -> str:
    provider = get_oauth_provider(provider_name)

    redirect_uri = str(request.url_for("oauth_auth_redirect", provider_name=provider_name))
    url = provider.get_oauth_url(redirect_url=redirect_uri)

    return url


@router.get(
    "/{provider_name}/auth/token",
    status_code=HTTPStatus.OK,
    tags=["oauth"],
    description="OAuth redirect",
    summary="OAuth redirect",
)
async def oauth_auth_redirect(
    code: Annotated[str, Query()],
    request: Request,
    provider_name: Annotated[str, Path(enum=list(OauthProvider))],  # type: ignore
    oauth_service_factory=Depends(get_oauth_service_factory),
) -> Response:
    provider = get_oauth_provider(provider_name)
    service: OAuthServiceInterface | None = oauth_service_factory(provider_name)

    response = Response(status_code=HTTPStatus.OK)
    ip = request.client.host  # type: ignore
    user_agent = request.headers.get("User-Agent")
    redirect_uri = str(request.url_for("oauth_auth_redirect", provider_name=provider_name))
    access_token = await provider.exchange_token(redirect_url=redirect_uri, code=code)
    info = await provider.get_user_info(access_token)

    tokens = await service.authorize(
        oauth_info=info,
        user_agent=user_agent,
        ip=ip,
    )

    response.set_cookie("access_token", tokens.access, httponly=True, secure=True)
    response.set_cookie("refresh_token", tokens.refresh, httponly=True, secure=True)
    return response


@router.get(
    "/{provider_name}/bind",
    status_code=HTTPStatus.OK,
    tags=["oauth"],
    description="OAuth bind",
    summary="OAuth bind",
)
async def oauth_bind(
    request: Request,
    provider_name: Annotated[str, Path(enum=list(OauthProvider))],  # type: ignore
) -> str:
    provider = get_oauth_provider(provider_name)

    redirect_uri = str(request.url_for("oauth_bind_redirect", provider_name=provider_name))
    url = provider.get_oauth_url(redirect_url=redirect_uri)

    return url


@router.get(
    "/{provider_name}/bind/token",
    status_code=HTTPStatus.OK,
    tags=["oauth"],
    description="OAuth bind redirect",
    summary="OAuth bind redirect",
    response_class=Response,
)
async def oauth_bind_redirect(
    code: Annotated[str, Query()],
    request: Request,
    provider_name: Annotated[str, Path(enum=list(OauthProvider))],  # type: ignore
    oauth_service_factory=Depends(get_oauth_service_factory),
    current_user: User = Depends(get_current_user),
) -> Response:
    provider = get_oauth_provider(provider_name)
    service: OAuthServiceInterface = oauth_service_factory(provider_name)

    redirect_uri = str(request.url_for("oauth_bind_redirect", provider_name=provider_name))
    access_token = await provider.exchange_token(redirect_url=redirect_uri, code=code)
    info = await provider.get_user_info(access_token)
    await service.bind(current_user.id, info)

    return Response(status_code=HTTPStatus.CREATED)


@router.delete(
    "/{oauth_id}",
    status_code=HTTPStatus.OK,
    tags=["oauth"],
    description="Delete binded social",
    summary="Delete binded social",
    response_class=Response,
    dependencies=[Depends(get_current_user)],
)
async def delete_social(
    oauth_id: str,
    socialnet_repository: SocialnetRepository = Depends(get_socialnet_repository),
) -> Response:
    await socialnet_repository.delete_by_oauth_id(oauth_id=oauth_id)
    return Response(status_code=HTTPStatus.OK)


@router.get(
    "/oauth/",
    status_code=HTTPStatus.OK,
    tags=["oauth"],
    description="Binded socialnet",
    summary="Binded socialnet",
    response_model=list[SocialNetSchema],
)
async def get_socialnet_list(
    user_socialnet_repository: UserSocialnetRepository = Depends(get_user_socialnet_repository),
    current_user: User = Depends(get_current_user),
) -> list[SocialNetSchema]:
    records = await user_socialnet_repository.get_user_socialnet(current_user.id)

    return [SocialNetSchema(**record.dict()) for record in records]
