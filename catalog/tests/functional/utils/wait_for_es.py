from elasticsearch import Elasticsearch

from settings import test_settings
from utils.helpers import backoff


@backoff('elastic')
def elastic_connection(client: Elasticsearch):
    return client.ping()


if __name__ == '__main__':
    elastic_client = Elasticsearch(
        hosts=f'{test_settings.ELASTIC_HOST}:{test_settings.ELASTIC_PORT}',
        validate_cert=False,
        use_ssl=False
    )
    elastic_connection(elastic_client)
