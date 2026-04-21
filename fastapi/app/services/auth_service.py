from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import SecuritySettings
from app.core.exceptions import UnauthorizedError
from app.core.security import create_access_token, verify_password
from app.dao.user import user_dao
from app.models.user import User
from app.schemas.token import Token


class AuthService:
    def __init__(self, db: AsyncSession, security: SecuritySettings) -> None:
        self._db = db
        self._security = security

    async def authenticate(self, email: str, password: str) -> User:
        user = await user_dao.get_by_email(self._db, email=email)
        if user is None or not verify_password(password, user.hashed_password):
            # Same error for both cases — avoid leaking which emails exist.
            raise UnauthorizedError("Incorrect email or password.")
        if not user.is_active:
            raise UnauthorizedError("User is inactive.")
        return user

    async def login(self, email: str, password: str) -> Token:
        user = await self.authenticate(email, password)
        token = create_access_token(
            subject=user.id,
            settings=self._security,
            extra_claims={"is_superuser": user.is_superuser},
        )
        return Token(access_token=token)
