## cinema/Makefile — top-level orchestration for the pet cinema stack.
##
## Default target (`make`) brings the whole project up: auth + admin-panel + catalog + gateway.
## Bootstrap (network, named volumes, .env files, RSA keys) is idempotent and runs automatically.
##
## See `make help` for the full target list.

SHELL := /bin/bash
.DEFAULT_GOAL := up

.PHONY: help up down restart ps logs \
        bootstrap network volumes envs keys \
        auth admin catalog gateway minio \
        down-auth down-admin down-catalog down-gateway down-minio

help: ## show available targets
	@awk 'BEGIN{FS=":.*##"; printf "\nTargets:\n"} /^[a-zA-Z_-]+:.*##/ {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

## --- bootstrap (idempotent; runs automatically as a dependency) ---

network: ## create the shared cinema_net docker network
	@docker network inspect cinema_net >/dev/null 2>&1 || docker network create cinema_net

volumes: ## create the named volumes the gateway mounts for Django assets
	@docker volume inspect movies_static_volume >/dev/null 2>&1 || docker volume create movies_static_volume
	@docker volume inspect movies_media_volume  >/dev/null 2>&1 || docker volume create movies_media_volume

envs: ## copy .env.example -> .env in every stack (won't overwrite existing files)
	@for d in auth admin-panel catalog minio; do \
		if [ ! -f $$d/.env ] && [ -f $$d/.env.example ]; then \
			cp $$d/.env.example $$d/.env && echo "created $$d/.env from .env.example"; \
		fi; \
	done

keys: ## generate RSA keypair and empty service-account list for auth (only if missing)
	@if [ ! -f auth/keys/rsa.private ]; then \
		openssl genrsa -out auth/keys/rsa.private 2048 2>/dev/null; \
		openssl rsa -in auth/keys/rsa.private -pubout -out auth/keys/rsa.pub 2>/dev/null; \
		echo "generated auth/keys/rsa.{private,pub}"; \
	fi
	@if [ ! -f auth/keys/services.json ]; then \
		echo '[]' > auth/keys/services.json && echo "created empty auth/keys/services.json"; \
	fi

bootstrap: network volumes envs keys ## run all one-time setup steps

## --- per-stack ---

auth: bootstrap ## start auth-api + auth-postgres + auth-redis
	cd auth && docker compose up -d

admin: bootstrap ## start Django admin + ETL + Elasticsearch (creates etl_network)
	cd admin-panel && docker compose up -d

catalog: bootstrap admin ## start catalog API (depends on admin: needs etl_network + ES indices + ../auth/keys/rsa.pub)
	cd catalog && docker compose up -d

gateway: bootstrap ## start the single nginx entrypoint on host:80
	cd gateway && docker compose up -d

minio: bootstrap ## start MinIO object storage (S3-compatible, console at :9001)
	cd minio && docker compose up -d

## --- whole project ---

up: auth admin catalog gateway minio ## bring up the entire cinema (default goal)
	@echo ""
	@echo "cinema is up. Public entrypoint: http://localhost/"
	@echo "  /auth/api/openapi      — auth swagger"
	@echo "  /admin/movies/         — Django admin"
	@echo "  /content/api/openapi   — catalog swagger"
	@echo "  http://localhost:9001  — MinIO console"
	@echo ""
	@echo "Next steps (optional):"
	@echo "  make -C auth create-admin email=root@cinema.local password=changeme"

restart: down up ## tear down and bring back up

## --- ops ---

ps: ## docker ps with a uniform format
	@docker ps --format 'table {{.Names}}\t{{.Image}}\t{{.Status}}\t{{.Ports}}'

logs: ## tail logs of all running cinema containers
	@docker ps --format '{{.Names}}' | xargs -I{} -P0 sh -c 'docker logs --tail=20 -f {} 2>&1 | sed "s/^/[{}] /"'

## --- shutdown ---

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

down: down-gateway down-catalog down-admin down-auth down-minio ## stop everything (network and volumes preserved)
