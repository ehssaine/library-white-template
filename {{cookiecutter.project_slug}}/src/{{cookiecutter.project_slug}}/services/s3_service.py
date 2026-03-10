"""S3 service for object storage operations.

Provides a thin, typed wrapper around ``boto3`` that centralises bucket access,
supports custom endpoints (MinIO, LocalStack …), and adds structured logging.
"""

from __future__ import annotations

import io
from typing import TYPE_CHECKING

import boto3
import structlog

if TYPE_CHECKING:
    from mypy_boto3_s3 import S3Client

from {{ cookiecutter.project_slug }}.config.settings import S3Settings, Settings

logger = structlog.get_logger(__name__)


class S3Service:
    """Manage interactions with a single S3 bucket.

    Parameters
    ----------
    settings:
        Optional ``S3Settings`` instance.  When *None* the settings are read
        from the environment / ``.env`` file via :class:`Settings`.
    """

    def __init__(self, settings: S3Settings | None = None) -> None:
        self._settings = settings or Settings().s3
        self._client: S3Client = self._build_client()

    def _build_client(self) -> S3Client:
        kwargs: dict[str, str] = {"region_name": self._settings.region}
        if self._settings.endpoint_url:
            kwargs["endpoint_url"] = self._settings.endpoint_url
        if self._settings.access_key_id:
            kwargs["aws_access_key_id"] = self._settings.access_key_id
        if self._settings.secret_access_key:
            kwargs["aws_secret_access_key"] = self._settings.secret_access_key
        return boto3.client("s3", **kwargs)  # type: ignore[arg-type]

    @property
    def bucket(self) -> str:
        return self._settings.bucket_name

    # ------------------------------------------------------------------
    # Upload
    # ------------------------------------------------------------------
    def upload_bytes(self, key: str, data: bytes, content_type: str = "application/octet-stream") -> None:
        """Upload raw bytes to S3."""
        logger.info("s3.upload", bucket=self.bucket, key=key, size=len(data))
        self._client.put_object(
            Bucket=self.bucket,
            Key=key,
            Body=data,
            ContentType=content_type,
        )

    def upload_file(self, key: str, file_path: str) -> None:
        """Upload a local file to S3."""
        logger.info("s3.upload_file", bucket=self.bucket, key=key, file=file_path)
        self._client.upload_file(Filename=file_path, Bucket=self.bucket, Key=key)

    # ------------------------------------------------------------------
    # Download
    # ------------------------------------------------------------------
    def download_bytes(self, key: str) -> bytes:
        """Download an object and return its bytes."""
        logger.info("s3.download", bucket=self.bucket, key=key)
        response = self._client.get_object(Bucket=self.bucket, Key=key)
        return response["Body"].read()  # type: ignore[union-attr]

    def download_file(self, key: str, destination: str) -> None:
        """Download an object to a local file."""
        logger.info("s3.download_file", bucket=self.bucket, key=key, dest=destination)
        self._client.download_file(Bucket=self.bucket, Key=key, Filename=destination)

    def download_fileobj(self, key: str) -> io.BytesIO:
        """Download an object into an in-memory file-like object."""
        buf = io.BytesIO()
        self._client.download_fileobj(Bucket=self.bucket, Key=key, Fileobj=buf)
        buf.seek(0)
        return buf

    # ------------------------------------------------------------------
    # List / Delete
    # ------------------------------------------------------------------
    def list_objects(self, prefix: str = "", max_keys: int = 1000) -> list[str]:
        """List object keys under *prefix*."""
        logger.info("s3.list", bucket=self.bucket, prefix=prefix)
        paginator = self._client.get_paginator("list_objects_v2")
        keys: list[str] = []
        for page in paginator.paginate(Bucket=self.bucket, Prefix=prefix, PaginationConfig={"MaxItems": max_keys}):
            for obj in page.get("Contents", []):
                keys.append(obj["Key"])
        return keys

    def delete_object(self, key: str) -> None:
        """Delete a single object."""
        logger.info("s3.delete", bucket=self.bucket, key=key)
        self._client.delete_object(Bucket=self.bucket, Key=key)

    def object_exists(self, key: str) -> bool:
        """Return *True* if the object exists in the bucket."""
        try:
            self._client.head_object(Bucket=self.bucket, Key=key)
        except self._client.exceptions.ClientError:
            return False
        return True

    # ------------------------------------------------------------------
    # Presigned URLs
    # ------------------------------------------------------------------
    def generate_presigned_url(self, key: str, expiration: int = 3600) -> str:
        """Generate a presigned URL for downloading *key*."""
        return self._client.generate_presigned_url(
            "get_object",
            Params={"Bucket": self.bucket, "Key": key},
            ExpiresIn=expiration,
        )
