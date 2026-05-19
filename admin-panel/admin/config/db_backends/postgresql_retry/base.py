import logging
import time

import psycopg2
from django.db.backends.postgresql import base as postgresql_base


logger = logging.getLogger(__name__)

DEFAULT_BASE_DELAY = 15.0


class DatabaseWrapper(postgresql_base.DatabaseWrapper):
    """
    Postgres backend that retries the initial socket connect on transient
    OperationalError indefinitely with linear backoff: the Nth attempt sleeps
    `base_delay * N` seconds.

    Override via DATABASES['default']['OPTIONS']:
        connect_base_delay (float) — base step in seconds, default 15.0
    """

    def get_new_connection(self, conn_params):
        options = self.settings_dict.get('OPTIONS', {}) or {}
        base_delay = float(options.get('connect_base_delay', DEFAULT_BASE_DELAY))

        attempt = 1
        while True:
            try:
                return super().get_new_connection(conn_params)
            except psycopg2.OperationalError as exc:
                reason = str(exc).strip().splitlines()[-1] if str(exc) else exc.__class__.__name__
                delay = base_delay * attempt
                logger.warning(
                    'Warning | Postgres lost connection | Connect attempt %d failed: %s; retrying in %.1fs',
                    attempt, reason, delay,
                )
                time.sleep(delay)
            attempt += 1
