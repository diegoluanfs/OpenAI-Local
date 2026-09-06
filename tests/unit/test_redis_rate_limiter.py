import pytest

from app.infrastructure.rate_limiter import InMemoryRateLimiter
from app.infrastructure.redis_rate_limiter import RedisRateLimiter


class FakePipeline:
    def __init__(self, result: list[int]) -> None:
        self.result = result
        self.commands: list[tuple[str, object]] = []

    async def __aenter__(self):
        return self

    async def __aexit__(self, *_):
        return None

    def incr(self, key: str):
        self.commands.append(("incr", key))

    def expire(self, key: str, seconds: int):
        self.commands.append(("expire", (key, seconds)))

    async def execute(self):
        return self.result


class FakeRedis:
    def __init__(self, result: list[int] | None = None, error: Exception | None = None) -> None:
        self.result = result or [1, True]
        self.error = error
        self.last_pipeline: FakePipeline | None = None

    def pipeline(self, transaction: bool = True):
        if self.error:
            raise self.error
        self.last_pipeline = FakePipeline(self.result)
        return self.last_pipeline

    async def aclose(self):
        return None


@pytest.mark.asyncio
async def test_redis_rate_limiter_uses_prefixed_key_and_limit():
    client = FakeRedis(result=[1, True])
    limiter = RedisRateLimiter("redis://unused", "prefix", client=client)

    allowed = await limiter.allow("client", limit=1)

    assert allowed
    assert client.last_pipeline is not None
    assert ("incr", "prefix:client") in client.last_pipeline.commands


@pytest.mark.asyncio
async def test_redis_rate_limiter_falls_back_to_memory_on_failure():
    limiter = RedisRateLimiter(
        "redis://unused",
        "prefix",
        fallback=InMemoryRateLimiter(),
        client=FakeRedis(error=ConnectionError("redis unavailable")),
    )

    assert await limiter.allow("client", limit=1)
    assert not await limiter.allow("client", limit=1)
