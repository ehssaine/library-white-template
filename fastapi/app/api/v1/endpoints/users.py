from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, status

from app.api.deps import CurrentUserDep, UserServiceDep
from app.schemas.user import UserCreate, UserRead, UserUpdate

router = APIRouter()


@router.post(
    "",
    response_model=UserRead,
    status_code=status.HTTP_201_CREATED,
)
async def register_user(
    payload: UserCreate,
    user_service: UserServiceDep,
) -> UserRead:
    user = await user_service.register(payload)
    return UserRead.model_validate(user)


@router.get("/me", response_model=UserRead)
async def get_me(current_user: CurrentUserDep) -> UserRead:
    return UserRead.model_validate(current_user)


@router.patch("/me", response_model=UserRead)
async def update_me(
    payload: UserUpdate,
    current_user: CurrentUserDep,
    user_service: UserServiceDep,
) -> UserRead:
    user = await user_service.update(current_user.id, payload)
    return UserRead.model_validate(user)


@router.get("/{user_id}", response_model=UserRead)
async def get_user(
    user_id: UUID,
    _current_user: CurrentUserDep,
    user_service: UserServiceDep,
) -> UserRead:
    user = await user_service.get(user_id)
    return UserRead.model_validate(user)
