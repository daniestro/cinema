import uuid
import random

import pytest
from http import HTTPStatus

from ..testdata.films import films_pool


pytestmark = pytest.mark.asyncio


@pytest.mark.parametrize(
    'film_id, expected_answer',
    [
        (
                'bccef253-1414-4d65-8b2e-5d5c8cb61d60',
                {
                    'status': HTTPStatus.OK,
                    'body': {
                        'uuid': 'bccef253-1414-4d65-8b2e-5d5c8cb61d60',
                        'title': 'The Star',
                        'imdb_rating': 8.5,
                        'description': 'New World',
                        'genre': [{'uuid': 'bccef253-1414-4d65-8b2e-5d5c8cb61d60', 'name': 'Action'}],
                        'actors': [],
                        'directors': [],
                        'writers': []
                    },
                    'cache_key': 'FilmService_get_by_id_bccef253-1414-4d65-8b2e-5d5c8cb61d60'
                },
        ),
    ]
)
async def test_get_film_by_id(es_write_data, get_data_from_cache, cleanup,
                              make_get_request, film_id, expected_answer):
    await es_write_data([
        {
            'id': 'bccef253-1414-4d65-8b2e-5d5c8cb61d60',
            'title': 'The Star',
            'imdb_rating': 8.5,
            'description': 'New World',
            'genre': [{'id': 'bccef253-1414-4d65-8b2e-5d5c8cb61d60', 'name': 'Action'}],
            'directors_names': [],
            'actors_names': [],
            'writers_names': [],
            'actors': [],
            'directors': [],
            'writers': []
        }
    ], 'movies')

    status, body = await make_get_request('/films/' + film_id, {})
    cache = await get_data_from_cache(expected_answer['cache_key'])

    await cleanup(['movies'])

    assert status == expected_answer['status']
    assert body == expected_answer['body']
    assert cache == body


@pytest.mark.parametrize(
    'film_id, expected_answer',
    [
        (
                'ae6740c4-f003-44f5-8c0f-495896aba433',
                {
                    'status': HTTPStatus.NOT_FOUND,
                    'body': {"detail": "Film not found."},
                    'cache_key': 'GenreService_get_by_id_ae6740c4-f003-44f5-8c0f-495896aba433'
                },
        )
    ]
)
async def test_not_found_get_film_by_id(get_data_from_cache,  make_get_request,
                                        cleanup, film_id, expected_answer):
    status, body = await make_get_request('/films/' + film_id, {})
    cache = await get_data_from_cache(expected_answer['cache_key'])

    await cleanup(['movies'])

    assert status == expected_answer['status']
    assert body == expected_answer['body']
    assert bool(cache) is False


@pytest.mark.parametrize(
    'genre_id, expected_answer',
    [
        (
            films_pool[0]['genre'][0]['id'],
            {
                'status': HTTPStatus.OK,
                'body': [{
                    'uuid': films_pool[0]['id'],
                    'title': 'The Star',
                    'imdb_rating': films_pool[0]['imdb_rating']
                }]
            }
        ),
        (
            str(uuid.uuid4()),
            {
                'status': HTTPStatus.NOT_FOUND,
                'body': {"detail": "Films not found."}
            }
        )
    ]
)
async def test_films_get_by_genre_id(es_write_data, cleanup, make_get_request, genre_id, expected_answer):
    films = films_pool[:10]

    await es_write_data(films, 'movies')

    status, body = await make_get_request('/films/', {'genre': genre_id})

    await cleanup(['movies'])

    assert status == expected_answer['status']
    assert body == expected_answer['body']


@pytest.mark.parametrize(
    'sort, expected_answer',
    [
        (
            'imdb_rating',
            {'status': HTTPStatus.OK}
        ),
        (
            '-imdb_rating',
            {'status': HTTPStatus.OK}
        )
    ]
)
async def test_films_sort(es_write_data, cleanup, make_get_request, sort, expected_answer):
    films = films_pool[:10]

    await es_write_data(films, 'movies')

    status, body = await make_get_request('/films/', {'sort': sort})

    await cleanup(['movies'])

    sort_flag = True
    previous = body[0]['imdb_rating']
    for film in body[1:]:
        if sort == 'imdb_rating':
            if film['imdb_rating'] < previous:
                sort_flag = False
                break
        else:
            if film['imdb_rating'] > previous:
                sort_flag = False
                break
        previous = film['imdb_rating']

    assert status == expected_answer['status']
    assert sort_flag


