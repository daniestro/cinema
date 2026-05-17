import datetime

from .base import DTOBaseSchema


class LoginRecordSchema(DTOBaseSchema):
    created_at: datetime.datetime
    user_agent: str
    ip: str
