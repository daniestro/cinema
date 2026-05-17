import uuid
from http import HTTPStatus

import pytest

pytestmark = pytest.mark.asyncio


@pytest.mark.parametrize(
    'es_data_len, expected_answer',
    [
        (
            26,
            {'status': HTTPStatus.OK, 'length': 26, 'cache': True, 'key': 'GenreService_get_list'},
        ),
        (
            0,
            {'status': HTTPStatus.NOT_FOUND, 'length': 1, 'cache': False, 'key': 'GenreService_get_list'},
        )
    ]
)
async def test_list_genres(es_write_data, get_data_from_cache, cleanup, make_get_request, es_data_len, expected_answer):
    es_data = [{
        'id': str(uuid.uuid4()),
        'name': f'Genre{i}',
        'description': f'Description{i}',
    } for i in range(es_data_len)]

    if es_data:
        await es_write_data(es_data, 'genres')

    status, body = await make_get_request('/genres/', {})

    cache = await get_data_from_cache(expected_answer['key'])

    await cleanup(['genres'])

    assert status == expected_answer['status']
    assert len(body) == expected_answer['length']
    assert bool(cache) == expected_answer['cache']


@pytest.mark.parametrize(
    'genre_id, expected_answer',
    [
        (
            'bccef253-1414-4d65-8b2e-5d5c8cb61d60',
            {
                'status': HTTPStatus.OK,
                'body': {
                    'uuid': 'bccef253-1414-4d65-8b2e-5d5c8cb61d60',
                    'name': 'Genre1',
                    'description': 'Description1',
                },
                'cache': True,
                'key': 'GenreService_get_by_id_bccef253-1414-4d65-8b2e-5d5c8cb61d60'
            },
        ),
        (
            'ae6740c4-f003-44f5-8c0f-495896aba433',
            {
                'status': HTTPStatus.NOT_FOUND,
                'body': {
                    "detail": "Genre not found."
                },
                'cache': False,
                'key': 'GenreService_get_by_id_ae6740c4-f003-44f5-8c0f-495896aba433'
            },
        )
    ]
)
async def test_get_genre_by_id(es_write_data, get_data_from_cache, cleanup, make_get_request, genre_id, expected_answer):
    es_data = [
        {
            'id': 'bccef253-1414-4d65-8b2e-5d5c8cb61d60',
            'name': 'Genre1',
            'description': 'Description1',
        },
        {
            'id': '7d7b1604-310b-4249-a97d-9419cfbc6801',
            'name': 'Genre2',
            'description': 'Description2',
        }
    ]

    if es_data:
        await es_write_data(es_data, 'genres')

    status, body = await make_get_request('/genres/' + genre_id, {})

    cache = await get_data_from_cache(expected_answer['key'])

    await cleanup(['genres'])

    assert status == expected_answer['status']
    assert body == expected_answer['body']
    assert bool(cache) == expected_answer['cache']
