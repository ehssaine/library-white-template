"""Shared test fixtures."""

from __future__ import annotations

import pytest

from {{ cookiecutter.project_slug }}.config.settings import Settings

{% if cookiecutter.use_s3 == "yes" %}
import boto3
from moto import mock_aws

from {{ cookiecutter.project_slug }}.services.s3_service import S3Service
from {{ cookiecutter.project_slug }}.config.settings import S3Settings
{% endif %}


@pytest.fixture
def settings() -> Settings:
    """Return a ``Settings`` instance with test defaults."""
    return Settings()


{% if cookiecutter.use_s3 == "yes" %}
@pytest.fixture
def s3_settings() -> S3Settings:
    return S3Settings(
        bucket_name="test-bucket",
        region="{{ cookiecutter.aws_region }}",
    )


@pytest.fixture
def s3_service(s3_settings: S3Settings) -> S3Service:
    """Return an S3Service backed by moto."""
    with mock_aws():
        # Create the bucket in the mocked environment
        client = boto3.client("s3", region_name=s3_settings.region)
        client.create_bucket(
            Bucket=s3_settings.bucket_name,
            CreateBucketConfiguration={"LocationConstraint": s3_settings.region},
        )
        yield S3Service(settings=s3_settings)
{% endif %}