@pytest.mark.parametrize(
    'query_data, expected_data',
    [
        (
            {
                'genre': str(uuid.uuid4()),
                'sort': 'imdb_rating',
                'page_number': 1,
                'page_size': 10
            },
            {
                'status': HTTPStatus.OK,
                'length': 10,
            }
        ),
        (
            {
                'genre': str(uuid.uuid4()),
                'sort': 'imdb_rating',
                'page_number': 2,
                'page_size': 10
            },
            {
                'status': HTTPStatus.OK,
                'length': 8,
            }
        )
    ]
)
async def test_films_all_params(es_write_data, cleanup, make_get_request,
                                get_data_from_cache, query_data, expected_data):
    genre_films = [{
        'id': str(uuid.uuid4()),
        'imdb_rating': round(random.uniform(0, 10), 1),
        'genre': [{'id': query_data['genre'], 'name': 'Action'}],
        'title': 'The Star',
        'description': 'New World',
        'directors_names': [],
        'actors_names': [],
        'writers_names': [],
        'actors': [],
        'directors': [],
        'writers': []
    } for _ in range(18)]

    await es_write_data(genre_films + films_pool[:20], 'movies')

    status, body = await make_get_request('/films/', query_data)

    sort_choise = 'Choises.first' if query_data['sort'] == 'imdb_rating' else 'Choises.second'
    key = f"FilmService_get_list_{query_data['genre']}_None_" \
          f"{sort_choise}_{query_data['page_number']}_{query_data['page_size']}"

    cache = await get_data_from_cache(key)

    await cleanup(['movies'])

    assert status == expected_data['status']
    assert len(body) == expected_data['length']
    assert cache == body


@pytest.mark.parametrize(
    'query_data, expected_data',
    [
        (
            {
                'genre': str(uuid.uuid4()),
                'sort': 'imdb_rating',
                'page_number': 1,
                'page_size': 10
            },
            {
                'status': HTTPStatus.NOT_FOUND,
                'body': {"detail": "Films not found."}
            }
        )
    ]
)
async def test_films_not_found_all_params(es_write_data, cleanup, make_get_request,
                                          get_data_from_cache, query_data, expected_data):
    status, body = await make_get_request('/films/', query_data)

    sort_choise = 'Choises.first' if query_data['sort'] == 'imdb_rating' else 'Choises.second'
    key = f"FilmService_get_list_{query_data['genre']}_None_" \
          f"{sort_choise}_{query_data['page_number']}_{query_data['page_size']}"

    cache = await get_data_from_cache(key)

    await cleanup(['movies'])

    assert status == expected_data['status']
    assert body == expected_data['body']
    assert bool(cache) is False


@pytest.mark.parametrize(
    'query, expected_data',
    [
        (
            'Movie',
            {
                'status': HTTPStatus.OK,
                'length': 5
            }
        )
    ]
)
async def test_films_search_get_by_query(es_write_data, cleanup, make_get_request, query, expected_data):
    part1 = films_pool[:10]

    part2 = [
        {
            'id': str(uuid.uuid4()),
            'imdb_rating': 0,
            'genre': [{'id': str(uuid.uuid4()), 'name': 'Action'}],
            'title': query,
            'description': 'New World',
            'directors_names': [],
            'actors_names': [],
            'writers_names': [],
            'actors': [],
            'directors': [],
            'writers': []
        } for _ in range(5)
    ]

    await es_write_data(part1 + part2, 'movies')

    status, body = await make_get_request('/films/search/', {'query': query})

    await cleanup(['movies'])

    search_flag = True
    for film in body:
        if query not in film['title']:
            search_flag = False
            break

    assert status == expected_data['status']
    assert len(body) == expected_data['length']
    assert search_flag


