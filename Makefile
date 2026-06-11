# Shorthand helper automation commands for CodeGuru AI

.PHONY: dev build down migrate test logs shell-backend shell-frontend

dev:
	docker-compose up -d

build:
	docker-compose up --build -d

down:
	docker-compose down

migrate:
	docker-compose exec backend alembic upgrade head

test:
	docker-compose exec backend pytest

logs:
	docker-compose logs -f

shell-backend:
	docker-compose exec backend bash

shell-frontend:
	docker-compose exec frontend sh
