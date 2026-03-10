# Python Library White Template

A **cookiecutter** template for generating production-ready Python libraries focused on **data I/O**, **data services**, and **external API connectors**. Built with modern Python standards and **uv** for fast, reliable dependency management.

## Features

- **uv** — blazing-fast dependency resolution and virtual environment management
- **pydantic-settings** — type-safe, env-based configuration with `.env` support
- **S3 service** — ready-to-use `S3Service` class wrapping `boto3` (optional)
- **HTTP connector** — reusable `httpx`-based client with retry, timeout, and auth
- **Database connector** — SQLAlchemy-based connector with session management (optional)
- **Data I/O** — JSON and CSV readers/writers that work with files and streams
- **Structured logging** — pre-configured `structlog` setup
- **Quality tooling** — ruff (lint + format), mypy (strict), pytest + coverage
- **Pre-commit hooks** — automated code quality on every commit
- **GitHub Actions CI** — multi-version test matrix (optional)
- **Docker** — multi-stage build with uv (optional)

---

## Prerequisites

Install **cookiecutter** and **uv** before generating a project.

### Install uv

```bash
# macOS / Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# or via Homebrew
brew install uv

# or via pip
pip install uv
```

### Install cookiecutter

```bash
# via uv (recommended)
uv tool install cookiecutter

# or via pip
pip install cookiecutter
```

---

## Generate a new library

### From a local clone

```bash
git clone <this-repo-url> library-white-template
cookiecutter library-white-template/
```

### From a remote repository

```bash
cookiecutter gh:your-org/library-white-template
```

### Interactive prompts

Cookiecutter will ask you for the following values:

| Variable | Description | Default |
|---|---|---|
| `project_name` | Human-readable project name | `My Data Library` |
| `project_slug` | Python package name (auto-generated) | `my_data_library` |
| `project_description` | One-line description | `A Python library for data I/O…` |
| `author_name` | Your name | `Your Name` |
| `author_email` | Your email | `your.email@example.com` |
| `organization` | Organization / namespace | `my_org` |
| `python_version` | Target Python version | `3.12` |
| `min_python_version` | Minimum supported Python | `3.10` |
| `license` | License type | `MIT` |
| `use_s3` | Include S3 service module | `yes` |
| `use_docker` | Generate Dockerfile | `yes` |
| `use_github_actions` | Generate CI workflow | `yes` |
| `aws_region` | Default AWS region | `eu-west-1` |
| `s3_default_bucket` | Default S3 bucket name | _(empty)_ |
| `include_api_connector` | Include HTTP API connector | `yes` |
| `include_database_connector` | Include database connector | `yes` |
| `log_level` | Default log level | `INFO` |

### Non-interactive generation

```bash
cookiecutter library-white-template/ --no-input \
  project_name="Customer Data Lib" \
  use_s3=yes \
  include_api_connector=yes \
  include_database_connector=no
```

---

## After generation — project setup

```bash
cd my_data_library

# Initialise git
git init && git add . && git commit -m "Initial project from template"

# Install all dependencies (including dev)
uv sync --all-extras

# Set up pre-commit hooks
uv run pre-commit install

# Copy and configure environment variables
cp .env.example .env
# Edit .env with your actual values

# Run the full quality suite
make test        # pytest + coverage
make lint        # ruff check
make format      # ruff format
make typecheck   # mypy --strict
```

---

## Generated project structure

```
my_data_library/
│
├── src/
│   └── my_data_library/
│       │
│       ├── __init__.py              # Package root, re-exports Settings
│       │
│       ├── config/                  # Configuration layer
│       │   ├── __init__.py
│       │   └── settings.py          # Pydantic-settings with nested models
│       │                            #   Settings, S3Settings, APISettings, DatabaseSettings
│       │
│       ├── services/                # Business-logic services
│       │   ├── __init__.py
│       │   └── s3_service.py        # S3 upload/download/list/delete/presigned URLs
│       │
│       ├── connectors/              # External service connectors
│       │   ├── __init__.py
│       │   ├── http_connector.py    # Generic HTTP client (httpx) with retry & auth
│       │   └── database_connector.py # SQLAlchemy engine + session management
│       │
│       ├── io/                      # Data I/O (readers & writers)
│       │   ├── __init__.py
│       │   ├── readers.py           # read_json(), read_csv_lines()
│       │   └── writers.py           # write_json(), write_csv()
│       │
│       └── utils/                   # Shared utilities
│           ├── __init__.py
│           └── logging.py           # structlog bootstrap
│
├── tests/
│   ├── conftest.py                  # Shared fixtures (Settings, moto-backed S3)
│   ├── unit/
│   │   ├── test_settings.py
│   │   ├── test_io.py
│   │   └── test_s3_service.py
│   └── integration/
│
├── .env.example                     # Template for environment variables
├── .gitignore
├── .pre-commit-config.yaml          # ruff + mypy + pre-commit-hooks
├── .python-version                  # Pinned Python version for uv
├── Dockerfile                       # Multi-stage build with uv
├── Makefile                         # Common dev commands
├── pyproject.toml                   # Project metadata, deps, tool config
└── README.md                        # Generated project README
```