@pytest.mark.parametrize(
    'query, expected_data',
    [
        (
            'Movie',
            {
                'status': HTTPStatus.NOT_FOUND,
                'body': {"detail": "Films not found."}
            }
        )
    ]
)
async def test_films_search_get_by_query(es_write_data, make_get_request,
                                         cleanup, query, expected_data):
    status, body = await make_get_request('/films/search/', {'query': query})

    await cleanup(['movies'])

    assert status == expected_data['status']
    assert body == expected_data['body']


@pytest.mark.parametrize(
    'sort, expected_answer',
    [
        (
            'imdb_rating',
            {'status': HTTPStatus.OK}
        ),
        (
            '-imdb_rating',
            {'status': HTTPStatus.OK}
        )
    ]
)
async def test_films_search_sort(es_write_data, cleanup, make_get_request, sort, expected_answer):
    films = films_pool[:10]

    await es_write_data(films, 'movies')

    status, body = await make_get_request('/films/search/', {'sort': sort})

    await cleanup(['movies'])

    sort_flag = True
    previous = body[0]['imdb_rating']
    for film in body[1:]:
        if sort == 'imdb_rating':
            if film['imdb_rating'] < previous:
                sort_flag = False
                break
        else:
            if film['imdb_rating'] > previous:
                sort_flag = False
                break
        previous = film['imdb_rating']

    assert status == expected_answer['status']
    assert sort_flag


@pytest.mark.parametrize(
    'query, expected_data',
    [
        (
            {
                'query': 'Movie',
                'sort': 'imdb_rating',
                'page_number': 1,
                'page_size': 5
            },
            {
                'status': HTTPStatus.OK,
                'length': 5
            }
        ),
        (
            {
                'query': 'Star',
                'sort': '-imdb_rating',
                'page_number': 2,
                'page_size': 5
            },
            {
                'status': HTTPStatus.OK,
                'length': 5
            }
        )
    ]
)
async def test_films_search_all_params(es_write_data, cleanup, make_get_request,
                                       get_data_from_cache, query, expected_data):
    part1 = films_pool[:10]

    part2 = [
        {
            'id': str(uuid.uuid4()),
            'imdb_rating': round(random.uniform(0, 10), 1),
            'genre': [{'id': str(uuid.uuid4()), 'name': 'Action'}],
            'title': query['query'],
            'description': 'New World',
            'directors_names': [],
            'actors_names': [],
            'writers_names': [],
            'actors': [],
            'directors': [],
            'writers': []
        } for _ in range(5)
    ]

    await es_write_data(part1 + part2, 'movies')

    status, body = await make_get_request('/films/search/', query)

    sort_choise = 'Choises.first' if query['sort'] == 'imdb_rating' else 'Choises.second'
    key = f"FilmService_get_list_None_{query['query']}_{sort_choise}" \
          f"_{query['page_number']}_{query['page_size']}"

    cache = await get_data_from_cache(key)

    await cleanup(['movies'])

    assert status == expected_data['status']
    assert len(body) == expected_data['length']
    assert cache == body


@pytest.mark.parametrize(
    'query, expected_data',
    [
        (
            {
                'query': 'Movie',
                'sort': 'imdb_rating',
                'page_number': 2,
                'page_size': 5
            },
            {
                'status': HTTPStatus.NOT_FOUND,
                'body': {"detail": "Films not found."}
            }
        )
    ]
)
async def test_films_non_found_search_all_params(cleanup, make_get_request,
                                                 get_data_from_cache, query,
                                                 expected_data):
    status, body = await make_get_request('/films/search/', query)

    sort_choise = 'Choises.first' if query['sort'] == 'imdb_rating' else 'Choises.second'
    key = f"FilmService_get_list_None_{query['query']}_{sort_choise}" \
          f"_{query['page_number']}_{query['page_size']}"

    cache = await get_data_from_cache(key)

    await cleanup(['movies'])

    assert status == expected_data['status']
    assert body == expected_data['body']
    assert bool(cache) is False
