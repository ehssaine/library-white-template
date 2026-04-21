"""Declarative base and model registry.

Importing every ORM model here ensures they are registered on
``Base.metadata`` before Alembic's autogenerate reads it. If a model is not
imported in this module, Alembic will not see it and will silently miss
migrations.
"""

from __future__ import annotations

from app.models.base import Base  # noqa: F401
from app.models.user import User  # noqa: F401

__all__ = ["Base"]
