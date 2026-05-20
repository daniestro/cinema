import threading
from datetime import datetime
from time import monotonic

import psycopg
from aiohttp import web
from psycopg.rows import dict_row

from decorators import CONNECTION_ERRORS, backoff
from elastic import Elastic
from http_api import create_app
from logger import logger
from processes import etl_process_for_genres, etl_process_for_movies, etl_process_for_persons
from runtime import EtlRuntime
from state.state_storage import JsonFileStorage, State
from utils.config import database_settings, elastic_settings


TICK_INTERVAL_SECONDS = 10
STATE_FILES = ('state_movies.json', 'state_persons.json', 'state_genres.json')
WEB_PORT = 8000


@backoff()
def build_elastic() -> Elastic:
    return Elastic(**elastic_settings.dict())


@backoff()
def etl_pipline(runtime: EtlRuntime, elastic: Elastic):
    """Функция, которая запускает pipline ETL"""

    # Для каждого пайплайна создается свой обработчик State
    state_movies = State(JsonFileStorage(logger=logger, file_path=STATE_FILES[0]))
    state_persons = State(JsonFileStorage(logger=logger, file_path=STATE_FILES[1]))
    state_genres = State(JsonFileStorage(logger=logger, file_path=STATE_FILES[2]))

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
            try:
                with runtime.lock:
                    fetcher_movies_coro.send(state_movies.get_state('last_movies_updated') or str(datetime.min))
                    fetcher_persons_coro.send(state_persons.get_state('last_persons_updated') or str(datetime.min))
                    fetcher_genres_coro.send(state_genres.get_state('last_genres_updated') or str(datetime.min))
                runtime.last_error = None
            # Connection errors propagate to @backoff: it sleeps and reruns the whole pipeline,
            # which reopens Postgres. Other bugs are recorded in runtime and the worker keeps going,
            # so /state surfaces them instead of silently killing the thread.
            except CONNECTION_ERRORS:
                raise
            except Exception as exc:
                logger.exception('ETL tick failed')
                runtime.last_error = f'{type(exc).__name__}: {exc}'

            runtime.iteration += 1
            runtime.last_run_finished_at = datetime.utcnow()
            runtime.last_tick_duration_ms = (monotonic() - tick_started) * 1000

            runtime.trigger.wait(TICK_INTERVAL_SECONDS)
            runtime.trigger.clear()


def main():
    runtime = EtlRuntime()
    elastic = build_elastic()
    worker = threading.Thread(target=etl_pipline, args=(runtime, elastic), daemon=True, name='etl-worker')
    worker.start()
    app = create_app(runtime, elastic, worker, STATE_FILES)
    web.run_app(app, port=WEB_PORT)
    # run_app returns on SIGTERM/SIGINT. Exit non-zero so docker's restart policy
    # kicks in if we're stopping because the worker has died rather than a clean shutdown.
    raise SystemExit(1)


if __name__ == '__main__':
    main()
