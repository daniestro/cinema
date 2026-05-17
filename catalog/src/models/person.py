from pydantic import conlist

from .common import OrjsonModel, UUIDMixin


class Person(OrjsonModel, UUIDMixin):
    full_name: str


class RoleFilm(OrjsonModel, UUIDMixin):
    roles: conlist(str, min_items=0)


class PersonWithFilms(Person):
    films: conlist(RoleFilm, min_items=0)
