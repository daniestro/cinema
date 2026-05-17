from uuid import UUID

import orjson
from pydantic import BaseModel, Field


def orjson_dumps(v, *, default):
    return orjson.dumps(v, default=default).decode()


class OrjsonModel(BaseModel):
    class Config:
        json_loads = orjson.loads
        json_dumps = orjson_dumps


class UUIDMixin(BaseModel):
    uuid: UUID = Field(..., alias="id")

    class Config:
        allow_population_by_field_name = True
