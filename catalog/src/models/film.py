from typing import Optional

from pydantic import confloat, conlist

from .common import OrjsonModel, UUIDMixin
from .genre import SmallGenre
from .person import Person


class Film(OrjsonModel, UUIDMixin):
    title: str
    imdb_rating: confloat(ge=0.0, le=100.0) = 0.0


class DetailFilm(Film):
    description: Optional[str] = None
    genre: conlist(SmallGenre, min_items=1)
    directors: conlist(Person, min_items=0)
    actors: conlist(Person, min_items=0)
    writers: conlist(Person, min_items=0)
