# cinema/Makefile — top-level orchestration for the pet cinema stack.
#
# Default target (`make`) brings the whole project up: auth + admin-panel + catalog + gateway.
# Bootstrap (network, named volumes, .env files, RSA keys) is idempotent and runs automatically.
#
# See `make help` for the full target list.

SHELL := /bin/bash
.DEFAULT_GOAL := up

.PHONY: help up down restart ps logs \
        bootstrap network volumes envs keys \
        auth admin catalog gateway minio frontend admin-superuser \
        down-auth down-admin down-catalog down-gateway down-minio down-frontend \
        drop-volume drop-volumes

# Django admin superuser defaults — override via `make admin-superuser ADMIN_USER=foo ADMIN_PASS=bar`.
ADMIN_USER  ?= admin
ADMIN_PASS  ?= admin
ADMIN_EMAIL ?= admin@cinema.local

# `make help` parses a description placed directly above each target:
#     ## description text
#     target-name:
# Section banners (`# === ... ===`) are plain comments and don't show up in help.
## show available targets
help:
	@awk 'BEGIN{FS=":"} \
	     /^## / {desc=substr($$0, 4); next} \
	     /^[a-zA-Z_-]+:/ {if (desc != "") {printf "  \033[36m%-15s\033[0m %s\n", $$1, desc; desc=""}} \
	     /^[[:space:]]*$$/ {desc=""}' $(MAKEFILE_LIST)

# === bootstrap (idempotent; runs automatically as a dependency) ===

## create the shared cinema_net docker network
network:
	@docker network inspect cinema_net >/dev/null 2>&1 || docker network create cinema_net

## create the named volumes the gateway mounts for Django assets
volumes:
	@docker volume inspect movies_static_volume >/dev/null 2>&1 || docker volume create movies_static_volume
	@docker volume inspect movies_media_volume  >/dev/null 2>&1 || docker volume create movies_media_volume

## copy .env.example -> .env in every stack (won't overwrite existing files)
envs:
	@for d in auth admin-panel catalog minio frontend; do \
		if [ ! -f $$d/.env ] && [ -f $$d/.env.example ]; then \
			cp $$d/.env.example $$d/.env && echo "created $$d/.env from .env.example"; \
		fi; \
	done

## generate RSA keypair and empty service-account list for auth (only if missing)
keys:
	@if [ ! -f auth/keys/rsa.private ]; then \
		openssl genrsa -out auth/keys/rsa.private 2048 2>/dev/null; \
		openssl rsa -in auth/keys/rsa.private -pubout -out auth/keys/rsa.pub 2>/dev/null; \
		echo "generated auth/keys/rsa.{private,pub}"; \
	fi
	@if [ ! -f auth/keys/services.json ]; then \
		echo '[]' > auth/keys/services.json && echo "created empty auth/keys/services.json"; \
	fi

## run all one-time setup steps
bootstrap: network volumes envs keys

# === per-stack ===

## start auth-api + auth-postgres + auth-redis
auth: bootstrap
	cd auth && docker compose up -d

## start Django admin + ETL + Elasticsearch (creates etl_network)
admin: bootstrap
	cd admin-panel && docker compose up -d

## start catalog API (depends on admin: needs etl_network + ES indices + ../auth/keys/rsa.pub)
catalog: bootstrap admin
	cd catalog && docker compose up -d

## start the single nginx entrypoint on host:80
gateway: bootstrap
	cd gateway && docker compose up -d

## start MinIO object storage (S3-compatible, console at :9001)
minio: bootstrap
	cd minio && docker compose up -d

## start Next.js frontend (serves http://localhost/ via the gateway)
frontend: bootstrap
	cd frontend && docker compose up -d

## create/reset Django superuser (defaults: admin/admin, override ADMIN_USER/ADMIN_PASS/ADMIN_EMAIL)
admin-superuser:
	@docker exec movies-admin python manage.py shell -c "from django.contrib.auth import get_user_model; U = get_user_model(); user, created = U.objects.update_or_create(username='$(ADMIN_USER)', defaults={'email': '$(ADMIN_EMAIL)', 'is_staff': True, 'is_superuser': True}); user.set_password('$(ADMIN_PASS)'); user.save(); print('superuser $(ADMIN_USER)/$(ADMIN_PASS)', 'created' if created else 'reset')"

# === whole project ===

## bring up the entire cinema (default goal)
up: auth admin catalog gateway minio frontend
	@echo ""
	@echo "cinema is up. Public entrypoint: http://localhost/"
	@echo "  /auth/api/openapi      — auth swagger"
	@echo "  /admin/movies/         — Django admin"
	@echo "  /content/api/openapi   — catalog swagger"
	@echo "  http://localhost:9001  — MinIO console"
	@echo ""
	@echo "Next steps (optional):"
	@echo "  make admin-superuser                                              # Django admin: admin/admin"
	@echo "  make -C auth create-admin email=root@cinema.local password=changeme"

## tear down and bring back up
restart: down up

# === ops ===

## docker ps with a uniform format
ps:
	@docker ps --format 'table {{.Names}}\t{{.Image}}\t{{.Status}}\t{{.Ports}}'

## tail logs of all running cinema containers
logs:
	@docker ps --format '{{.Names}}' | xargs -I{} -P0 sh -c 'docker logs --tail=20 -f {} 2>&1 | sed "s/^/[{}] /"'

# === shutdown ===

down-auth:
	-cd auth && docker compose down
down-admin:
	-cd admin-panel && docker compose down
down-catalog:
	-cd catalog && docker compose down
down-gateway:
	-cd gateway && docker compose down
down-minio:
	-cd minio && docker compose down
down-frontend:
	-cd frontend && docker compose down

## stop everything (network and volumes preserved)
down: down-gateway down-frontend down-catalog down-admin down-auth down-minio

# === volume cleanup (destructive) ===

# Named volumes owned by this stack.
PROJECT_VOLUMES := auth_auth_db_volume auth_auth_redis_volume movies_static_volume movies_media_volume es_data postgres_etl_data cinema-minio_minio_data

## drop a single docker volume by name (usage: make drop-volume name=movies_media_volume)
drop-volume:
	@if [ -z "$(name)" ]; then echo "usage: make drop-volume name=<volume>"; exit 2; fi
	@docker volume rm -f $(name)

## drop ALL named volumes owned by this stack (auth db/redis, Django static/media, ES, postgres-etl, MinIO)
drop-volumes: down
	@docker volume rm -f $(PROJECT_VOLUMES)
