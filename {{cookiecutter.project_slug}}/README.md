# {{ cookiecutter.project_name }}

> {{ cookiecutter.project_description }}

## Quick start

```bash
# Install dependencies
uv sync --all-extras

# Copy and fill in environment variables
cp .env.example .env

# Run tests
make test

# Run linter and formatter
make lint
make format
```

## Project structure

```
{{ cookiecutter.project_slug }}/
├── src/
│   └── {{ cookiecutter.project_slug }}/
│       ├── config/          # Pydantic-based settings & configuration
│       │   └── settings.py
│       ├── connectors/      # External service & API connectors
│       │   ├── http_connector.py
│       │   └── database_connector.py
│       ├── io/              # Data readers & writers (JSON, CSV, …)
│       │   ├── readers.py
│       │   └── writers.py
│       ├── services/        # Business-logic services
│       │   └── s3_service.py
│       └── utils/           # Shared utilities (logging, …)
│           └── logging.py
├── tests/
│   ├── unit/
│   └── integration/
├── pyproject.toml
├── Makefile
└── .pre-commit-config.yaml
```

## Configuration

All configuration is managed through environment variables loaded via
[pydantic-settings](https://docs.pydantic.dev/latest/concepts/pydantic_settings/).

| Variable | Description | Default |
|---|---|---|
| `LOG_LEVEL` | Logging level | `{{ cookiecutter.log_level }}` |
{%- if cookiecutter.use_s3 == "yes" %}
| `S3_BUCKET_NAME` | Default S3 bucket | `{{ cookiecutter.s3_default_bucket }}` |
| `S3_REGION` | AWS region | `{{ cookiecutter.aws_region }}` |
| `S3_ENDPOINT_URL` | Custom S3 endpoint (MinIO, LocalStack) | — |
| `AWS_ACCESS_KEY_ID` | AWS access key | — |
| `AWS_SECRET_ACCESS_KEY` | AWS secret key | — |
{%- endif %}
{%- if cookiecutter.include_api_connector == "yes" %}
| `API_BASE_URL` | External API base URL | `https://api.example.com` |
| `API_KEY` | API authentication key | — |
| `API_TIMEOUT` | Request timeout (seconds) | `30` |
{%- endif %}
{%- if cookiecutter.include_database_connector == "yes" %}
| `DATABASE_URL` | Database connection string | `sqlite:///data.db` |
{%- endif %}

## Development

```bash
# Install dev dependencies
uv sync --all-extras

# Set up pre-commit hooks
uv run pre-commit install

# Available make targets
make help
```

## License

{{ cookiecutter.license }}
