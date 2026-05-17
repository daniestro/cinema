import uuid

PERSON_ID = '02a4ba21-290a-40ac-bd1a-b321e90f258e'
FILMS_IDS = ('8bc0f3de-7c0a-4cc9-a980-8d5a6142f5df', 'b019a663-b60b-40ed-b989-3742a0e9c111')

es_data_film = [
        {
            'id': FILMS_IDS[0],
            'imdb_rating': 10,
            'genre': [
                {'id': str(uuid.uuid4()), 'name': 'Sci-Fi'}
            ],
            'title': 'The Star 1',
            'description': 'New World 1',
            'directors_names': ['Stan'],
            'actors_names': ['Al Pacino', 'Bob'],
            'writers_names': ['Ben', 'Howard'],
            'actors': [
                {'id': PERSON_ID, 'full_name': 'Al Pacino'},
                {'id': str(uuid.uuid4()), 'full_name': 'Bob'}
            ],
            'directors': [
                {'id': str(uuid.uuid4()), 'full_name': 'Stan'}
            ],
            'writers': [
                {'id': str(uuid.uuid4()), 'full_name': 'Ben'},
                {'id': str(uuid.uuid4()), 'full_name': 'Howard'}
            ]
        },
        {
            'id': FILMS_IDS[1],
            'imdb_rating': 9,
            'genre': [
                {'id': str(uuid.uuid4()), 'name': 'Sci-Fi'}
            ],
            'title': 'The Star 2',
            'description': 'New World 2',
            'directors_names': ['Al Pacino'],
            'actors_names': ['Ann', 'Bob'],
            'writers_names': ['Al Pacino', 'Howard'],
            'actors': [
                {'id': str(uuid.uuid4()), 'full_name': 'Ann'},
                {'id': str(uuid.uuid4()), 'full_name': 'Bob'}
            ],
            'directors': [
                {'id': PERSON_ID, 'full_name': 'Al Pacino'}
            ],
            'writers': [
                {'id': PERSON_ID, 'full_name': 'Al Pacino'},
                {'id': str(uuid.uuid4()), 'full_name': 'Howard'}
            ]
        }
    ]
es_data_person = [
        {
            'id': PERSON_ID,
            'full_name': 'Al Pacino'
        },
        {
            'id': str(uuid.uuid4()),
            'full_name': 'Chuck Norris'
        }
    ]
