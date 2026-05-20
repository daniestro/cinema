import asyncio
import json
import os
import threading
from datetime import datetime, timedelta
from typing import Iterable

from aiohttp import web

from elastic import Elastic
from runtime import EtlRuntime


HEALTH_STALENESS_THRESHOLD = timedelta(seconds=60)


async def handle_health(request: web.Request) -> web.Response:
    runtime: EtlRuntime = request.app['runtime']
    worker: threading.Thread = request.app['worker']

    if not worker.is_alive():
        return web.json_response(
            {'status': 'dead', 'reason': 'etl worker thread is not alive'},
            status=503,
        )

    last_finished = runtime.last_run_finished_at
    if last_finished is None:
        return web.json_response(
            {'status': 'starting', 'reason': 'no ticks completed yet'},
            status=503,
        )

    staleness = datetime.utcnow() - last_finished
    if staleness > HEALTH_STALENESS_THRESHOLD:
        return web.json_response(
            {'status': 'stale', 'reason': f'last tick finished {staleness.total_seconds():.0f}s ago'},
            status=503,
        )

    return web.json_response({'status': 'ok'})


async def handle_state(request: web.Request) -> web.Response:
    runtime: EtlRuntime = request.app['runtime']
    state_files: Iterable[str] = request.app['state_files']

    files: dict = {}
    for path in state_files:
        try:
            with open(path) as fh:
                files[path] = json.load(fh)
        except FileNotFoundError:
            files[path] = None
        except json.JSONDecodeError as exc:
            files[path] = {'error': f'unreadable: {exc}'}

    return web.json_response({
        'iteration': runtime.iteration,
        'last_run_started_at': runtime.last_run_started_at.isoformat() if runtime.last_run_started_at else None,
        'last_run_finished_at': runtime.last_run_finished_at.isoformat() if runtime.last_run_finished_at else None,
        'last_tick_duration_ms': runtime.last_tick_duration_ms,
        'last_error': runtime.last_error,
        'state_files': files,
    })


async def handle_trigger(request: web.Request) -> web.Response:
    runtime: EtlRuntime = request.app['runtime']
    runtime.trigger.set()
    return web.json_response({'status': 'triggered'}, status=202)


async def handle_reset_index(request: web.Request) -> web.Response:
    runtime: EtlRuntime = request.app['runtime']
    elastic: Elastic = request.app['elastic']
    state_files: Iterable[str] = request.app['state_files']

    # ES calls and runtime.lock are blocking; run on a worker thread so the event loop stays free.
    def do_reset() -> dict:
        deleted_indexes: list = []
        removed_state: list = []
        with runtime.lock:
            for index in elastic.index_names():
                elastic.delete_index(index)
                deleted_indexes.append(index)
            for path in state_files:
                try:
                    os.remove(path)
                    removed_state.append(path)
                except FileNotFoundError:
                    pass
            elastic.ensure_indexes()
            runtime.trigger.set()
        return {'deleted_indexes': deleted_indexes, 'removed_state_files': removed_state}

    result = await asyncio.to_thread(do_reset)
    return web.json_response({'status': 'ok', **result})


def create_app(
    runtime: EtlRuntime,
    elastic: Elastic,
    worker: threading.Thread,
    state_files: Iterable[str],
) -> web.Application:
    app = web.Application()
    app['runtime'] = runtime
    app['elastic'] = elastic
    app['worker'] = worker
    app['state_files'] = tuple(state_files)
    app.add_routes([
        web.get('/health', handle_health),
        web.get('/state', handle_state),
        web.post('/trigger', handle_trigger),
        web.post('/reset-index', handle_reset_index),
    ])
    return app
