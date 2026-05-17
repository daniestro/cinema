# catalog — read-only films / genres / persons API

## Purpose

This service is the **public read path** of the cinema catalog. It does one thing: serves film, genre, and person data over HTTP, fast, to end users.

- It **does not write** anything. The source of truth is Postgres, owned by `admin-panel/`. The `admin-panel/etl/` worker replicates that data into Elasticsearch indices, and this service reads from those indices.
- It **does not issue tokens**. JWT signing is the responsibility of `auth/`. This service only **verifies** tokens using the public RSA key, mounted as a read-only Docker secret.
- It **caches** every successful response in Redis with a short TTL so repeated requests skip Elasticsearch entirely.

That's the whole contract: read from ES, verify the bearer token, cache the result, return JSON.

## Quick start

### 1. Prerequisites

This service depends on two siblings being available on the host:

- **`auth/`** — must have been started at least once so that `../auth/keys/rsa.pub` exists. The compose file mounts it as a Docker secret.
- **`admin-panel/`** — owns the Elasticsearch container that this service reads from. The `etl_network` is created by `admin-panel/`'s compose. Start it before catalog, otherwise `docker compose up` will fail with `network etl_network not found`.

The shared `cinema_net` must also exist (created once with `docker network create cinema_net`).

### 2. Configure environment

```bash
cp .env.example .env
$EDITOR .env       # defaults are fine for a local stand
```

The variables are limited to host/port wiring — there are no secrets here.

### 3. Bring up the stack

```bash
docker compose up -d
```

This starts three containers:

- `movies-api` — the FastAPI app, exposed only on the internal `etl_network` and `cinema_net` (no host port — reach it through the gateway).
- `movies-redis` — Redis 7, configured as a pure cache (LRU eviction at 80mb, no persistence; see `command:` in the compose file).
- `jaeger` — all-in-one Jaeger for trace visualization, UI on host port `16686`.

### 4. Verify

```bash
# via the cinema gateway (recommended)
curl -H 'X-Request-Id: smoke' http://localhost/content/api/openapi.json | head -c 200

# Swagger UI
open http://localhost/content/api/openapi
```

All real endpoints require a Bearer JWT — get one from `auth/` first (e.g. `POST /auth/api/v1/auth/login`).

## What the deployed service provides

### HTTP API (`/api/v1/*`)

All endpoints are mounted under `root_path=/content` (set via `PROJECT_ROOT_URL` in compose), so the public-facing URLs go through the gateway at `http://localhost/content/...`.

| Path | Module | Returns |
|---|---|---|
| `GET /api/v1/films/` | `api/v1/films.py` | List of films; supports `sort` (by rating), `genre` filter, pagination (`page_size`, `page_number`) |
| `GET /api/v1/films/search/` | `api/v1/films.py` | Full-text search over films |
| `GET /api/v1/films/{uuid}` | `api/v1/films.py` | Single film detail |
| `GET /api/v1/genres/` | `api/v1/genres.py` | List of genres (paginated) |
| `GET /api/v1/genres/{uuid}` | `api/v1/genres.py` | Single genre detail |
| `GET /api/v1/persons/` | `api/v1/persons.py` | Persons (paginated, searchable) |
| `GET /api/v1/persons/{uuid}` | `api/v1/persons.py` | Single person detail |
| `GET /api/v1/persons/{uuid}/film/` | `api/v1/persons.py` | All films that this person took part in |

**Every endpoint requires:**

- `Authorization: Bearer <jwt>` — a token signed by `auth/` with RS256. Verification uses `/run/secrets/rsa_public`.
- `X-Request-Id: <id>` — enforced by middleware. Requests without it get `400 Bad Request`. The cinema gateway adds this header automatically.

**Rate limit:** 20 requests per minute per client IP, via `slowapi` (in-memory limiter). Exceeding the limit returns `429 Too Many Requests`.

### Caching

Every successful response is cached in Redis (`movies-redis`) for `REDIS_CACHE_EXP_SECS` seconds (300 by default). Cache keys are derived from the endpoint, path params, and query string — so the same `/films/?genre=action&page_size=10` request hits Redis on the second call.

The cache is **ephemeral by design**: no AOF, no RDB. On restart the cache is empty and rebuilds itself from ES on demand. This matches the role — durable storage of cache contents would just chew disk for no benefit.

### Tracing

When the container has `jaeger_agent_host_name` reachable, OpenTelemetry exports spans to Jaeger via the Thrift agent on UDP 6831. View traces at <http://localhost:16686>.

## Tests

The project ships **functional black-box tests** that spin up a parallel stack (api + ES + Redis) and hit the API over HTTP.

### Layout

```
tests/functional/
├── docker-compose.yml      ← test-only stack (api + ES + Redis + tests sidecar)
├── Dockerfile              ← image used by the tests sidecar
├── requirements.txt        ← pytest, aiohttp, etc.
├── conftest.py             ← session-level fixtures
├── settings.py             ← test-suite config (hosts/ports)
├── fixtures/               ← reusable pytest fixtures (http session, ES data seeding)
├── testdata/               ← canned request/response bodies + ES mappings
├── utils/wait_for_es.py    ← readiness gate
└── src/                    ← actual test modules: test_film, test_genre, test_person, test_validation
```

