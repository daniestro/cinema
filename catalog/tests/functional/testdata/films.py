import uuid
import random


films_pool = [{
        'id': str(uuid.uuid4()),
        'imdb_rating': round(random.uniform(0, 10), 1),
        'genre': [{'id': str(uuid.uuid4()), 'name': 'Action'}],
        'title': 'The Star',
        'description': 'New World',
        'directors_names': [],
        'actors_names': [],
        'writers_names': [],
        'actors': [],
        'directors': [],
        'writers': []
    } for _ in range(100)]
