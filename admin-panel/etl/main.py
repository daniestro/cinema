import threading
from datetime import datetime
from time import monotonic

import psycopg
from psycopg.rows import dict_row

from elastic import Elastic
from processes import etl_process_for_movies, etl_process_for_persons, etl_process_for_genres
from logger import logger
from decorators import backoff
from runtime import EtlRuntime
from utils.config import database_settings, elastic_settings
from state.state_storage import JsonFileStorage, State


TICK_INTERVAL_SECONDS = 10


@backoff()
def etl_pipline(runtime: EtlRuntime):
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
            tick_started = monotonic()
            runtime.last_run_started_at = datetime.utcnow()

            fetcher_movies_coro.send(state_movies.get_state('last_movies_updated') or str(datetime.min))
            fetcher_persons_coro.send(state_persons.get_state('last_persons_updated') or str(datetime.min))
            fetcher_genres_coro.send(state_genres.get_state('last_genres_updated') or str(datetime.min))

            runtime.iteration += 1
            runtime.last_run_finished_at = datetime.utcnow()
            runtime.last_tick_duration_ms = (monotonic() - tick_started) * 1000

            runtime.trigger.wait(TICK_INTERVAL_SECONDS)
            runtime.trigger.clear()


def main():
    runtime = EtlRuntime()
    worker = threading.Thread(target=etl_pipline, args=(runtime,), daemon=True, name='etl-worker')
    worker.start()
    worker.join()
    # join() returns normally even if the worker raised; exit non-zero so the
    # container's restart policy kicks in instead of silently exiting 0.
    raise SystemExit(1)


if __name__ == '__main__':
    main()
