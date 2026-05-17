import uuid

from .base import DTOBaseSchema


class RoleCreateSchema(DTOBaseSchema):
    name: str
    description: str


class RoleUpdateSchema(DTOBaseSchema):
    name: str
    description: str


class RoleInfoSchema(DTOBaseSchema):
    id: uuid.UUID
    name: str
    description: str
