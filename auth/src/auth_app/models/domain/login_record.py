import datetime
from uuid import UUID

from sqlmodel import TIMESTAMP, Column, Field, ForeignKey, SQLModel, text

from .base import get_uuid_field


class LoginRecord(SQLModel, table=True):
    __tablename__ = "login_record"

    id: UUID = get_uuid_field()
    user_id: UUID = Field(sa_column=Column(ForeignKey("user.id", ondelete="CASCADE"), nullable=False))
    user_agent: str = Field(nullable=True)
    ip: str = Field(nullable=True)
    access_jti: UUID = Field()
    refresh_jti: UUID = Field()
    created_at: datetime.datetime = Field(
        sa_column=Column(
            TIMESTAMP(timezone=True),
            nullable=False,
            server_default=text("CURRENT_TIMESTAMP"),
        ),
    )
