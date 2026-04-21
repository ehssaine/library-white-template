from __future__ import annotations

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ConflictError
from app.schemas.user import UserCreate
from app.services.user_service import UserService


@pytest.mark.asyncio
async def test_register_creates_user(db_session: AsyncSession) -> None:
    service = UserService(db_session)
    user = await service.register(
        UserCreate(email="alice@example.com", password="correct-horse-battery", full_name="Alice")
    )
    assert user.id is not None
    assert user.email == "alice@example.com"
    assert user.hashed_password != "correct-horse-battery"


@pytest.mark.asyncio
async def test_register_duplicate_email_raises_conflict(db_session: AsyncSession) -> None:
    service = UserService(db_session)
    payload = UserCreate(email="bob@example.com", password="correct-horse-battery")
    await service.register(payload)

    with pytest.raises(ConflictError):
        await service.register(payload)
