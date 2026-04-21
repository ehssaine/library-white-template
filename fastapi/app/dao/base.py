"""Generic, typed CRUD base for DAOs.

A DAO is **pure persistence** — it does not hash passwords, send emails, or
decide who can do what. Those are service-layer concerns. Keeping this
boundary sharp is what lets you swap the persistence backend or mock the DAO
in unit tests.
"""

from __future__ import annotations

from typing import Any, Generic, TypeVar
from uuid import UUID

from pydantic import BaseModel
from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.base import Base

ModelT = TypeVar("ModelT", bound=Base)
CreateSchemaT = TypeVar("CreateSchemaT", bound=BaseModel)
UpdateSchemaT = TypeVar("UpdateSchemaT", bound=BaseModel)


class CRUDBase(Generic[ModelT, CreateSchemaT, UpdateSchemaT]):
    """CRUD operations common to most aggregates.

    Subclass for entity-specific queries. Do NOT call ``commit`` here — the
    service layer owns the unit-of-work boundary so it can compose multiple
    DAOs inside a single transaction.
    """

    def __init__(self, model: type[ModelT]) -> None:
        self.model = model

    async def get(self, db: AsyncSession, id: UUID) -> ModelT | None:
        return await db.get(self.model, id)

    async def get_or_raise(self, db: AsyncSession, id: UUID) -> ModelT:
        obj = await self.get(db, id)
        if obj is None:
            from app.core.exceptions import NotFoundError

            raise NotFoundError(f"{self.model.__name__} {id} not found")
        return obj

    async def list(
        self,
        db: AsyncSession,
        *,
        offset: int = 0,
        limit: int = 50,
        filters: dict[str, Any] | None = None,
    ) -> list[ModelT]:
        stmt = select(self.model).offset(offset).limit(limit)
        if filters:
            for key, value in filters.items():
                stmt = stmt.where(getattr(self.model, key) == value)
        result = await db.scalars(stmt)
        return list(result.all())

    async def count(
        self, db: AsyncSession, *, filters: dict[str, Any] | None = None
    ) -> int:
        stmt = select(func.count()).select_from(self.model)
        if filters:
            for key, value in filters.items():
                stmt = stmt.where(getattr(self.model, key) == value)
        return int(await db.scalar(stmt) or 0)

    async def create(self, db: AsyncSession, *, payload: CreateSchemaT) -> ModelT:
        obj = self.model(**payload.model_dump())
        db.add(obj)
        await db.flush()  # flush, not commit — service decides when to commit
        await db.refresh(obj)
        return obj

    async def update(
        self,
        db: AsyncSession,
        *,
        db_obj: ModelT,
        payload: UpdateSchemaT | dict[str, Any],
    ) -> ModelT:
        data = (
            payload
            if isinstance(payload, dict)
            else payload.model_dump(exclude_unset=True)
        )
        for field, value in data.items():
            setattr(db_obj, field, value)
        db.add(db_obj)
        await db.flush()
        await db.refresh(db_obj)
        return db_obj

    async def delete(self, db: AsyncSession, *, id: UUID) -> None:
        await db.execute(delete(self.model).where(self.model.id == id))
        await db.flush()
