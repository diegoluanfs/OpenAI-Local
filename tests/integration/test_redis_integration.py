import os

import pytest

from app.infrastructure.redis_rate_limiter import RedisRateLimiter


@pytest.mark.asyncio
async def test_real_redis_rate_limiter():
    redis_url = os.getenv("REDIS_URL")
    if not redis_url:
        pytest.skip("REDIS_URL not configured")

    limiter = RedisRateLimiter(redis_url, "integration-test")
    key = "integration-client"
    try:
        await limiter._client.delete(f"integration-test:{key}")
        assert await limiter.allow(key, limit=2)
        assert await limiter.allow(key, limit=2)
        assert not await limiter.allow(key, limit=2)
    finally:
        await limiter._client.delete(f"integration-test:{key}")
        await limiter.close()
