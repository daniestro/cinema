from datetime import datetime
from time import sleep

import psycopg
from psycopg.rows import dict_row

from elastic import Elastic
from processes import etl_process_for_movies, etl_process_for_persons, etl_process_for_genres
from logger import logger
from decorators import backoff
from utils.config import database_settings, elastic_settings
from state.state_storage import JsonFileStorage, State


@backoff()
def etl_pipline():
    """Функция, которая запускает pipline ETL"""

    # Для каждого пайплайна создается свой обработчик State
    state_movies = State(JsonFileStorage(logger=logger, file_path='state_movies.json'))
    state_persons = State(JsonFileStorage(logger=logger, file_path='state_persons.json'))
    state_genres = State(JsonFileStorage(logger=logger, file_path='state_genres.json'))
    elastic = Elastic(**elastic_settings.dict())

    # Для работы с Postgres я использую Psycopg последней версии (3.19)
    # В этой версии подключении через `with` закроется в конце блока
    with psycopg.connect(**database_settings.dict(), row_factory=dict_row) as conn, conn.cursor() as pg_cursor:
        # Определяем стартовые точки для процессов Postgres -> ES
        fetcher_movies_coro = etl_process_for_movies(state_movies, elastic, pg_cursor)
        fetcher_persons_coro = etl_process_for_persons(state_persons, state_movies, elastic, pg_cursor)
        fetcher_genres_coro = etl_process_for_genres(state_genres, state_movies, elastic, pg_cursor)

        while True:
            logger.info('Starting ETL process for updates ...')

            # Запуск процессов
            fetcher_movies_coro.send(state_movies.get_state('last_movies_updated') or str(datetime.min))
            fetcher_persons_coro.send(state_persons.get_state('last_persons_updated') or str(datetime.min))
            fetcher_genres_coro.send(state_genres.get_state('last_genres_updated') or str(datetime.min))

            sleep(10)


if __name__ == '__main__':
    etl_pipline()
