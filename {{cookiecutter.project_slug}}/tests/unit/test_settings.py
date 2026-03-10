"""Tests for configuration / settings."""

from __future__ import annotations

import pytest

from {{ cookiecutter.project_slug }}.config.settings import Settings


@pytest.mark.unit
class TestSettings:
    def test_default_log_level(self) -> None:
        settings = Settings()
        assert settings.log_level == "{{ cookiecutter.log_level }}"

    def test_override_log_level(self) -> None:
        settings = Settings(log_level="DEBUG")
        assert settings.log_level == "DEBUG"

    {% if cookiecutter.use_s3 == "yes" %}
    def test_s3_defaults(self) -> None:
        settings = Settings()
        assert settings.s3.region == "{{ cookiecutter.aws_region }}"
    {% endif %}
