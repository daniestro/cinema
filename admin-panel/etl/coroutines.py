from datetime import datetime
from typing import Generator, Union, Optional

from decorators import coroutine, backoff
from elastic import Elastic
from logger import logger
from movie_model import Movie, Person, Genre, GenreWithDesc
from state.state_storage import State


@coroutine
def fetch_changes(cursor, next_node: Generator, table_name: str, batch_size: int = 1000) \
        -> Generator[None, datetime, None]:
    """Корутина которая ищет измененные данные и
    отправляет в следующую корутину (кортеж id, последняя дата изменения, )"""
    while last_updated := (yield):
        logger.info(f'Fetching {table_name} changed after {last_updated}')
        sql = f'SELECT id, updated_at FROM content.{table_name} WHERE updated_at > %s order by updated_at asc'
        logger.info(f'Fetching {table_name} updated after {last_updated}')

        cursor.execute(sql, (last_updated,))
        while results := cursor.fetchmany(size=batch_size):
            ids = tuple(elem['id'] for elem in results)
            last_fetched_date = results[-1]['updated_at']
            next_node.send((ids, last_fetched_date, ))


@coroutine
@backoff()
def fetch_data(cursor, sql_query: str, next_node: Generator) -> Generator[None, tuple[tuple, str], None]:
    """Корутина которая достает информацию из бд и
        отправляет в следующую корутину (кортеж с данными из БД, последняя дата изменения, )"""
    while data := (yield):
        ids = data[0]

        placeholders = ','.join(['%s'] * len(ids))
        cursor.execute(sql_query.format(placeholders), ids)
        while results := cursor.fetchall():
            next_node.send((results, data[1]))


@coroutine
@backoff()
def transform_data(next_node: Generator, model: Union[GenreWithDesc, Person]) -> Generator[None, tuple[tuple, str], None]:
    """Корутина которая трансформирует список из бд в модель и
    отправляет в следующую корутину (список с моделями, последняя дата изменения, )"""
    while data := (yield):
        data_dicts = data[0]
        batch = []
        for data_dict in data_dicts:
            batch.append(model(**data_dict))

        next_node.send((batch, data[1]))


@coroutine
@backoff()
def save_data(state: State, state_key: str, elastic: Elastic, index: str, next_node: Optional[Generator] = None) \
        -> Generator[None, tuple[list[Union[Genre, Person, Movie]], str], None]:
    """Корутина которая сохраняет информацию о моделях,
    сохраняет state и передает данные в следующую корутину если указан next_node"""
    while data := (yield):
        models = data[0]

        logger.info(f'Received for saving {len(models)} {index}')
        result = elastic.bulk_post(index, models)
        logger.info(f'Elastic result: {result}')

        state.set_state(state_key, str(data[1]))
        if next_node is not None:
            next_node.send(([model.id for model in models], data[1]))


@coroutine
@backoff()
def fetch_movies_ids(cursor, next_node: Generator, table_name: str) \
        -> Generator[None, tuple[tuple, str], None]:
    """Корутина которая ищет id фильмов связанных с измененными person или genre и
    отправляет в следующую корутину (кортеж id фильмов, последняя дата изменения, )"""
    while data := (yield):
        ids = data[0]

        placeholders = ','.join(['%s'] * len(ids))
        sql = f"""
        SELECT DISTINCT * FROM(
            SELECT fw.id
            FROM content.film_work fw
            LEFT JOIN content.{table_name}_film_work {table_name}fw ON {table_name}fw.film_work_id = fw.id
            WHERE {table_name}fw.{table_name}_id IN ({placeholders})
            ORDER BY fw.updated_at) as t;
        """

        cursor.execute(sql, ids)
        while results := cursor.fetchall():
            movies_ids = tuple(elem['id'] for elem in results)
            next_node.send((movies_ids, data[1], ))


@coroutine
@backoff()
def transform_movies(next_node: Generator) -> Generator[None, tuple[tuple, str], None]:
    """Корутина которая трансформирует информацию о фильмах и
    отправляет в следующую корутину (список с трансформированными фильмами, последняя дата изменения, )"""
    while data := (yield):
        movie_dicts = data[0]
        batch = []
        for movie_dict in movie_dicts:
            movie_dict.update({
                'actors': [],
                'actors_names': [],
                'writers': [],
                'writers_names': [],
                'directors': [],
                'directors_names': [],
                'genre': [Genre(id=genre['genre_id'], name=genre['genre_name']) for genre in movie_dict['genres']]
            })

            for person in movie_dict['persons']:
                person_role = person['person_role']
                person_obj = Person(id=str(person['person_id']), full_name=person['person_name'])
                if person_role == 'actor':
                    movie_dict['actors'].append(person_obj)
                    movie_dict['actors_names'].append(person_obj.full_name)
                elif person_role == 'writer':
                    movie_dict['writers'].append(person_obj)
                    movie_dict['writers_names'].append(person_obj.full_name)
                elif person_role == 'director':
                    movie_dict['directors'].append(person_obj)
                    movie_dict['directors_names'].append(person_obj.full_name)

            del movie_dict['persons']
            del movie_dict['genres']

            poster_key = movie_dict.pop('poster', None)
            movie_dict['poster_url'] = f'/media/posters/{poster_key}' if poster_key else None

            movie = Movie(**movie_dict)
            movie.title = movie.title.upper()
            batch.append(movie)

        next_node.send((batch, data[1]))
