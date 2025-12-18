.PHONY: help build up down logs shell migrate test clean

help:
	@echo "Library Management System - Docker Commands"
	@echo ""
	@echo "Available commands:"
	@echo "  make build       - Build Docker images"
	@echo "  make up          - Start all services"
	@echo "  make down        - Stop all services"
	@echo "  make logs        - View logs"
	@echo "  make shell       - Open Django shell"
	@echo "  make migrate     - Run migrations"
	@echo "  make superuser   - Create superuser"
	@echo "  make test        - Run tests"
	@echo "  make clean       - Remove containers and volumes"
	@echo "  make dev         - Start dev server (SQLite)"
	@echo "  make restart     - Restart services"

build:
	docker-compose build

up:
	docker-compose up -d
	@echo "Services started!"
	@echo "API: http://localhost:8000"
	@echo "Swagger: http://localhost:8000/swagger/"
	@echo "Admin: http://localhost:8000/admin/"

down:
	docker-compose down

logs:
	docker-compose logs -f

logs-web:
	docker-compose logs -f web

logs-db:
	docker-compose logs -f db

shell:
	docker-compose exec web python manage.py shell

bash:
	docker-compose exec web bash

migrate:
	docker-compose exec web python manage.py makemigrations
	docker-compose exec web python manage.py migrate

superuser:
	docker-compose exec web python manage.py createsuperuser

test:
	docker-compose exec web pytest -v

test-cov:
	docker-compose exec web pytest --cov=. --cov-report=html

clean:
	docker-compose down -v
	docker system prune -f

dev:
	docker-compose -f docker-compose.dev.yml up

dev-build:
	docker-compose -f docker-compose.dev.yml up --build

restart:
	docker-compose restart

status:
	docker-compose ps
