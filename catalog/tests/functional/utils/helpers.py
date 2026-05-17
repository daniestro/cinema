import json
import time
from functools import wraps


def backoff(name, start_sleep_time=5, factor=2, border_sleep_time=10):
    def func_wrapper(func):
        @wraps(func)
        def inner(*args, **kwargs):
            sleep_time = start_sleep_time
            while True:
                result = func(*args, **kwargs)
                if result:
                    return result
                print(f"Retrying connect to {name} in {sleep_time} seconds...")
                time.sleep(sleep_time)
                sleep_time *= factor
                if sleep_time >= border_sleep_time:
                    sleep_time = border_sleep_time

        return inner

    return func_wrapper


def get_es_bulk_query(data: list[dict], es_index: str) -> str:
    bulk_query = []
    for row in data:
        bulk_query.extend([
            json.dumps({'index': {'_index': es_index, '_id': row['id']}}),
            json.dumps(row)
        ])

    return '\n'.join(bulk_query) + '\n'
