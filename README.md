# Cinema — online cinema platform (pet project)

A small but full-shape **online cinema backend** built as a set of independent services that talk to each other through a single gateway. Each service can be developed, deployed, and reasoned about on its own.

This is a portfolio / pet project: it isn't running in production, but it solves the same problems a real cinema backend has to solve — how to store and search a catalogue of films, how to authenticate users, how to manage editorial content, and how to expose all of that under one consistent public URL.

## What's inside

Four services, each in its own directory with its own README:

| Service | What it does | Stack |
|---|---|---|
| **[`auth/`](auth/README.md)** | Issues and verifies JWT tokens, owns user accounts, handles OAuth login (Yandex, Google), enforces roles | FastAPI · Postgres · Redis · RS256 JWT |
| **[`admin-panel/`](admin-panel/README.md)** | Editorial UI for films / genres / persons + ETL worker that mirrors the database into a search index | Django · Postgres · Elasticsearch |
| **[`catalog/`](catalog/README.md)** | Read-only public API serving the film catalogue with caching and rate limiting | FastAPI · Elasticsearch · Redis |
| **[`gateway/`](gateway/README.md)** | Single nginx entrypoint on port 80, routes traffic to every service by URL prefix | nginx |

How they fit together: editors write films in the **admin-panel**, an ETL worker indexes them into Elasticsearch, the **catalog** serves them to end users, and every request is authenticated against tokens issued by **auth**. The **gateway** is the only thing the outside world ever talks to.

## Quick start

You need Docker (with Compose v2), `make`, and `openssl`.

```bash
make
```

That's the whole setup. The default target:

1. creates the shared `cinema_net` Docker network and named volumes;
2. copies every `.env.example` to `.env` (only if missing — won't clobber local edits);
3. generates an RSA keypair for the JWT issuer;
4. starts all four services in the right order.

Once it finishes, the stack is reachable at <http://localhost/>:

| URL | What |
|---|---|
| <http://localhost/> | Plain-text landing page listing the routes |
| <http://localhost/auth/api/openapi> | Auth API Swagger UI |
| <http://localhost/content/api/openapi> | Catalog API Swagger UI |
| <http://localhost/admin/movies/> | Django admin for the catalogue |

Optionally, create a human admin account:

```bash
make -C auth create-admin email=root@cinema.local password=changeme
```

To stop everything (network and volumes preserved): `make down`. Full target list: `make help`.

## Tech stack at a glance

- **Languages**: Python 3.9–3.12
- **Web frameworks**: FastAPI (auth, catalog), Django (admin-panel)
- **Datastores**: PostgreSQL (auth, admin-panel), Elasticsearch (search index for the catalogue), Redis (cache + rate-limit + JWT blacklist)
- **Auth**: RS256 JWTs signed by `auth/`, verified by `catalog/` and (in production) other consumers via a shared public key
- **Routing**: nginx reverse proxy with per-service URL prefixes
- **Containerization**: Docker Compose, one stack per service, joined by a shared `cinema_net` network
- **Observability**: OpenTelemetry + Jaeger tracing, `X-Request-Id` propagation end-to-end
- **Migrations**: Alembic (auth), Django migrations (admin-panel)

## Repository layout

```
cinema/
├── Makefile           ← root orchestration; `make` brings up everything
├── README.md          ← you are here
├── auth/              ← identity service
├── admin-panel/       ← Django admin + ETL (Postgres → Elasticsearch)
├── catalog/           ← read-only public film API
└── gateway/           ← single nginx entrypoint (host port 80)
```

Each service directory is self-contained: its own `docker-compose.yml`, its own dependencies, its own README with technical details.

## Where to read more

- For **how a specific service works**: open its README — every service has one with purpose, endpoints, architecture, and integration notes.
- For **how the gateway routes traffic** between services: [`gateway/README.md`](gateway/README.md).
- For **operational commands**: `make help` at the repo root.

## Origin

The services were assembled from coursework done as part of Yandex Practicum's *Middle Python Developer* track. Original sprint authors are credited in commit history; this repository consolidates the per-sprint stacks into a single integrated cinema and adds the gateway, root Makefile, RSA-key sharing, and cross-service routing that turn them into one coherent system.
