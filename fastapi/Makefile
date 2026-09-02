.PHONY: help install run test lint format typecheck migrate revision docker-up docker-down

help:
	@echo "install     Install deps with uv"
	@echo "run         Run the API with reload"
	@echo "test        Run pytest"
	@echo "lint        ruff check"
	@echo "format      ruff format"
	@echo "typecheck   mypy --strict"
	@echo "migrate     alembic upgrade head"
	@echo "revision    alembic revision --autogenerate -m 'msg'"
	@echo "docker-up   docker compose up --build"
	@echo "docker-down docker compose down -v"

install:
	uv sync --all-extras

run:
	uv run uvicorn app.main:app --reload

test:
	uv run pytest

lint:
	uv run ruff check .

format:
	uv run ruff format .

typecheck:
	uv run mypy app

migrate:
	uv run alembic upgrade head

revision:
	uv run alembic revision --autogenerate -m "$(m)"

docker-up:
	docker compose up --build

docker-down:
	docker compose down -v
