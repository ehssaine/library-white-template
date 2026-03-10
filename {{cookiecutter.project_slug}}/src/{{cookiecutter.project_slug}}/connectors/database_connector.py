"""Database connector using SQLAlchemy.

Only rendered when ``include_database_connector == "yes"``.
"""
{% if cookiecutter.include_database_connector == "yes" %}
from __future__ import annotations

from collections.abc import Generator
from contextlib import contextmanager
from typing import Any

import structlog
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from {{ cookiecutter.project_slug }}.config.settings import DatabaseSettings, Settings

logger = structlog.get_logger(__name__)


class DatabaseConnector:
    """Thin wrapper around a SQLAlchemy engine and session factory.

    Parameters
    ----------
    settings:
        Optional ``DatabaseSettings``.  Falls back to env-based ``Settings``.
    """

    def __init__(self, settings: DatabaseSettings | None = None) -> None:
        self._settings = settings or Settings().database
        self._engine: Engine = create_engine(
            self._settings.url,
            pool_size=self._settings.pool_size,
            echo=self._settings.echo,
        )
        self._session_factory = sessionmaker(bind=self._engine)

    @contextmanager
    def session(self) -> Generator[Session, None, None]:
        """Provide a transactional session scope."""
        session = self._session_factory()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    def execute(self, query: str, params: dict[str, Any] | None = None) -> list[Any]:
        """Execute a raw SQL query and return rows."""
        with self._engine.connect() as conn:
            result = conn.execute(text(query), params or {})
            return [row._asdict() for row in result]

    def health_check(self) -> bool:
        """Return *True* if the database is reachable."""
        try:
            with self._engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            return True
        except Exception:
            logger.exception("database.health_check_failed")
            return False

    def dispose(self) -> None:
        """Dispose of the connection pool."""
        self._engine.dispose()
{% else %}
# Database connector is disabled.  Enable it by setting
# ``include_database_connector`` to "yes" when generating the project.
{% endif %}
