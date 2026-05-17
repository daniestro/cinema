import uuid as uuid_pkg

from sqlmodel import Column, Field, ForeignKey, SQLModel


class UserRole(SQLModel, table=True):
    __tablename__ = "user_role"

    user_id: uuid_pkg.UUID = Field(sa_column=Column(ForeignKey("user.id", ondelete="CASCADE"), primary_key=True))
    role_id: uuid_pkg.UUID = Field(sa_column=Column(ForeignKey("role.id", ondelete="CASCADE"), primary_key=True))