### Run

```bash
cd tests/functional
docker compose up --build --abort-on-container-exit
docker compose down -v
```

The sidecar container (`movies-tests`) executes `pytest tests/functional/src` against the freshly-started API. Exit code propagates from pytest. Volumes are dropped on `down -v` so each run starts from a clean ES index.

There are **no unit tests** at the moment — only the functional layer.

## Project structure

```
catalog/
├── docker-compose.yml      ← api + redis + jaeger
├── Dockerfile              ← Python 3.9 + gunicorn(uvicorn worker)
├── requirements.txt        ← pinned direct deps
├── .env.example
├── src/
│   ├── main.py             ← FastAPI app, lifespan, tracing, middleware, router include
│   ├── limiter.py          ← slowapi limiter instance
│   ├── api/
│   │   ├── v1/{films,genres,persons}.py
│   │   └── __init__.py
│   ├── core/
│   │   ├── config.py       ← pydantic Settings
│   │   ├── exceptions.py
│   │   └── logger.py
│   ├── db/
│   │   ├── elastic.py      ← AsyncElasticsearch singleton
│   │   └── redis.py        ← Redis singleton
│   ├── models/             ← pydantic response models + query validators
│   └── services/
│       ├── abstract.py     ← BaseService interface
│       ├── auth.py         ← JWT verification (RS256, reads public key from secret)
│       ├── film.py, genres.py, persons.py   ← per-entity service classes
│       └── common.py
└── tests/functional/       ← see Tests section
```

## Architecture

The service is a thin **FastAPI → Elasticsearch** read path with a Redis cache in front. The interesting parts are how it fits into the rest of the cinema.

**Where the data comes from.** This service never owns data. Editors write films/genres/persons in Django admin (`admin-panel/`), which persists to Postgres. The `admin-panel/etl/` worker reads new and changed rows from Postgres and bulk-indexes them into Elasticsearch. This service connects to that same Elasticsearch over the shared `etl_network` and reads only — it has no credentials or code path that could mutate the indices.

**Request flow.** A request lands on the cinema gateway (`http://localhost/content/...`), which adds `X-Request-Id` and proxies to `movies-api:8000` over `cinema_net`. Middleware enforces presence of `X-Request-Id` and passes the trace ID to OpenTelemetry. The router invokes `security_jwt`, which fetches the bearer token and verifies its RS256 signature with the public key auth issued; failures return 401/403. On success the endpoint computes a cache key, looks it up in Redis, and either returns the cached JSON or queries Elasticsearch, caches the result, and returns it.

**Trust model.** The service has no shared secret with `auth/`. It only has the **public** half of the RSA key pair (mounted as Docker secret `rsa_public`, file source `../auth/keys/rsa.pub`). If `auth/` rotates its key, every dependent service — including this one — must restart to pick up the new public key.

**Why Redis is configured as a pure cache.** The compose `command:` enforces `maxmemory 80mb`, `maxmemory-policy allkeys-lru`, `--save ""`, `--appendonly no`. On memory pressure Redis evicts the least-recently-used keys; on restart everything is gone. This is the right shape for a query cache: durability would be wasted (the data is rebuildable from ES) and unbounded growth would OOM the container against its 96mb cgroup limit.

**Rate limiting caveat.** `slowapi` uses `request.client.host` to identify clients. Behind the gateway, that becomes the gateway's container IP, not the real client. If you need accurate per-client limits, configure the gateway to forward `X-Forwarded-For` and switch `slowapi` to a key function that reads from it.

## Integration with the cinema stack

- **Networks.** `movies-api` joins three networks: `etl_network` (to reach the Elasticsearch container owned by `admin-panel/`), `cinema_net` (so the gateway and other services can reach it by container name), and the private `jaeger_net` (only for the tracing sidecar). All three external prerequisites must exist before `docker compose up`:

  ```bash
  docker network create cinema_net          # one-time, shared
  docker compose -f ../admin-panel/docker-compose.yml up -d   # creates etl_network and ES
  ```

- **Public entrypoint.** There is no nginx in this stack. The single cinema gateway at `cinema/gateway/` (host port `80`) proxies `/content/*` → `movies-api:8000`. Because the app is configured with `root_path=/content`, Swagger UI and OpenAPI links work end-to-end through the prefix.

- **RSA key sharing.** The `rsa_public` Docker secret is sourced from `../auth/keys/rsa.pub`. The compose file uses a relative path that assumes `catalog/` and `auth/` live as siblings, exactly as they do in this repository.

- **Bring-up order.** From the `cinema/` directory: `make admin && make auth && make catalog`, or `make read-stack` to bring up the whole read path (auth + admin + catalog) at once.

- **Direct host access.** There is no `ports:` block on `movies-api` on purpose — the only way in from outside Docker is through the gateway. Jaeger UI is the exception (port `16686:16686`) since you usually want to look at traces from your browser.

## URLs at a glance

| What | URL |
|---|---|
| Swagger UI (via gateway) | <http://localhost/content/api/openapi> |
| OpenAPI JSON (via gateway) | <http://localhost/content/api/openapi.json> |
| Jaeger UI | <http://localhost:16686> |
