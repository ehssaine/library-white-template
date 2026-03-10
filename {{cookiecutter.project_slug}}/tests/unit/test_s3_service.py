{%- if cookiecutter.use_s3 == "yes" -%}
"""Tests for S3Service using moto mock."""

from __future__ import annotations

import pytest

from {{ cookiecutter.project_slug }}.services.s3_service import S3Service


@pytest.mark.unit
class TestS3Service:
    def test_upload_and_download_bytes(self, s3_service: S3Service) -> None:
        payload = b"hello world"
        s3_service.upload_bytes("test/data.txt", payload)
        result = s3_service.download_bytes("test/data.txt")
        assert result == payload

    def test_list_objects(self, s3_service: S3Service) -> None:
        s3_service.upload_bytes("prefix/a.txt", b"a")
        s3_service.upload_bytes("prefix/b.txt", b"b")
        s3_service.upload_bytes("other/c.txt", b"c")
        keys = s3_service.list_objects(prefix="prefix/")
        assert set(keys) == {"prefix/a.txt", "prefix/b.txt"}

    def test_object_exists(self, s3_service: S3Service) -> None:
        assert not s3_service.object_exists("missing.txt")
        s3_service.upload_bytes("exists.txt", b"data")
        assert s3_service.object_exists("exists.txt")

    def test_delete_object(self, s3_service: S3Service) -> None:
        s3_service.upload_bytes("to_delete.txt", b"data")
        s3_service.delete_object("to_delete.txt")
        assert not s3_service.object_exists("to_delete.txt")
{%- else -%}
# S3 service tests are disabled (use_s3 == "no").
{%- endif %}
