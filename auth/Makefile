up:
	docker compose up -d --build

down:
	docker compose down

downv:
	docker compose down -v

env:
	cp .env.example .env

migrate:
	docker compose exec auth-api alembic -c /opt/app/alembic.ini upgrade head

create-admin:
	docker compose exec auth-api python -m cli admin create $(email) $(password)

init-service-accounts:
	docker compose exec auth-api python -m cli service init-service-accounts

create-user:
	docker compose exec auth-api python -m cli user create $(n)

network:
	docker network inspect cinema_net >/dev/null 2>&1 || docker network create cinema_net
