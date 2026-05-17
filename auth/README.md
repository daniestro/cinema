# auth — JWT issuer, OAuth, roles, blacklist

## Purpose

This service is the **identity layer** of the cinema project. It is the only service that:

- issues and validates **RS256 JWT tokens** (access + refresh) used by every other service in the stand;
- owns the **user registry** — accounts, passwords, login history;
- handles **OAuth login** via Yandex and Google, including linking external identities to existing accounts;
- enforces **role-based access control** (RBAC) — admins assign roles, every other service consumes the role claim from the JWT;
- maintains a **token blacklist** in Redis for revoked refresh tokens.

The canonical RSA private key (`keys/rsa.private`) lives here and **only** here; all other services receive the matching public key as a Docker secret and only verify tokens — they never issue them.

## Quick start

### 1. Prepare the shared Docker network

All cinema services join the external `cinema_net` so they can resolve each other by container name. Create it once on your host:

```bash
make network         # idempotent — no-op if it already exists
```

### 2. Configure environment

```bash
make env             # copies .env.example → .env
$EDITOR .env         # fill in OAuth credentials and any host-specific values
```

The defaults work for a local stand. The two values you actually need to fill in are the OAuth client IDs/secrets — get them at:

- Yandex OAuth — <https://oauth.yandex.ru>
- Google OAuth — <https://console.cloud.google.com>

### 3. Generate the RSA key pair (first time only)

The service signs JWTs with the RSA private key at `keys/rsa.private` and ships the matching public key at `keys/rsa.pub` for other services to verify. The private key and the service-account file are **gitignored** — you must produce them locally before the first `make up`:

```bash
openssl genrsa -out keys/rsa.private 2048
openssl rsa -in keys/rsa.private -pubout -out keys/rsa.pub
echo '[]' > keys/services.json    # empty service-account list; CLI will populate it
```

### 4. Bring up the stack

```bash
make up              # builds image, starts auth-api + auth-postgres + auth-redis
make migrate         # runs alembic upgrade head inside auth-api
```

The service is now reachable at `http://localhost:8002` (direct) and at `http://localhost/auth/` once the cinema gateway is up.

### 5. Bootstrap accounts

```bash
make init-service-accounts                              # creates the service accounts listed in keys/services.json
make create-admin email=root@cinema.local password=...  # creates a human admin
make create-user n=5                                    # optional: seed 5 random users for dev
```

### 6. Verify

```bash
curl http://localhost:8002/health           # → 200 OK
open http://localhost:8002/api/openapi      # Swagger UI (or /auth/api/openapi via gateway)
```

### Lifecycle commands

```bash
make down            # stop and remove containers, keep volumes
make downv           # stop, remove containers AND volumes (wipes the DB)
```

## What the deployed service provides

### HTTP API (`/api/v1/*`)

| Group | Module | What it does |
|---|---|---|
| `auth` | `api/v1/auth.py` | login (email+password), refresh, logout, current-user info; refresh tokens go through the Redis blacklist on logout |
| `oauth` | `api/v1/oauth.py` | login/registration via Yandex and Google; links external identities to existing accounts via the *socialnet* table |
| `user` | `api/v1/user.py` | sign-up, profile read/edit, change password, change login, list login history |
| `role` | `api/v1/role.py` | admin-only: create / edit / list / delete roles |
| `user_role` | `api/v1/user_role.py` | admin-only: assign / revoke a role for a user |
| `healthcheck` | `api/healthcheck.py` | `GET /health` — used by the docker healthcheck |

All write endpoints are rate-limited via `fastapi-limiter` (Redis-backed).

Public direct port: **`8002:80`**. Behind the cinema gateway: **`http://localhost/auth/...`** (the FastAPI app is configured with `root_path=/auth`, so Swagger and links work through the prefix).

### CLI (`python -m cli ...`)

The image ships a CLI used both at bootstrap and for ops:

| Command | Purpose |
|---|---|
| `cli admin create <email> <password>` | Create a human admin account |
| `cli user create <count>` | Generate N random users (dev only) |
| `cli service init-service-accounts` | Create service accounts from `keys/services.json` (called automatically by the entrypoint on every boot) |

