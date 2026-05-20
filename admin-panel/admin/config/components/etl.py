import os


# Base URL of the ETL HTTP API used by the admin dashboard. Defaults to the
# docker-compose service name; override via env in deployments where the
# worker is reachable under a different host.
ETL_BASE_URL = os.environ.get('ETL_BASE_URL', 'http://etl:8000')
