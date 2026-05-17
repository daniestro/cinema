from http import HTTPStatus

import pytest

from ..testdata.validation import pagination_params


@pytest.mark.parametrize(
    'query_data, expected_answer, endpoint',
    pagination_params
)
@pytest.mark.asyncio
async def test_person_search_validation(make_get_request, query_data, expected_answer, endpoint):
    """
    Тест, который проверяет граничные случаи пагинации
    """
    status, body = await make_get_request(endpoint, query_data)

    assert status == expected_answer['status']
    assert body == expected_answer['body']


@pytest.mark.parametrize(
    'index, id_path',
    [('films', 'film_id'), ('persons', 'person_id'), ('genres', 'genre_id')]
)
@pytest.mark.asyncio
async def test_get_by_id_validation(make_get_request, index, id_path):
    """
    Тест, который проверяет валидацию uuid
    """
    status, body = await make_get_request(f'/{index}/' + '1', {})

    assert status == HTTPStatus.UNPROCESSABLE_ENTITY
    assert body == {
        "detail": [
            {
             "loc": [
                "path",
                id_path
             ],
             "msg": "value is not a valid uuid",
             "type": "type_error.uuid"
            }
        ]
    }
