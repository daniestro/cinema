from typing import Optional

from .common import OrjsonModel, UUIDMixin


class SmallGenre(OrjsonModel, UUIDMixin):
    name: str


class Genre(SmallGenre):
    description: Optional[str] = None
