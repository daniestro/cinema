import uuid

from fastapi import Depends, Request

from auth_app.errors.api import NoAccessError
from auth_app.errors.services import InvalidTokenError
from auth_app.models.domain.user import User
from auth_app.services.jwt_service import JWTService, get_jwt_service
from auth_app.services.token_blacklist_service import TokenBlacklistService, get_token_blacklist_service
from auth_app.services.user_service import UserService, get_user_service


class NoAccess(Exception):
    ...


async def get_current_user(
    request: Request,
    jwt_service: JWTService = Depends(get_jwt_service),
    user_service: UserService = Depends(get_user_service),
    black_list_service: TokenBlacklistService = Depends(get_token_blacklist_service),
):
    access_token = request.cookies.get("access_token")
    if await black_list_service.get(access_token):
        raise InvalidTokenError
    user_id = jwt_service.decode_access_token(access_token)["sub"]
    yield await user_service.get(uuid.UUID(user_id))


class RequireRole:
    def __init__(self, require_roles: set[str]) -> None:
        self.requre_roles = require_roles

    def __call__(self, get_current_user: User = Depends(get_current_user)):
        roles = {i.name for i in get_current_user.roles}

        if not roles.intersection(self.requre_roles):
            raise NoAccessError


require_admin = RequireRole({"admin"})
