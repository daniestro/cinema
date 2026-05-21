# frontend/

Next.js 15 App Router service that serves `http://localhost/` through the gateway. RSC-first, dark theme, warm-orange (`#FF6A2C`) accent. See [`../FRONTEND.md`](../FRONTEND.md) for locked-in stack decisions.

## Running

```bash
make -C .. frontend    # only this service
make -C .. up          # whole cinema (gateway + auth + admin + catalog + minio + frontend)
```

The container joins the external `cinema_net`. It does not publish a host port — the gateway is the single public entrypoint on `:80`.

## Dev loop

`docker-compose.yml` mounts `./src`, `./messages`, `./public`, and the four root config files into the container. Editing them triggers Next.js hot reload through the gateway's `proxy_http_version 1.1` + `Upgrade`/`Connection` headers on `location /`.

Rebuild after touching `package.json`, `pnpm-lock.yaml`, or the `Dockerfile`:

```bash
docker compose build && docker compose up -d
```

## Stack pins

Every dependency in `package.json` is exact-pinned (no `^`/`~`). Versions are chosen per the project's "≥ 6 months old, no open advisories" rule from `feedback_frontend_workflow`. The security override won out for `next` and `react`/`react-dom` (CVE-2025-66478 / CVE-2025-55182): both are bumped to the patched releases inside their minor lines, even though the patches are younger than 6 months.

## Layout

```
src/app/        — App Router routes (RSC by default)
src/components/ — shared, domain-agnostic UI (layout/, common/, later: ui/ for shadcn)
src/features/   — business logic by domain (later chunks)
src/lib/        — env, utils, api client (later chunks)
messages/en.json — strings live here, not hardcoded in JSX (i18n-ready)
```
