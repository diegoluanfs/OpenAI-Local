import pytest

from app.infrastructure.rate_limiter import InMemoryRateLimiter


@pytest.mark.asyncio
async def test_in_memory_rate_limiter_enforces_limit():
    limiter = InMemoryRateLimiter()

    assert await limiter.allow("client", limit=2)
    assert await limiter.allow("client", limit=2)
    assert not await limiter.allow("client", limit=2)


@pytest.mark.asyncio
async def test_in_memory_rate_limiter_keeps_keys_isolated():
    limiter = InMemoryRateLimiter()

    assert await limiter.allow("client-a", limit=1)
    assert await limiter.allow("client-b", limit=1)
    assert not await limiter.allow("client-a", limit=1)
