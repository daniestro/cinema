from http import HTTPStatus
from typing import Optional, Annotated

from fastapi import APIRouter, Depends, HTTPException, Request

from services.film import get_film_service
from services.common import BaseService
from models.film import DetailFilm, Film
from models.validators import GenreFilter, QueryFilter, Paginator, UUID
from core.exceptions import ErrorMessagesUtil
from services.auth import security_jwt
from limiter import limiter


router = APIRouter()


@router.get(
    '/',
    response_model=list[Film],
    response_model_by_alias=False,
    summary="Получить список всех фильмов"
)
@limiter.limit("20/minute")
async def all_films(
        request: Request,
        user: Annotated[dict, Depends(security_jwt)],
        filters: GenreFilter = Depends(),
        paginator: Paginator = Depends(),
        film_service: BaseService = Depends(get_film_service)
) -> Optional[list[Film]]:
    """
    Отдает список фильмов подходящих под запрос

    - **sort**: сортировка фильмов по рейтингу
    - **genre**: фильмы только в этом жанре
    - **page_size**: номер страницы
    - **page_number**: кол-во элементов на странице
    """

    films = await film_service.get_list(filters.genre, None, filters.sort,
                                         paginator.page_number, paginator.page_size)
    if not films:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=ErrorMessagesUtil.films_not_found())
    return films


@router.get(
    '/{film_id}',
    response_model=DetailFilm,
    response_model_by_alias=False,
    summary="Получить информацию о фильме"
)
@limiter.limit("20/minute")
async def film_details(
        film_id: UUID,
        request: Request,
        user: Annotated[dict, Depends(security_jwt)],
        film_service: BaseService = Depends(get_film_service)
) -> DetailFilm:
    film = await film_service.get_by_id(film_id)
    if not film:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=ErrorMessagesUtil.film_not_found())
    return film


@router.get(
    '/search/',
    response_model=list[Film],
    response_model_by_alias=False,
    summary="Поисковой запрос по фильмам"
)
@limiter.limit("20/minute")
async def search_films(
        request: Request,
        user: Annotated[dict, Depends(security_jwt)],
        filters: QueryFilter = Depends(),
        paginator: Paginator = Depends(),
        film_service: BaseService = Depends(get_film_service)
) -> Optional[list[Film]]:
    """
    Отдает список фильмов подходящих под поисковой запрос
    _Поиск фильма является неточным и происходит по его названию_

    - **sort**: сортировка фильмов по рейтингу
    - **query**: поисковой запрос по названию фильма
    - **page_size**: номер страницы
    - **page_number**: кол-во элементов на странице
    """

    films = await film_service.get_list(None, filters.query, filters.sort, paginator.page_number, paginator.page_size)
    if not films:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=ErrorMessagesUtil.films_not_found())
    return films
