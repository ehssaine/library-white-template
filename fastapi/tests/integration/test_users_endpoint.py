from __future__ import annotations

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_register_then_login(client: AsyncClient) -> None:
    r = await client.post(
        "/api/v1/users",
        json={
            "email": "carol@example.com",
            "password": "correct-horse-battery",
            "full_name": "Carol",
        },
    )
    assert r.status_code == 201, r.text
    body = r.json()
    assert body["email"] == "carol@example.com"
    assert "hashed_password" not in body

    r = await client.post(
        "/api/v1/auth/login",
        data={"username": "carol@example.com", "password": "correct-horse-battery"},
    )
    assert r.status_code == 200
    assert r.json()["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_liveness(client: AsyncClient) -> None:
    r = await client.get("/api/v1/health/live")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}
