.PHONY: help dev prod migrate shell test clean

help:
	@echo "ReplyCompass - Quick Reference"
	@echo "=============================="
	@echo ""
	@echo "Development:"
	@echo "  make dev              - Start development with hot-reload"
	@echo "  make dev-build        - Rebuild & start development"
	@echo "  make dev-down         - Stop development"
	@echo "  make dev-logs         - View development logs"
	@echo ""
	@echo "Production:"
	@echo "  make prod             - Start production"
	@echo "  make prod-build       - Rebuild & start production"
	@echo "  make prod-down        - Stop production"
	@echo ""
	@echo "Database:"
	@echo "  make migrate          - Run migrations"
	@echo "  make makemigrations   - Create migrations"
	@echo "  make seed             - Seed RBAC data"
	@echo "  make superuser        - Create superuser"
	@echo ""
	@echo "Testing:"
	@echo "  make test             - Run all tests"
	@echo "  make coverage         - Run with coverage"
	@echo ""
	@echo "Utilities:"
	@echo "  make shell            - Django shell"
	@echo "  make bash             - Container bash"
	@echo "  make ps               - List containers"
	@echo "  make clean            - Remove containers"
	@echo ""

dev:
	BUILD_TARGET=development docker compose up --watch

dev-build:
	BUILD_TARGET=development docker compose up --build --watch

dev-down:
	docker compose down

dev-logs:
	docker compose logs -f web celery_worker

prod:
	BUILD_TARGET=production docker compose up -d

prod-build:
	BUILD_TARGET=production docker compose up --build -d

prod-down:
	docker compose down

prod-logs:
	docker compose logs -f

migrate:
	docker compose exec web python manage.py migrate

makemigrations:
	docker compose exec web python manage.py makemigrations

seed:
	docker compose exec web python manage.py seed_rbac

superuser:
	docker compose exec web python manage.py createsuperuser

shell:
	docker compose exec web python manage.py shell

bash:
	docker compose exec web bash

test:
	docker compose exec web python manage.py test

coverage:
	docker compose exec web pytest --cov=apps --cov-report=html --cov-report=term

ps:
	docker compose ps

restart:
	docker compose restart

clean:
	docker compose down -v

clean-all:
	docker compose down -v --rmi all --remove-orphans

install:
	@echo "Installing ReplyCompass..."
	@if [ ! -f .env ]; then cp .env.example .env; echo ".env file created - please update it"; fi
	BUILD_TARGET=development docker compose build
	BUILD_TARGET=development docker compose up -d
	@sleep 5
	docker compose exec web python manage.py migrate
	docker compose exec web python manage.py seed_rbac
	@echo "Installation complete! Access at http://localhost:8000"
