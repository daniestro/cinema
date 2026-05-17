from typing import TYPE_CHECKING
from uuid import UUID

from sqlmodel import Field, Relationship, SQLModel

from .base import get_uuid_field
from .user_role import UserRole

if TYPE_CHECKING:
    from .user import User


class Role(SQLModel, table=True):
    __tablename__ = "role"

    id: UUID = get_uuid_field()
    name: str = Field(max_length=256, unique=True, nullable=False)
    description: str | None = Field(max_length=256)

    users: list["User"] = Relationship(link_model=UserRole, back_populates="roles")
