import asyncio
import contextlib
import json
import logging

import typer
from auth_app.db.sqlalchemy import get_async_session
from auth_app.errors.external import RoleAlreadyExists
from auth_app.external.role_repository import RoleRepository
from auth_app.external.user_repository import UserRepository
from auth_app.external.user_role_repository import UserRoleRepository
from auth_app.services.hash_service import get_hash_service
from auth_app.services.role_service import RoleService
from auth_app.services.user_role_service import UserRoleService
from auth_app.services.user_service import UserService

router = typer.Typer(help="Commands with auth service")


@contextlib.asynccontextmanager
async def get_user_service():
    logger = logging.getLogger("CLI")
    get_async_session_context = contextlib.asynccontextmanager(get_async_session)
    async with get_async_session_context() as session:
        user_rep = UserRepository(logger=logger, session=session)
        yield UserService(user_rep, get_hash_service(), logger=logger)


@contextlib.asynccontextmanager
async def get_role_service():
    logger = logging.getLogger("CLI")
    get_async_session_context = contextlib.asynccontextmanager(get_async_session)
    async with get_async_session_context() as session:
        role_rep = RoleRepository(logger=logger, session=session)
        yield RoleService(role_rep, logger=logger)


@contextlib.asynccontextmanager
async def get_user_role_service():
    logger = logging.getLogger("CLI")
    get_async_session_context = contextlib.asynccontextmanager(get_async_session)
    async with get_async_session_context() as session:
        user_rep = UserRepository(logger=logger, session=session)
        role_rep = RoleRepository(logger=logger, session=session)
        user_role_rep = UserRoleRepository(logger=logger, session=session)
        yield UserRoleService(
            user_rep,
            role_rep,
            user_role_rep,
            logger=logger,
        )


@router.command(help="Create admin user")
def create(email: str, password: str):
    async def _inner():
        async with get_role_service() as service:
            try:
                await service.create("admin", "Super-user role")
            except RoleAlreadyExists:
                await service.role_repository.session.rollback()

            role = await service.get_by_name("admin")

        async with get_user_service() as service:
            user = await service.create(email, password)

        async with get_user_role_service() as service:
            await service.set_user_role(user.id, role.id)

        print("Successfully created admin")
        cred = {"email": email, "password": password}
        print(json.dumps(cred, indent=3))

    asyncio.run(_inner())