---

## How to structure new code

### Adding a new service

Services encapsulate business logic. Place them in `src/<pkg>/services/`.

```python
# src/my_data_library/services/transform_service.py
from __future__ import annotations

import structlog

logger = structlog.get_logger(__name__)


class TransformService:
    """Transform raw data into domain models."""

    def normalize(self, records: list[dict]) -> list[dict]:
        logger.info("transform.normalize", count=len(records))
        return [self._clean(r) for r in records]

    def _clean(self, record: dict) -> dict:
        return {k.lower().strip(): v for k, v in record.items()}
```

### Adding a new connector

Connectors integrate with external systems. Place them in `src/<pkg>/connectors/`.

```python
# src/my_data_library/connectors/weather_connector.py
from __future__ import annotations

from my_data_library.connectors.http_connector import HTTPConnector


class WeatherConnector:
    """Fetch weather data from an external API."""

    def __init__(self, base_url: str, api_key: str) -> None:
        self._http = HTTPConnector(
            base_url=base_url,
            headers={"X-API-Key": api_key},
        )

    def get_forecast(self, city: str) -> dict:
        return self._http.get(f"/forecast/{city}")

    def close(self) -> None:
        self._http.close()
```

### Adding a new I/O format

Readers and writers go in `src/<pkg>/io/`. Follow the existing pattern — accept both
file paths and file-like objects so they compose with S3 streams.

```python
# src/my_data_library/io/readers.py  (add to existing file)

import xml.etree.ElementTree as ET
from pathlib import Path
from typing import IO


def read_xml(source: str | Path | IO[bytes]) -> ET.Element:
    """Parse XML from a file path or binary stream."""
    if isinstance(source, (str, Path)):
        tree = ET.parse(source)
        return tree.getroot()
    return ET.fromstring(source.read())
```

### Adding configuration for a new component

Extend `settings.py` with a new nested model:

```python
# In src/my_data_library/config/settings.py

class RedisSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="REDIS_")

    host: str = "localhost"
    port: int = 6379
    db: int = 0


class Settings(BaseSettings):
    # ... existing fields ...
    redis: RedisSettings = RedisSettings()
```

Then set `REDIS_HOST`, `REDIS_PORT`, etc. in your `.env` file.

### Writing tests

- **Unit tests** go in `tests/unit/` — fast, no external dependencies.
- **Integration tests** go in `tests/integration/` — may require running services.
- Use `moto` for mocking AWS services (see `tests/conftest.py` for the S3 fixture).
- Mark tests with `@pytest.mark.unit` or `@pytest.mark.integration`.

```python
# tests/unit/test_transform_service.py
import pytest
from my_data_library.services.transform_service import TransformService


@pytest.mark.unit
class TestTransformService:
    def test_normalize_lowercases_keys(self) -> None:
        svc = TransformService()
        result = svc.normalize([{"Name": "Alice", "AGE": 30}])
        assert result == [{"name": "Alice", "age": 30}]
```

---

## Common workflows

### Using S3Service to read/write data

```python
from my_data_library.services.s3_service import S3Service
from my_data_library.io.readers import read_json

s3 = S3Service()

# Upload
s3.upload_file("data/input.json", "/local/path/input.json")

# Download as stream and parse
stream = s3.download_fileobj("data/input.json")
data = read_json(stream)

# List objects
keys = s3.list_objects(prefix="data/")
```

### Using HTTPConnector with an external API

```python
from my_data_library.connectors.http_connector import HTTPConnector

with HTTPConnector() as client:          # reads API_BASE_URL, API_KEY from env
    users = client.get("/v1/users", params={"page": 1})
    client.post("/v1/users", json={"name": "Alice"})
```

### Running quality checks

```bash
make help          # show all available targets
make lint          # ruff check
make format        # ruff format + fix
make typecheck     # mypy --strict
make test          # pytest with coverage
make test-unit     # unit tests only
make clean         # remove build artifacts
```

---

## Dependency management with uv

```bash
# Add a runtime dependency
uv add requests

# Add a dev dependency
uv add --dev hypothesis

# Remove a dependency
uv remove requests

# Update all dependencies
uv lock --upgrade

# Sync environment to match lockfile
uv sync --all-extras
```

---

## License

This template is provided under the MIT license.
