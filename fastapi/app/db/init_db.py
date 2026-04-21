"""Bootstrap data that must exist in every environment (first superuser,
reference tables). Idempotent — safe to run on every startup."""

from __future__ import annotations

import structlog
from sqlalchemy.ext.asyncio import AsyncSession

from app.dao.user import user_dao
from app.schemas.user import UserCreate

logger = structlog.get_logger(__name__)


async def seed_initial_data(
    db: AsyncSession,
    *,
    admin_email: str,
    admin_password: str,
) -> None:
    existing = await user_dao.get_by_email(db, email=admin_email)
    if existing is not None:
        logger.debug("init_db.admin_exists", email=admin_email)
        return

    await user_dao.create_with_password(
        db,
        payload=UserCreate(email=admin_email, password=admin_password, full_name="Admin"),
        is_superuser=True,
    )
    await db.commit()
    logger.info("init_db.admin_created", email=admin_email)
