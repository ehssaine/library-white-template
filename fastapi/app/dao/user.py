from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import hash_password
from app.dao.base import CRUDBase
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate


class UserDAO(CRUDBase[User, UserCreate, UserUpdate]):
    async def get_by_email(self, db: AsyncSession, *, email: str) -> User | None:
        stmt = select(User).where(User.email == email.lower())
        return await db.scalar(stmt)

    async def create_with_password(
        self,
        db: AsyncSession,
        *,
        payload: UserCreate,
        is_superuser: bool = False,
    ) -> User:
        user = User(
            email=payload.email.lower(),
            hashed_password=hash_password(payload.password),
            full_name=payload.full_name,
            is_superuser=is_superuser,
        )
        db.add(user)
        await db.flush()
        await db.refresh(user)
        return user

    async def set_password(self, db: AsyncSession, *, user: User, new_password: str) -> User:
        user.hashed_password = hash_password(new_password)
        db.add(user)
        await db.flush()
        await db.refresh(user)
        return user


user_dao = UserDAO(User)
