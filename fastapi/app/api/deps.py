"""Reusable FastAPI dependencies.

Keep dependencies thin — they wire together (DB session + settings + auth)
and produce either a primitive (e.g. current user) or a ready-to-use service.
"""

from __future__ import annotations

from typing import Annotated
from uuid import UUID

import jwt
from fastapi import Depends, Header
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import Settings, get_settings
from app.core.exceptions import ForbiddenError, UnauthorizedError
from app.core.security import decode_access_token
from app.dao.user import user_dao
from app.db.session import get_db
from app.models.user import User
from app.services.auth_service import AuthService
from app.services.user_service import UserService

SettingsDep = Annotated[Settings, Depends(get_settings)]
DbDep = Annotated[AsyncSession, Depends(get_db)]

_oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


async def get_current_user(
    db: DbDep,
    settings: SettingsDep,
    token: Annotated[str, Depends(_oauth2_scheme)],
) -> User:
    try:
        payload = decode_access_token(token, settings.security)
        user_id = UUID(payload["sub"])
    except (jwt.PyJWTError, KeyError, ValueError) as exc:
        raise UnauthorizedError("Invalid authentication token.") from exc

    user = await user_dao.get(db, user_id)
    if user is None or not user.is_active:
        raise UnauthorizedError("User not found or inactive.")
    return user


CurrentUserDep = Annotated[User, Depends(get_current_user)]


async def require_superuser(current_user: CurrentUserDep) -> User:
    if not current_user.is_superuser:
        raise ForbiddenError("Superuser privileges required.")
    return current_user


def get_user_service(db: DbDep) -> UserService:
    return UserService(db)


def get_auth_service(db: DbDep, settings: SettingsDep) -> AuthService:
    return AuthService(db, settings.security)


UserServiceDep = Annotated[UserService, Depends(get_user_service)]
AuthServiceDep = Annotated[AuthService, Depends(get_auth_service)]


async def get_request_id(
    x_request_id: Annotated[str | None, Header(alias="X-Request-ID")] = None,
) -> str | None:
    return x_request_id
