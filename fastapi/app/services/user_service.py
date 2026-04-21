"""User business logic.

The service owns the unit-of-work: it decides when to commit, when to emit
events, and translates persistence-level collisions into domain errors.
"""

from __future__ import annotations

from uuid import UUID

import structlog
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ConflictError
from app.dao.user import user_dao
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate

logger = structlog.get_logger(__name__)


class UserService:
    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def register(self, payload: UserCreate) -> User:
        if await user_dao.get_by_email(self._db, email=payload.email) is not None:
            raise ConflictError("A user with that email already exists.")

        user = await user_dao.create_with_password(self._db, payload=payload)
        await self._db.commit()
        logger.info("user.registered", user_id=str(user.id), email=user.email)
        return user

    async def get(self, user_id: UUID) -> User:
        return await user_dao.get_or_raise(self._db, user_id)

    async def update(self, user_id: UUID, payload: UserUpdate) -> User:
        user = await user_dao.get_or_raise(self._db, user_id)

        # Password needs hashing — handled by DAO; other fields pass through.
        new_password = payload.password
        data = payload.model_dump(exclude_unset=True, exclude={"password"})

        if data:
            user = await user_dao.update(self._db, db_obj=user, payload=data)
        if new_password is not None:
            user = await user_dao.set_password(
                self._db, user=user, new_password=new_password
            )

        await self._db.commit()
        return user

    async def deactivate(self, user_id: UUID) -> User:
        user = await user_dao.get_or_raise(self._db, user_id)
        user = await user_dao.update(self._db, db_obj=user, payload={"is_active": False})
        await self._db.commit()
        logger.info("user.deactivated", user_id=str(user.id))
        return user
