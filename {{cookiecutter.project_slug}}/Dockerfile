{%- if cookiecutter.use_docker == "yes" -%}
# ---------- build stage ----------
FROM python:{{ cookiecutter.python_version }}-slim AS builder

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

# Install dependencies first for better layer caching
COPY pyproject.toml uv.lock* ./
RUN uv sync --frozen --no-dev --no-install-project

# Copy source and install project
COPY src/ src/
RUN uv sync --frozen --no-dev

# ---------- runtime stage ----------
FROM python:{{ cookiecutter.python_version }}-slim AS runtime

WORKDIR /app

COPY --from=builder /app/.venv /app/.venv

ENV PATH="/app/.venv/bin:$PATH"

# Run as non-root
RUN groupadd --gid 1000 app && useradd --uid 1000 --gid app --shell /bin/bash app
USER app

ENTRYPOINT ["python", "-m", "{{ cookiecutter.project_slug }}"]
{%- else -%}
# Docker support is disabled.
# Enable it by setting ``use_docker`` to "yes" when generating the project.
{%- endif %}
