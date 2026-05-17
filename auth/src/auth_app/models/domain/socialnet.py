from uuid import UUID

from sqlmodel import Field, SQLModel

from .base import get_uuid_field


class Socialnet(SQLModel, table=True):
    __tablename__ = "socialnet"

    id: UUID = get_uuid_field()
    oauth_id: str = Field(unique=True, index=True, nullable=False)
    email: str | None = Field(unique=True, nullable=True)

    user_id: UUID = Field(foreign_key="user.id")
