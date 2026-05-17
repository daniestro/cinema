import uuid

from pydantic import EmailStr

from .base import DTOBaseSchema


class SocialNetSchema(DTOBaseSchema):
    id: uuid.UUID
    oauth_id: str
    email: EmailStr
