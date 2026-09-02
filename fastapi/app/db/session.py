"""Async engine, session factory, and the ``get_db`` FastAPI dependency.

This is the single place where a DB connection is created. Everything else
(DAO, service, router) receives an ``AsyncSession`` via dependency injection
so tests can swap in an in-memory SQLite or a test transaction.
"""

from __future__ import annotations

from collections.abc import AsyncIterator

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.core.config import Settings, get_settings


def build_engine(settings: Settings) -> AsyncEngine:
    """Build the async engine. Exposed as a function so tests can build
    alternate engines (e.g. SQLite in-memory)."""
    db = settings.db
    return create_async_engine(
        db.async_dsn,
        echo=db.echo,
        pool_size=db.pool_size,
        max_overflow=db.max_overflow,
        pool_timeout=db.pool_timeout,
        pool_recycle=db.pool_recycle,
        pool_pre_ping=True,  # validates connection before use — handles dropped conns
        future=True,
    )


_settings = get_settings()
engine: AsyncEngine = build_engine(_settings)

# expire_on_commit=False keeps ORM objects usable after commit, which
# simplifies returning them from services.
SessionLocal: async_sessionmaker[AsyncSession] = async_sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
    expire_on_commit=False,
    class_=AsyncSession,
)


async def get_db() -> AsyncIterator[AsyncSession]:
    """FastAPI dependency yielding a session scoped to one request.

    The session is closed automatically. Commit/rollback is the *service
    layer's* responsibility — we do NOT auto-commit here, to keep the
    unit-of-work boundary explicit.
    """
    async with SessionLocal() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise


async def dispose_engine() -> None:
    """Dispose of the connection pool. Called on app shutdown."""
    await engine.dispose()
