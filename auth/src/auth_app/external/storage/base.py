import abc
from datetime import timedelta
from typing import Any


class BaseStorageRepository(abc.ABC):
    @abc.abstractmethod
    async def get(self, key: Any) -> Any:
        ...

    @abc.abstractmethod
    async def put(self, key: Any, value: Any, expires_in: timedelta) -> None:
        ...
