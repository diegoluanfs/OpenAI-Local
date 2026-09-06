import asyncio

import httpx
import pytest

from app.core.config import Settings
from app.main import create_app


@pytest.mark.asyncio
async def test_liveness_handles_concurrent_requests():
    app = create_app(Settings(auto_pull_default_model=False))
    transport = httpx.ASGITransport(app=app)

    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        responses = await asyncio.gather(
            *(client.get("/health/live") for _ in range(20))
        )

    assert all(response.status_code == 200 for response in responses)
    assert all(response.json()["status"] == "alive" for response in responses)
