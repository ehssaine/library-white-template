"""Generic HTTP connector with retry, timeout, and auth support.

Built on ``httpx`` for both sync and async usage.
"""

from __future__ import annotations

from typing import Any

import httpx
import structlog

from {{ cookiecutter.project_slug }}.config.settings import Settings

logger = structlog.get_logger(__name__)

{% if cookiecutter.include_api_connector == "yes" %}

class HTTPConnector:
    """Reusable HTTP client preconfigured from application settings.

    Parameters
    ----------
    base_url:
        Override the default ``APISettings.base_url``.
    api_key:
        Override the default ``APISettings.key``.
    timeout:
        Per-request timeout in seconds.
    max_retries:
        Number of automatic retries on transient errors.
    """

    def __init__(
        self,
        *,
        base_url: str | None = None,
        api_key: str | None = None,
        timeout: int | None = None,
        max_retries: int | None = None,
    ) -> None:
        settings = Settings().api
        self._base_url = (base_url or settings.base_url).rstrip("/")
        self._api_key = api_key or settings.key
        self._timeout = timeout or settings.timeout
        self._max_retries = max_retries or settings.max_retries

        transport = httpx.HTTPTransport(retries=self._max_retries)
        self._client = httpx.Client(
            base_url=self._base_url,
            timeout=self._timeout,
            transport=transport,
            headers=self._default_headers(),
        )

    def _default_headers(self) -> dict[str, str]:
        headers: dict[str, str] = {"Accept": "application/json"}
        if self._api_key:
            headers["Authorization"] = f"Bearer {self._api_key}"
        return headers

    def get(self, path: str, *, params: dict[str, Any] | None = None) -> Any:
        """Send a GET request and return decoded JSON."""
        logger.info("http.get", url=f"{self._base_url}{path}")
        response = self._client.get(path, params=params)
        response.raise_for_status()
        return response.json()

    def post(self, path: str, *, json: Any = None, data: Any = None) -> Any:
        """Send a POST request and return decoded JSON."""
        logger.info("http.post", url=f"{self._base_url}{path}")
        response = self._client.post(path, json=json, data=data)
        response.raise_for_status()
        return response.json()

    def put(self, path: str, *, json: Any = None) -> Any:
        """Send a PUT request and return decoded JSON."""
        logger.info("http.put", url=f"{self._base_url}{path}")
        response = self._client.put(path, json=json)
        response.raise_for_status()
        return response.json()

    def delete(self, path: str) -> None:
        """Send a DELETE request."""
        logger.info("http.delete", url=f"{self._base_url}{path}")
        response = self._client.delete(path)
        response.raise_for_status()

    def close(self) -> None:
        """Close the underlying connection pool."""
        self._client.close()

    def __enter__(self) -> HTTPConnector:
        return self

    def __exit__(self, *exc: object) -> None:
        self.close()

{% else %}

class HTTPConnector:
    """Reusable HTTP client.

    Parameters
    ----------
    base_url:
        Base URL for the API.
    timeout:
        Per-request timeout in seconds.
    max_retries:
        Number of automatic retries on transient errors.
    headers:
        Extra headers merged into every request.
    """

    def __init__(
        self,
        *,
        base_url: str,
        timeout: int = 30,
        max_retries: int = 3,
        headers: dict[str, str] | None = None,
    ) -> None:
        self._base_url = base_url.rstrip("/")
        transport = httpx.HTTPTransport(retries=max_retries)
        default_headers = {"Accept": "application/json"}
        if headers:
            default_headers.update(headers)
        self._client = httpx.Client(
            base_url=self._base_url,
            timeout=timeout,
            transport=transport,
            headers=default_headers,
        )

    def get(self, path: str, *, params: dict[str, Any] | None = None) -> Any:
        logger.info("http.get", url=f"{self._base_url}{path}")
        response = self._client.get(path, params=params)
        response.raise_for_status()
        return response.json()

    def post(self, path: str, *, json: Any = None, data: Any = None) -> Any:
        logger.info("http.post", url=f"{self._base_url}{path}")
        response = self._client.post(path, json=json, data=data)
        response.raise_for_status()
        return response.json()

    def close(self) -> None:
        self._client.close()

    def __enter__(self) -> HTTPConnector:
        return self

    def __exit__(self, *exc: object) -> None:
        self.close()

{% endif %}
