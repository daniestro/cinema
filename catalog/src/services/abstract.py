from abc import ABC, abstractmethod


class AbstractCacheStorage(ABC):
    def __init__(self, cache_service):
        self.cache_service = cache_service

    @abstractmethod
    async def data_from_cache(self, *args):
        pass

    @abstractmethod
    async def put_data_to_cache(self, *args):
        pass


class AbstractDataStorage(ABC):
    def __init__(self, storage_service):
        self.storage_service = storage_service

    @abstractmethod
    async def get_by_id(self, *args):
        pass

    @abstractmethod
    async def get_list(self, *args):
        pass
