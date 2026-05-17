# admin-panel — Django admin & ETL (Postgres → Elasticsearch)

## Purpose

This service is the **content management layer** of the cinema project. It is responsible for two things:

1. **Django admin** (`admin/`) — the editorial UI where staff create and edit films, genres, and persons. Postgres 13 is the source of truth for all content metadata.
2. **ETL** (`etl/`) — a Python worker that continuously reads new and updated rows from Postgres and indexes them into **Elasticsearch 8.11.0**, so that the read-only `content-api` service can serve fast search/filter queries to end users.

In other words: editors write to Postgres through Django; ETL replicates that data into Elasticsearch; `content-api` reads from Elasticsearch. This service owns the **write path**.

## Quick start

### 1. Configure environment

Copy the template and fill in the values:

```bash
cp .env.example .env
```

Required variables:

| Variable | Purpose | Typical value |
|---|---|---|
| `DB_NAME` | Postgres database name | `movies_database` |
| `DB_USER` | Postgres user | `app` |
| `DB_PASSWORD` | Postgres password | — |
| `DB_HOST` | Postgres host (use `postgres` inside Docker, `localhost` for local ETL) | `postgres` |
| `DB_PORT` | Postgres port inside the Docker network | `5432` |
| `ES_HOST` | Elasticsearch host | `elasticsearch` |
| `ES_PORT` | Elasticsearch port | `9200` |
| `DISCOVERY_TYPE` | ES cluster discovery mode | `single-node` |
| `XPACK_SECURITY_ENABLED` | ES security toggle | `false` |

### 2. Bring up the stack

```bash
docker compose up -d
```

This starts four containers:

- `postgres-etl` — Postgres 13, seeded from `etl/utils/dump.sql` on first boot; exposed on host port **5433** (remapped from container's `5432` to avoid clashing with `notifications/`'s Postgres).
- `elastic` — Elasticsearch 8.11.0, exposed on `${ES_PORT}`.
- `movies-admin` — Django admin app, exposed only on the internal Docker network on port `8000`.
- `etl` — the ETL worker, no exposed ports.

### 3. Run the ETL locally (optional)

If you prefer to iterate on the ETL outside Docker, start only the data containers and run the worker on the host:

```bash
docker compose up -d postgres elasticsearch
cd etl
python main.py
```

Set `DB_HOST=localhost` and `DB_PORT=5433` in your `.env` for this mode.

### 4. Reset the search index

To reindex everything from scratch (e.g., after schema changes):

```bash
# 1. Drop the Elasticsearch index
curl -X DELETE http://localhost:9200/movies

# 2. Remove ETL checkpoint files so the worker re-reads all rows
rm etl/state/state_*.json

# 3. Restart the ETL container (or rerun python main.py)
docker compose restart etl
```

This does **not** touch Postgres — content metadata is safe; only the derived search index is rebuilt.

### 5. Tests

A Postman collection for smoke-testing the indexed data lives at `etl/utils/postman_tests.json`.

## What the deployed app provides

### Django admin

- **URL (standalone):** `http://localhost:8000/admin/` (only accessible if you bind `movies-admin` to a host port; by default it is reachable only through the gateway — see below)
- **URL (via cinema gateway):** `http://localhost/admin/movies/`
- Models: `Filmwork`, `Genre`, `Person`, plus the M2M tables linking them.
- Static and media files are served from the named volumes `movies_static_volume` and `movies_media_volume`, which the cinema-wide gateway mounts as read-only to serve `/admin/movies/static/*` and `/admin/movies/media/*`.

### Elasticsearch

- **URL:** `http://localhost:${ES_PORT}` (default `9200`)
- **Index produced by ETL:** `movies`
- **Schema:** `etl/es_schema.json` (mappings & analyzers for full-text search over films).
- Consumed by `content-api` (sibling service) for the public `/api/v1/films` endpoints.

### Postgres

- **Host port:** `5433` → container `5432`
- **Container name:** `postgres-etl`
- Seeded once from `etl/utils/dump.sql` on the first container start. Subsequent boots reuse the volume at `~/postgresql/data` on the host.

