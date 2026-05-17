import uuid

from .base import DTOBaseSchema


class UserRoleSchema(DTOBaseSchema):
    user_id: uuid.UUID
    role_id: uuid.UUID
