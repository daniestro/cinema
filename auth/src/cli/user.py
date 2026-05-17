import asyncio
import random
from string import ascii_lowercase

import typer
from auth_app.errors.external import RoleAlreadyExists

from cli.admin import get_role_service, get_user_role_service, get_user_service

router = typer.Typer(help="Commands with auth service")


def generate_email() -> str:
    return "".join([random.choice(ascii_lowercase) for i in range(10)]) + "@mail.ru"  # noqa: S311


def generate_password() -> str:
    return "".join([random.choice(ascii_lowercase) for i in range(10)])  # noqa: S311


@router.command(help="Create test users")
def create(n: int):
    async def _inner():
        async with get_role_service() as service:
            try:
                await service.create("user", "User")
            except RoleAlreadyExists:
                await service.role_repository.session.rollback()

            try:
                await service.create("subscriber", "Subscriber")
            except RoleAlreadyExists:
                await service.role_repository.session.rollback()

            subscriber_role = await service.get_by_name("subscriber")
            user_role = await service.get_by_name("user")

        for _ in range(n):
            async with get_user_service() as service:
                user = await service.create(generate_email(), generate_password())

            async with get_user_role_service() as service:
                await service.set_user_role(user.id, user_role.id)
                is_subscriber = False
                if random.randint(0, 1):  # noqa: S311
                    await service.set_user_role(user.id, subscriber_role.id)
                    is_subscriber = True

            print(f"Successfully created user {user.email}, subscriber - {is_subscriber}")

    asyncio.run(_inner())
