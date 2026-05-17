import uuid

from pydantic import EmailStr, Field

from .base import DTOBaseSchema


class UserSignUpSchema(DTOBaseSchema):
    email: EmailStr = Field(title="Email")
    password: str = Field(title="Password", min_length=6)


class UserSignInSchema(DTOBaseSchema):
    email: EmailStr = Field(title="Email")
    password: str = Field(title="Password", min_length=6)


class UserInfoSchema(DTOBaseSchema):
    id: uuid.UUID = Field(title="User id")
    email: EmailStr = Field(title="Email")
