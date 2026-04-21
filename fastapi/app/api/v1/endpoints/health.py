from __future__ import annotations

from fastapi import APIRouter, status
from sqlalchemy import text

from app.api.deps import DbDep

router = APIRouter()


@router.get("/health/live", status_code=status.HTTP_200_OK)
async def liveness() -> dict[str, str]:
    """Liveness: does the process respond? No dependencies checked."""
    return {"status": "ok"}


@router.get("/health/ready", status_code=status.HTTP_200_OK)
async def readiness(db: DbDep) -> dict[str, str]:
    """Readiness: can we actually serve traffic? Checks DB connectivity.
    Kubernetes uses this to decide whether to route traffic to the pod."""
    await db.execute(text("SELECT 1"))
    return {"status": "ready"}
