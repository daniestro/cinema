from .base import DTOBaseSchema


class JWTResponseSchema(DTOBaseSchema):
    access_token: str
    refresh_token: str
