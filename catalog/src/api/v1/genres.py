from http import HTTPStatus
from typing import Optional, Annotated

from fastapi import APIRouter, Depends, HTTPException, Request

from services.genres import get_genre_service
from services.common import BaseService
from models.genre import Genre
from models.validators import UUID
from core.exceptions import ErrorMessagesUtil
from services.auth import security_jwt
from limiter import limiter


router = APIRouter()


@router.get(
    '/',
    response_model=list[Genre],
    response_model_by_alias=False,
    summary="Получить список всех жанров"
)
@limiter.limit("20/minute")
async def all_genres(
        request: Request,
        user: Annotated[dict, Depends(security_jwt)],
        genre_service: BaseService = Depends(get_genre_service)
) -> Optional[list[Genre]]:
    genres = await genre_service.get_list()
    if not genres:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=ErrorMessagesUtil.genres_not_found())
    return genres


@router.get(
    '/{genre_id}',
    response_model=Genre,
    response_model_by_alias=False,
    summary="Получить информацию о жанре"
)
@limiter.limit("20/minute")
async def genre_details(
        genre_id: UUID,
        request: Request,
        genre_service: BaseService = Depends(get_genre_service)
) -> Genre:
    genre = await genre_service.get_by_id(genre_id)
    if not genre:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=ErrorMessagesUtil.genre_not_found())
    return genre
