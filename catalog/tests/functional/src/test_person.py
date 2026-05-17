from http import HTTPStatus

import pytest

from ..testdata.persons import es_data_person, es_data_film, PERSON_ID, FILMS_IDS

pytestmark = pytest.mark.asyncio


@pytest.mark.parametrize(
    'query_data, expected_answer',
    [
        (
                {
                    'query': 'Al Pacino',
                    'page_size': 100,
                    'page_number': 1
                },
                {
                    'status': HTTPStatus.OK,
                    'body': [
                        {
                            "uuid": PERSON_ID,
                            "full_name": "Al Pacino",
                            "films": [
                                {"uuid": FILMS_IDS[1], "roles": ["writer", "director"]},
                                {"uuid": FILMS_IDS[0], "roles": ["actor"]}
                            ]
                        }
                    ],
                    'cache': [
                        {
                            "uuid": PERSON_ID,
                            "full_name": "Al Pacino",
                            "films": [
                                {"uuid": FILMS_IDS[1], "roles": ["writer", "director"]},
                                {"uuid": FILMS_IDS[0], "roles": ["actor"]}
                            ]
                        }
                    ],
                    'key': 'PersonService_get_list_None_Al Pacino_1_100'
                }
        ),
        (
                {
                    'query': 'Robert De Niro',
                    'page_size': 100,
                    'page_number': 1
                },
                {
                    'status': HTTPStatus.NOT_FOUND,
                    'body': {
                        "detail": "Person not found."
                    },
                    'cache': None,
                    'key': 'PersonService_get_list_None_Robert De Niro_1_100'}
        )
    ]
)
async def test_person_search(es_write_data, get_data_from_cache, make_get_request, cleanup, query_data,
                             expected_answer):
    await es_write_data(es_data_film, 'movies')
    await es_write_data(es_data_person, 'persons')

    status, body = await make_get_request('/persons/search/', query_data)

    cache = await get_data_from_cache(expected_answer['key'])

    await cleanup(['movies', 'persons'])

    assert status == expected_answer['status']
    assert body == expected_answer['body']
    assert cache == expected_answer['cache']


@pytest.mark.parametrize(
    'person_id, expected_answer',
    [
        (
                PERSON_ID,
                {
                    'status': HTTPStatus.OK,
                    'body': [
                        {
                            "uuid": FILMS_IDS[1],
                            "title": "The Star 2",
                            "imdb_rating": 9
                        },
                        {
                            "uuid": FILMS_IDS[0],
                            "title": "The Star 1",
                            "imdb_rating": 10.0
                        }
                    ],
                    'cache': [
                        {
                            "uuid": FILMS_IDS[1],
                            "title": "The Star 2",
                            "imdb_rating": 9
                        },
                        {
                            "uuid": FILMS_IDS[0],
                            "title": "The Star 1",
                            "imdb_rating": 10.0
                        }
                    ],
                    'key': f'PersonService_get_list_{PERSON_ID}_None_None_None'
                }
        ),
        (
                '32c4d77c-aec9-4b6e-a300-3c2432916a7a',
                {
                    'status': HTTPStatus.NOT_FOUND,
                    'body': {
                        "detail": "Films not found."
                    },
                    'cache': None,
                    'key': f'PersonService_get_list_32c4d77c-aec9-4b6e-a300-3c2432916a7a_None_None_None'}
        )
    ]
)
async def test_person_films(es_write_data, get_data_from_cache, make_get_request, cleanup, person_id, expected_answer):
    await es_write_data(es_data_film, 'movies')
    await es_write_data(es_data_person, 'persons')

    status, body = await make_get_request(f'/persons/{person_id}/film', {})

    cache = await get_data_from_cache(expected_answer['key'])

    await cleanup(['movies', 'persons'])

    assert status == expected_answer['status']
    assert body == expected_answer['body']
    assert cache == expected_answer['cache']


@pytest.mark.parametrize(
    'person_id, expected_answer',
    [
        (
                PERSON_ID,
                {
                    'status': HTTPStatus.OK,
                    'body': {
                        "uuid": PERSON_ID,
                        "full_name": "Al Pacino",
                        "films": [
                            {"uuid": FILMS_IDS[1], "roles": ["writer", "director"]},
                            {"uuid": FILMS_IDS[0], "roles": ["actor"]}
                        ]
                    },
                    'cache': {
                        "uuid": PERSON_ID,
                        "full_name": "Al Pacino",
                        "films": [
                            {"uuid": FILMS_IDS[1], "roles": ["writer", "director"]},
                            {"uuid": FILMS_IDS[0], "roles": ["actor"]}
                        ]
                    },
                    'key': f'PersonService_get_by_id_{PERSON_ID}'
                }
        ),
        (
                '32c4d77c-aec9-4b6e-a300-3c2432916a7a',
                {
                    'status': HTTPStatus.NOT_FOUND,
                    'body': {
                        "detail": "Person not found."
                    },
                    'cache': None,
                    'key': f'PersonService_get_by_id_32c4d77c-aec9-4b6e-a300-3c2432916a7a'}
        )
    ]
)
async def test_get_person_by_id(es_write_data, get_data_from_cache, make_get_request, cleanup, person_id,
                                expected_answer):
    await es_write_data(es_data_film, 'movies')
    await es_write_data(es_data_person, 'persons')

    status, body = await make_get_request(f'/persons/{person_id}', {})

    cache = await get_data_from_cache(expected_answer['key'])

    await cleanup(['movies', 'persons'])

    assert status == expected_answer['status']
    assert body == expected_answer['body']
    assert cache == expected_answer['cache']
