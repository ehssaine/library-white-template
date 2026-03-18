"""Centralized settings using pydantic-settings.

All configuration is loaded from environment variables and/or `.env` files.
Nested models keep related settings grouped while remaining overridable via
flat env vars using the configured prefix and delimiter.
"""

from __future__ import annotations

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


{% if cookiecutter.use_s3 == "yes" -%}
class S3Settings(BaseSettings):
    """AWS S3 configuration."""

    model_config = SettingsConfigDict(env_prefix="S3_")

    bucket_name: str = "{{ cookiecutter.s3_default_bucket }}"
    region: str = "{{ cookiecutter.aws_region }}"
    endpoint_url: str | None = None
    access_key_id: str | None = Field(default=None, alias="AWS_ACCESS_KEY_ID")
    secret_access_key: str | None = Field(default=None, alias="AWS_SECRET_ACCESS_KEY")


{% endif -%}
{% if cookiecutter.include_api_connector == "yes" -%}
class APISettings(BaseSettings):
    """External API connector configuration."""

    model_config = SettingsConfigDict(env_prefix="API_")

    base_url: str = "https://api.example.com"
    key: str = ""
    timeout: int = 30
    max_retries: int = 3


{% endif -%}
{% if cookiecutter.include_database_connector == "yes" -%}
class DatabaseSettings(BaseSettings):
    """Database connection configuration."""

    model_config = SettingsConfigDict(env_prefix="DATABASE_")

    url: str = "sqlite:///data.db"
    pool_size: int = 5
    echo: bool = False


{% endif -%}
class Settings(BaseSettings):
    """Root application settings.

    Usage::

        settings = Settings()           # from env / .env
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )
    {%- if cookiecutter.use_s3 == "yes" %}
    s3: S3Settings = S3Settings()
    {%- endif %}
    {%- if cookiecutter.include_api_connector == "yes" %}
    api: APISettings = APISettings()
    {%- endif %}
    {%- if cookiecutter.include_database_connector == "yes" %}
    database: DatabaseSettings = DatabaseSettings()
    {%- endif %}
