import uuid
from typing import TYPE_CHECKING, NamedTuple

if TYPE_CHECKING:
    from auth_app.services.jwt_service import JWTService


class JWTPair(NamedTuple):
    access: str
    refresh: str


class JTIPair(NamedTuple):
    access: uuid.UUID
    refresh: uuid.UUID


class JWT(NamedTuple):
    tokens: JWTPair
    jti: JTIPair


def generate_jwt(jwt_service: "JWTService", user_id: str, email: str, roles: list[str]) -> JWT:
    access = jwt_service.encode_access_token(user_id, email, roles)
    refresh = jwt_service.encode_refresh_token(user_id, email, roles)

    access_jti = jwt_service.decode_token(access)["jti"]
    refresh_jti = jwt_service.decode_token(access)["jti"]

    tokens = JWTPair(access, refresh)
    jti = JTIPair(access=access_jti, refresh=refresh_jti)

    return JWT(tokens=tokens, jti=jti)
