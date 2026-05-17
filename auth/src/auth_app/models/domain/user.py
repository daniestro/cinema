from typing import TYPE_CHECKING
from uuid import UUID

from sqlmodel import Field, Relationship, SQLModel

from .base import get_uuid_field
from .user_role import UserRole

if TYPE_CHECKING:
    from .role import Role
    from .socialnet import Socialnet


class User(SQLModel, table=True):
    __tablename__ = "user"

    id: UUID = get_uuid_field()
    email: str = Field(unique=True, index=True, nullable=False)
    hashed_password: str = Field(max_length=256, min_length=8, nullable=False)

    roles: list["Role"] = Relationship(
        link_model=UserRole,
        back_populates="users",
        sa_relationship_kwargs={"cascade": "all, delete"},
    )
    socialnet: list["Socialnet"] = Relationship(
        sa_relationship_kwargs={"cascade": "all, delete"},
    )
