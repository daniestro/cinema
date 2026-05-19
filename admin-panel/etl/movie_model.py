import uuid

from pydantic import BaseModel, validator


class UUIDMixin(BaseModel):
    id: uuid.UUID

    def dict(self, **kwargs):
        # Получаем словарь атрибутов с помощью метода dict() из базового класса
        data = super().dict(**kwargs)

        # Преобразуем id в строковое представление
        data['id'] = str(data['id'])

        return data


class Person(UUIDMixin):
    full_name: str


class Genre(UUIDMixin):
    name: str


class GenreWithDesc(Genre):
    description: str

    @validator('description', pre=True)
    def none_to_str(cls, field):
        if field is None:
            return ''
        return field


class Movie(UUIDMixin):
    title: str
    genre: list
    description: str
    imdb_rating: float
    actors_names: list[str] = []
    writers_names: list[str] = []
    directors_names: list[str] = []
    actors: list[Person] = []
    writers: list[Person] = []
    directors: list[Person] = []
    poster_url: str | None = None

    @validator('description', pre=True)
    def none_to_str(cls, field):
        if field is None:
            return ''
        return field

    @validator('imdb_rating', pre=True)
    def none_to_float(cls, field):
        if field is None:
            return 0.0
        return field
