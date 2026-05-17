from http import HTTPStatus

# Параметры для теста test_validation.test_person_search_validation
# 'query_data, expected_answer, endpoint'

pagination_params = []
for elem in ['/persons/search/', '/films/', '/films/search/']:
    pagination_params.extend([
        (
            {
                'page_size': 0,
                'page_number': 0
            },
            {
                'status': HTTPStatus.UNPROCESSABLE_ENTITY,
                'body': {
                    "detail": [
                        {
                            "ctx": {
                                "limit_value": 1
                            },
                            "loc": [
                                "query",
                                "page_size"
                            ],
                            "msg": "ensure this value is greater than or equal to 1",
                            "type": "value_error.number.not_ge"
                        },
                        {
                            "ctx": {
                                "limit_value": 1
                            },
                            "loc": [
                                "query",
                                "page_number"
                            ],
                            "msg": "ensure this value is greater than or equal to 1",
                            "type": "value_error.number.not_ge"
                        }
                    ]
                }
            },
            elem
        ),
        (
            {
                'page_size': 101,
                'page_number': 1
            },
            {
                'status': HTTPStatus.UNPROCESSABLE_ENTITY,
                'body': {
                    "detail": [
                        {
                            "ctx": {
                                "limit_value": 100
                            },
                            "loc": [
                                "query",
                                "page_size"
                            ],
                            "msg": "ensure this value is less than or equal to 100",
                            "type": "value_error.number.not_le"
                        }
                    ]
                }
            },
            elem
        )
    ])

    # В /films/ и /films/search/ есть параметр sort
    if elem != '/persons/search/':
        pagination_params.append(
            (
                {'sort': 'string', 'page_size': 20, 'page_number': 1},
                {
                    "status": HTTPStatus.UNPROCESSABLE_ENTITY,
                    "body": {
                        "detail": [
                            {
                                "loc": [
                                    "query",
                                    "sort"
                                    ],
                                "msg": "value is not a valid enumeration member; permitted: 'imdb_rating', '-imdb_rating'",
                                "type": "type_error.enum",
                                "ctx": {
                                    "enum_values": [
                                        "imdb_rating",
                                        "-imdb_rating"
                                    ]
                                }
                            }
                        ]
                    }
                },
                elem
            )
        )

    # В /films/ есть параметр сортировки по genre_id
    if elem == '/films/':
        pagination_params.append(
            (
                {'genre': 'string', 'page_size': 20, 'page_number': 1},
                {
                    'status': HTTPStatus.UNPROCESSABLE_ENTITY,
                    'body': {
                        "detail": [
                            {
                                "loc": [
                                    "query",
                                    "genre"
                                    ],
                                "msg": "value is not a valid uuid",
                                "type": "type_error.uuid"
                            }
                        ]
                    }
                },
                elem
            ),
        )