## Project structure

```
admin-panel/
├── admin/                 ← Django project
│   ├── manage.py
│   ├── config/            ← settings package (split into config/components/*)
│   ├── movies/            ← Django app: models, admin, migrations, locale
│   ├── requirements.txt
│   └── Dockerfile
├── etl/                   ← ETL worker
│   ├── main.py            ← entrypoint loop
│   ├── coroutines.py      ← producer / enricher / merger / loader pipeline
│   ├── elastic.py         ← ES client wrapper
│   ├── es_schema.json     ← target index mapping
│   ├── movie_model.py     ← pydantic models for transformed rows
│   ├── processes.py       ← orchestration of pipeline tasks
│   ├── state/             ← per-stream checkpoint files (state_*.json)
│   ├── utils/
│   │   ├── dump.sql       ← initial Postgres seed
│   │   └── postman_tests.json
│   └── Dockerfile
├── docker-compose.yml
└── .env.example
```

## Architecture

The system follows a classic **write-path / read-path split**, with this service owning the write path end-to-end.

**Write path.** Staff editors log into Django admin (`movies-admin`), which persists every change to Postgres (`postgres-etl`) via the ORM. Postgres is the single source of truth — nothing else in the cinema writes to film metadata.

**Replication to search.** The `etl` worker runs continuously alongside the database. On each tick it asks Postgres for rows whose `modified` timestamp is newer than the last checkpoint it processed, transforms them, and bulk-indexes the result into the `movies` index in Elasticsearch.

**Read path.** A sibling service, `content-api`, never touches Postgres — it serves all public film queries directly from the Elasticsearch index that this ETL produces. This separation is what lets the read API stay fast and horizontally scalable while the admin remains a regular transactional Django app.

**Key properties of the ETL worker:**

- **Incremental and resumable.** Each stream (films, genres, persons) maintains its own `state_*.json` checkpoint under `etl/state/`, storing the `modified` timestamp of the last row it successfully indexed. After a restart the worker resumes from that point; deleting the state files forces a full reindex from scratch.
- **Coroutine pipeline.** The stages `producer → enricher → merger → loader` (in `coroutines.py`) are wired together as Python generators communicating via `send()`. Each stage processes one batch and pushes it downstream, which keeps memory bounded regardless of the corpus size.
- **Resilient to transient failures.** `decorators.py` wraps every Postgres and Elasticsearch call in a retry-with-exponential-backoff. Short outages of either store do not crash the worker — it backs off, reconnects, and continues from the last checkpoint.

## Integration with the cinema stack

This service is one of seven canonical stacks orchestrated from the repository root (`cinema/Makefile`, gateway at `cinema/gateway/`).

- **Docker networks.** Internally everything talks over the private `etl_network` (alias `movies_network`). The `movies-admin` container additionally joins the shared **`cinema_net`** so that it is reachable by the cinema-wide gateway. Create the shared network once before first start:

  ```bash
  docker network create cinema_net
  ```

- **Public entrypoint.** There is **no per-stack nginx** in this service anymore. The single gateway at `cinema/gateway/` (host port `80`) proxies:

  | Public URL | Upstream |
  |---|---|
  | `/admin/movies/*` | `movies-admin:8000` (Django runs with `FORCE_SCRIPT_NAME=/admin/movies/`) |
  | `/admin/movies/static/*` | alias from `movies_static_volume` |
  | `/admin/movies/media/*` | alias from `movies_media_volume` |
  | `/content/*` | `movies-api:8000` (the `content-api` service that reads the `movies` index this ETL produces) |

- **Bring-up from the cinema root.** From `cinema/` you can start this stack alone (`make admin`), together with auth + content (`make core`), or as part of the full stand (`make all`). See `cinema/CLAUDE.md` for the full matrix and RAM budget.

- **Port conflicts to watch out for.**
  - Postgres is **deliberately** remapped to host `5433` so it doesn't clash with `notifications/`'s Postgres on `5432`.
  - Elasticsearch on `9200` is exclusive to this stack — no other cinema service runs its own ES.