Run any of them via `docker compose exec auth-api python -m cli ...`, or via the Makefile shortcuts (`make create-admin`, `make create-user`, `make init-service-accounts`).

### Stores

- **Postgres 16** (`auth-postgres`) — users, roles, login history, socialnet links, blacklist persistence. Owned by this service, not shared.
- **Redis 7** (`auth-redis`) — refresh-token blacklist and rate-limiter counters.

### Docker secrets

The compose file mounts three files as Docker secrets, not as bind-mounts:

| Secret | Source file | Mounted at | Purpose |
|---|---|---|---|
| `rsa_priv` | `keys/rsa.private` | `/run/secrets/rsa_priv` | sign JWTs |
| `rsa_pub` | `keys/rsa.pub` | `/run/secrets/rsa_pub` | verify JWTs (also shared with other services) |
| `service_accounts` | `keys/services.json` | `/run/secrets/service_accounts` | bootstrap inter-service users (e.g. `notify.pipeline`) |

## Tests

The project has a **two-layer test pyramid**, both under `tests/`:

### `tests/unit/` — fast in-process tests

Pure unit tests for individual services: `JWTService` (encode/decode/expiry/invalid), `HashService` (passlib), password validation. No Docker, no database — they run against the app code directly.

```bash
poetry install
poetry run pytest tests/unit/
```

Test RSA keys for JWT round-trips live at `tests/unit/test_data/{rsa.pub,rsa.private}` — the private one is gitignored; generate a throwaway pair locally the same way as in step 3 of Quick start.

### `tests/functional/` — black-box HTTP tests in their own compose stack

Spins up a parallel `auth-api` plus its own Postgres and Redis (see `tests/docker-compose.yaml` and `tests/Dockerfile`), then runs `pytest tests/functional/src` inside a sidecar container. These tests speak to the API over HTTP exactly as a real client would.

```bash
cd tests
docker compose --env-file .test.env up --build --abort-on-container-exit
docker compose down -v
```

Layout: `tests/functional/fixtures/` (pytest fixtures: api client, redis, etc.), `tests/functional/testdata/` (request/response samples), `tests/functional/settings.py` (test-suite config), `tests/functional/src/` (the test modules pytest actually picks up).

## Project structure

```
auth/
├── Makefile                 ← entrypoint for everyday commands
├── docker-compose.yaml      ← auth-api + auth-postgres + auth-redis
├── pyproject.toml           ← poetry: deps, ruff, mypy, pytest config
├── poetry.lock
├── .env.example             ← template (no real secrets)
├── keys/
│   ├── rsa.pub              ← public JWT key (shared with other services)
│   ├── rsa.private          ← gitignored — generate locally
│   └── services.json        ← gitignored — service-account seed
├── src/
│   ├── Dockerfile
│   ├── docker-entrypoint.sh ← alembic upgrade → init service accounts → gunicorn/uvicorn
│   ├── requirements.txt     ← poetry-exported lock for the image build
│   ├── alembic.ini
│   ├── migrations/          ← alembic revisions
│   ├── cli/                 ← admin / user / service-account commands
│   └── auth_app/            ← the FastAPI app itself
│       ├── main.py          ← app factory, middleware, OTel/Jaeger setup, rate-limit init
│       ├── api/             ← HTTP layer (api/v1/{auth,oauth,user,role,user_role}.py)
│       ├── services/        ← business logic (jwt_service, hash_service, oauth/*)
│       ├── models/          ← {domain, dto} pydantic + sqlmodel models
│       ├── db/              ← sqlalchemy + redis bindings
│       ├── external/        ← storage adapters
│       ├── errors/          ← typed exceptions surfaced as HTTP errors
│       └── core/            ← settings, jaeger config
└── tests/
    ├── Dockerfile           ← image used by tests/docker-compose.yaml
    ├── docker-compose.yaml  ← isolated functional-test stack
    ├── requirements.txt
    ├── unit/                ← fast in-process tests (JWT, hash, validation)
    └── functional/          ← HTTP black-box tests, fixtures, testdata
```

### Why both `pyproject.toml` and `src/requirements.txt`?

`pyproject.toml` + `poetry.lock` are the source of truth — that is what `poetry install` reads for local development and CI. `src/requirements.txt` is an **export** of that lock for the Docker image build, so the container does not need to install Poetry itself (which is heavy and slow). When you change dependencies, edit `pyproject.toml`, run `poetry lock`, then refresh the export:

