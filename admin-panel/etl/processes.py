from elastic import Elastic
from coroutines import transform_movies, fetch_changes, fetch_movies_ids, fetch_data, \
    save_data, transform_data
from movie_model import Person, GenreWithDesc
from state.state_storage import State

SQL_QUERY_FOR_MOVIES = """
        SELECT
            fw.id, 
            fw.title, 
            fw.description, 
            fw.rating as imdb_rating,
            fw.poster,
            COALESCE (
               json_agg(
                   DISTINCT jsonb_build_object(
                       'person_role', pfw.role,
                       'person_id', p.id,
                       'person_name', p.full_name
                   )
               ) FILTER (WHERE p.id is not null),
               '[]'
           ) as persons,
           COALESCE (
               json_agg(
                   DISTINCT jsonb_build_object(
                       'genre_id', g.id,
                       'genre_name', g.name
                   )
               ) FILTER (WHERE g.id is not null),
               '[]'
           ) as genres
        FROM content.film_work fw
            LEFT JOIN content.person_film_work pfw ON pfw.film_work_id = fw.id
            LEFT JOIN content.person p ON p.id = pfw.person_id
            LEFT JOIN content.genre_film_work gfw ON gfw.film_work_id = fw.id
            LEFT JOIN content.genre g ON g.id = gfw.genre_id
        WHERE fw.id IN ({})
        GROUP BY fw.id;
        """


def etl_process_for_movies(state: State, elastic: Elastic, cursor):
    """Процесс по поиску измененных фильмов"""
    saver_coro = save_data(state, 'last_movies_updated', elastic, 'movies')
    transformer_coro = transform_movies(next_node=saver_coro)

    data_coro = fetch_data(cursor, SQL_QUERY_FOR_MOVIES[:], transformer_coro)

    return fetch_changes(cursor, data_coro, 'film_work')


def etl_process_for_persons(state_persons: State, state_movies: State, elastic: Elastic, cursor):
    """Процесс по поиску измененных сотрудников"""
    saver_coro = save_data(state_movies, 'last_movies_updated', elastic, 'movies')
    transformer_coro = transform_movies(next_node=saver_coro)
    data_coro = fetch_data(cursor, SQL_QUERY_FOR_MOVIES[:], transformer_coro)
    ids_coro = fetch_movies_ids(cursor, data_coro, 'person')

    saver_person_coro = save_data(state_persons, 'last_persons_updated', elastic, 'persons', ids_coro)
    transformer_person_coro = transform_data(next_node=saver_person_coro, model=Person)

    sql_query = """
        SELECT p.id, p.full_name 
        FROM content.person p 
        WHERE p.id IN ({})
        ORDER BY p.updated_at;
    """
    data_person_coro = fetch_data(cursor, sql_query, transformer_person_coro)

    return fetch_changes(cursor, data_person_coro, 'person')


def etl_process_for_genres(state_persons: State, state_movies: State, elastic: Elastic, cursor):
    """Процесс по поиску измененных жанров"""
    saver_coro = save_data(state_movies, 'last_movies_updated', elastic, 'movies')
    transformer_coro = transform_movies(next_node=saver_coro)
    data_coro = fetch_data(cursor, SQL_QUERY_FOR_MOVIES[:], transformer_coro)
    ids_coro = fetch_movies_ids(cursor, data_coro, 'genre')

    saver_genre_coro = save_data(state_persons, 'last_genres_updated', elastic, 'genres', ids_coro)
    transformer_genre_coro = transform_data(next_node=saver_genre_coro, model=GenreWithDesc)

    sql_query = """
        SELECT g.id, g.name, g.description  
        FROM content.genre g  
        WHERE g.id IN ({})
        ORDER BY g.updated_at;
    """
    data_genre_coro = fetch_data(cursor, sql_query, transformer_genre_coro)

    return fetch_changes(cursor, data_genre_coro, 'genre')
