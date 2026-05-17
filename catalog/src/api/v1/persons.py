from http import HTTPStatus
from typing import Optional, Annotated

from fastapi import APIRouter, Depends, HTTPException, Request

from services.persons import get_person_service
from services.common import BaseService
from models.person import PersonWithFilms
from models.film import Film
from models.validators import Paginator, UUID
from core.exceptions import ErrorMessagesUtil
from services.auth import security_jwt
from limiter import limiter


router = APIRouter()


@router.get(
    '/{person_id}',
    response_model=PersonWithFilms,
    response_model_by_alias=False,
    summary="Получить информацию о персоне"
)
@limiter.limit("20/minute")
async def person_details(
        person_id: UUID,
        request: Request,
        person_service: BaseService = Depends(get_person_service)
) -> Optional[PersonWithFilms]:
    person = await person_service.get_by_id(person_id)
    if not person:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=ErrorMessagesUtil.person_not_found())
    return person


@router.get(
    '/{person_id}/film',
    response_model=list[Film],
    response_model_by_alias=False,
    summary="Получить список фильмов по персоне"
)
@limiter.limit("20/minute")
async def person_films(
        person_id: UUID,
        request: Request,
        user: Annotated[dict, Depends(security_jwt)],
        person_service: BaseService = Depends(get_person_service)
) -> Optional[PersonWithFilms]:
    films = await person_service.get_list(person_id, None, None, None)
    if not films:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=ErrorMessagesUtil.films_not_found())
    return films


@router.get(
    '/search/',
    response_model=list[PersonWithFilms],
    response_model_by_alias=False,
    summary="Поисковой запрос по персонам"
)
@limiter.limit("20/minute")
async def person_search(
        request: Request,
        user: Annotated[dict, Depends(security_jwt)],
        query: str = None,
        paginator: Paginator = Depends(),
        person_service: BaseService = Depends(get_person_service)
) -> Optional[PersonWithFilms]:
    """
    Отдает список персон подходящих под поисковой запрос
    _Поиск персоны является неточным и происходит по его полному имени_

    - **query**: поисковой запрос по имени персоны
    - **page_size**: номер страницы
    - **page_number**: кол-во элементов на странице
    """

    person = await person_service.get_list(None, query, paginator.page_number, paginator.page_size)
    if not person:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=ErrorMessagesUtil.person_not_found())
    return person
