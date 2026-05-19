import time
from functools import wraps

import psycopg2
import requests

from logger import logger


# Only retry on transient connection-level failures to Postgres or Elasticsearch.
# Bugs (KeyError, TypeError, etc.) must surface immediately — retrying them
# forever hides the failure in the log noise.
CONNECTION_ERRORS = (
    psycopg2.OperationalError,
    psycopg2.InterfaceError,
    requests.ConnectionError,
    requests.Timeout,
)


def backoff(start_sleep_time=0.1, factor=2, border_sleep_time=10):
    """
    Функция для повторного выполнения функции через некоторое время, если возникла ошибка.
    Использует наивный экспоненциальный рост времени повтора (factor) до граничного времени ожидания (border_sleep_time)

    Формула:
        t = start_sleep_time * 2^(n) if t < border_sleep_time
        t = border_sleep_time if t >= border_sleep_time
    :param start_sleep_time: начальное время повтора
    :param factor: во сколько раз нужно увеличить время ожидания
    :param border_sleep_time: граничное время ожидания
    :return: результат выполнения функции
    """

    def func_wrapper(func):
        @wraps(func)
        def inner(*args, **kwargs):
            sleep_time = start_sleep_time
            while True:
                try:
                    result = func(*args, **kwargs)
                    return result
                except CONNECTION_ERRORS as e:
                    logger.warning(f"Connection error: {str(e)}. Retrying in {sleep_time} seconds...")
                    time.sleep(sleep_time)
                    sleep_time *= factor
                    if sleep_time >= border_sleep_time:
                        sleep_time = border_sleep_time

        return inner

    return func_wrapper


def coroutine(func):
    @wraps(func)
    def inner(*args, **kwargs):
        fn = func(*args, **kwargs)
        next(fn)
        return fn
    return inner
