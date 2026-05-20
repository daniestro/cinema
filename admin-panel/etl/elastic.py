import json
from typing import Union

import requests

from logger import logger
from movie_model import Movie, Genre, Person


class Elastic:
    """Класс для взаимодействия с ES"""
    def __init__(self, host: str, port: str, schema_path: str = 'es_schema.json'):
        self.__link = f'http://{host}:{port}'
        self._schema_path = schema_path
        self.ensure_indexes()

    def ensure_indexes(self) -> None:
        """Создаёт индексы из schema, если они отсутствуют."""
        for index_name, index_settings in self.get_indexes(self._schema_path).items():
            index_response = self.get_index(index_name)
            if not index_response.get(index_name):
                requests.put(self.__link + '/' + index_name, json=index_settings,
                             headers={"Content-Type": "application/json; charset=utf-8"})
                logger.info('Created index ' + index_name)

    def delete_index(self, index: str) -> None:
        """Удаляет индекс. 404 трактуется как успех (нечего удалять)."""
        response = requests.delete(self.__link + '/' + index)
        if response.status_code not in (200, 404):
            response.raise_for_status()
        logger.info(f'Deleted index {index} (status {response.status_code})')

    def index_names(self) -> list[str]:
        """Имена индексов, описанных в schema."""
        return list(self.get_indexes(self._schema_path).keys())

    def get_index(self, index: str) -> dict:
        """Функция возвращает информацию об индексе"""
        index = requests.get(self.__link + '/' + index).json()
        return index

    def bulk_post(self, index: str, data: list[Union[Genre, Person, Movie]]) -> dict:
        """Bulk запрос к ES"""
        formatted_data = []

        for elem in data:
            elem = elem.dict()
            formatted_data.append({"index": {"_index": index, "_id": elem['id']}})
            formatted_data.append(elem)

        data_to_post = '\n'.join(json.dumps(elem) for elem in formatted_data) + '\n'
        result = requests.post(self.__link + '/_bulk',
                               headers={"Content-Type": "application/x-ndjson; charset=utf-8"},
                               data=data_to_post).json()
        return result

    def get_indexes(self, file_path: str) -> dict:
        """Функция возвращает схемы индекса из файла"""
        with open(file_path, 'r') as txt_file:
            return json.load(txt_file)