```bash
poetry export -f requirements.txt --without-hashes -o src/requirements.txt
poetry export -f requirements.txt --without-hashes --with test -o tests/requirements.txt
```

`tests/requirements.txt` is a separate, narrower set used by the functional-test container.

## Architecture

This service is a fairly orthodox **FastAPI + SQLAlchemy + Redis** application; the interesting parts are how it earns its trust and how that trust propagates.

**Token issuance and verification.** The API receives a login (email+password or an OAuth callback), validates credentials, and returns an access/refresh token pair signed with RSA-256 using the private key at `/run/secrets/rsa_priv`. The matching public key is the only thing other services need: they verify the signature, read the role and user-id claims, and act accordingly. This is why every other stack mounts `keys/rsa.pub` as a read-only secret but never sees `keys/rsa.private`.

**Refresh-token blacklist.** Refresh tokens, unlike access tokens, are revocable. On logout (or password change, or admin force-logout) the token's `jti` is written to Redis with a TTL equal to its remaining lifetime. Every refresh request consults the blacklist before issuing a new pair — once blacklisted, the token cannot be exchanged again, and it disappears from Redis automatically when its TTL expires.

**OAuth and socialnet linking.** The `oauth` endpoints accept callbacks from Yandex and Google, fetch the user profile, and either log the user into a linked account or create a new one. If the same email already exists locally, the external identity is attached to it via a *socialnet* row — so the user can log in either way.

**Role-based access control.** Roles live in Postgres and are administered via `/api/v1/role` and `/api/v1/user_role`. The JWT carries the role list as a claim, so consuming services don't need to query auth on every request — they trust the signature.

**Rate limiting.** Sensitive endpoints (login, registration, password change) are wrapped in `fastapi-limiter` decorators backed by the same Redis instance. The limiter is initialized in the FastAPI `lifespan` handler at startup.

**Observability.** When `AUTH_JAEGER_HOST` is set, OpenTelemetry exports spans to Jaeger; an `X-Request-Id` is generated in middleware and propagated downstream so other services in the cinema can correlate traces.

**Bootstrap.** On every container start, `src/docker-entrypoint.sh` runs `alembic upgrade head`, then `python -m cli service init-service-accounts` (idempotent — it skips accounts that already exist), and finally launches gunicorn (release) or uvicorn `--reload` (debug, controlled by the `COMMAND` build arg).

## Integration with the cinema stack

- **Shared network.** `auth-api` joins **two** networks: the private `default` (for postgres/redis siblings) and the external `cinema_net`. Other cinema stacks resolve `auth-api` by container name over `cinema_net` — there is no per-stack copy of the auth service.

- **Public entrypoint.** There is no nginx in this stack anymore. The single cinema gateway (at `cinema/gateway/`, host port `80`) proxies `/auth/*` directly to `auth-api:80`. Because the app is started with `AUTH_PROJECT_ROOT_URL=/auth`, FastAPI's `root_path` is set correctly and Swagger UI works end-to-end at `http://localhost/auth/api/openapi`.

- **RSA-key distribution.** The canonical key pair belongs to this stack. Other stacks (`notifications/`, `ugc-content/`, `ugc-events/`) mount the **public** key as a Docker secret; only `auth/` ever sees the private one. If you regenerate the key pair, you must restart every dependent stack so they pick up the new public key.

- **Bring-up order from the cinema root.** From the `cinema/` directory you can start auth alone (`make auth`), the read path (`make core` — auth + admin + content), or the entire stand (`make all`). Notifications depends on auth being up first, so always start `auth` before `notify`. See `cinema/CLAUDE.md` for the full matrix and RAM budget.

- **Direct host port `8002`** is exposed for debugging convenience (e.g. `curl http://localhost:8002/health`); production deployments should drop the `ports:` block and rely on the gateway.

## URLs at a glance

| What | URL |
|---|---|
| Health check | <http://localhost:8002/health> |
| Swagger (direct) | <http://localhost:8002/api/openapi> |
| Swagger (via gateway) | <http://localhost/auth/api/openapi> |
| Jaeger UI (if started) | <http://localhost:16686/> |
