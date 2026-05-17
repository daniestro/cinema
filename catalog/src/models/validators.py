from uuid import UUID

from enum import Enum
from fastapi import Query
from pydantic import BaseModel


class Paginator(BaseModel):
    page_size: int = Query(default=20, ge=1, le=100)
    page_number: int = Query(default=1, ge=1)


class Choises(str, Enum):
    first = 'imdb_rating'
    second = '-imdb_rating'


class Filter(BaseModel):
    sort: Choises = Query(default=None)


class GenreFilter(Filter):
    genre: UUID = Query(default=None)


class QueryFilter(Filter):
    query: str = Query(default=None)
