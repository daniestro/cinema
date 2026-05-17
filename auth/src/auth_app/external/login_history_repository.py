import logging
import uuid
from logging import Logger

from fastapi import Depends
from sqlalchemy.exc import NoResultFound
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from auth_app.db.sqlalchemy import get_async_session
from auth_app.errors.external import UserNotFound
from auth_app.models.domain.login_record import LoginRecord


class LoginRecordRepository:
    def __init__(self, session: AsyncSession, logger: Logger) -> None:
        self.session = session
        self.logger = logger

    async def create_record(
        self,
        user_id: uuid.UUID,
        user_agent: str,
        ip: str,
        access_jti: uuid.UUID,
        refresh_jti: uuid.UUID,
    ) -> LoginRecord:
        login_record = LoginRecord(
            user_id=user_id,
            user_agent=user_agent,
            ip=ip,
            access_jti=access_jti,
            refresh_jti=refresh_jti,
        )

        self.session.add(login_record)
        await self.session.commit()
        await self.session.refresh(login_record)
        self.logger.info(f"Created login_record {login_record.id}")
        return login_record

    async def get_login_records(
        self,
        user_id: uuid.UUID,
        limit: int,
        offset: int,
    ) -> list[LoginRecord]:
        result = await self.session.execute(
            select(LoginRecord)  #
            .where(LoginRecord.user_id == user_id)  #
            .order_by(LoginRecord.created_at.desc())  #
            .limit(limit)  #
            .offset(offset),  #
        )
        try:
            return result.scalars().all()
        except NoResultFound:
            raise UserNotFound


def get_login_record_repository(session: AsyncSession = Depends(get_async_session)) -> LoginRecordRepository:
    logger = logging.getLogger(__name__)
    return LoginRecordRepository(session=session, logger=logger)
