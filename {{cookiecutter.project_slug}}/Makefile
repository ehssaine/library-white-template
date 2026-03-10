.DEFAULT_GOAL := help
.PHONY: help venv install lint format typecheck test test-unit test-integration clean

VENV_DIR := .venv
PYTHON := $(VENV_DIR)/bin/python
ACTIVATE := . $(VENV_DIR)/bin/activate

help: ## Show this help message
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

venv: ## Create virtual environment using venv
	@if [ ! -d "$(VENV_DIR)" ]; then \
		echo "Creating virtual environment in $(VENV_DIR)..."; \
		python{{ cookiecutter.python_version }} -m venv $(VENV_DIR) || python3 -m venv $(VENV_DIR); \
		echo "Virtual environment created. Activate with: $(ACTIVATE)"; \
	else \
		echo "Virtual environment already exists in $(VENV_DIR)"; \
	fi

install: venv ## Install dependencies with uv (creates venv first if needed)
	uv sync --all-extras

lint: ## Run ruff linter
	uv run ruff check src/ tests/

format: ## Format code with ruff
	uv run ruff format src/ tests/
	uv run ruff check --fix src/ tests/

typecheck: ## Run mypy type checker
	uv run mypy src/

test: ## Run all tests
	uv run pytest

test-unit: ## Run unit tests only
	uv run pytest -m unit

test-integration: ## Run integration tests only
	uv run pytest -m integration

clean: ## Remove build artifacts
	rm -rf dist/ build/ .eggs/ *.egg-info .mypy_cache .pytest_cache .coverage htmlcov/
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
