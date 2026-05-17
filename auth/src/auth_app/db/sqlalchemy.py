from sqlalchemy.ext.asyncio import AsyncEngine
from sqlalchemy.orm import sessionmaker
from sqlmodel.ext.asyncio.session import AsyncSession

engine: AsyncEngine | None = None


class EngineNotInitializedError(Exception):
    ...


async def get_async_session() -> AsyncSession:
    if not engine:
        raise EngineNotInitializedError
    async_session = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)
    async with async_session() as session:
        yield session
