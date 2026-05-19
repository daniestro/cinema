from pathlib import Path

from django.core.management.base import BaseCommand, CommandError
from django.db import connection


CHECK_TABLE = 'content.film_work'


class Command(BaseCommand):
    help = (
        'Load seed data from a SQL file produced by '
        '`pg_dump --data-only --column-inserts`. '
        'Idempotent: skips loading if the target table already has rows.'
    )

    def add_arguments(self, parser):
        parser.add_argument(
            '--from',
            dest='source',
            required=True,
            help='Path to the SQL file to execute.',
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Load even if the target table already has rows.',
        )

    def handle(self, *args, source, force, **opts):
        path = Path(source)
        if not path.is_file():
            raise CommandError(f'Seed file not found: {path}')

        existing = self._count_existing()
        if existing > 0 and not force:
            self.stdout.write(
                f'{CHECK_TABLE} already has {existing} rows; skipping seed. '
                f'Pass --force to load anyway.'
            )
            return

        sql = path.read_text()
        with connection.cursor() as cursor:
            cursor.execute(sql)

        loaded = self._count_existing()
        self.stdout.write(
            self.style.SUCCESS(
                f'Seeded from {path}. {CHECK_TABLE} now has {loaded} rows.'
            )
        )

    def _count_existing(self) -> int:
        with connection.cursor() as cursor:
            cursor.execute(f'SELECT COUNT(*) FROM {CHECK_TABLE}')
            return cursor.fetchone()[0]
