.PHONY: help up down restart logs build

help:
	@echo "Targets:"
	@echo "  up       Bring frontend-app up"
	@echo "  down     Stop frontend-app"
	@echo "  restart  Restart frontend-app"
	@echo "  logs     Tail container logs"
	@echo "  build    Rebuild the image"

up:
	docker compose up -d

down:
	docker compose down

restart:
	docker compose restart

logs:
	docker compose logs -f --tail=200

build:
	docker compose build
