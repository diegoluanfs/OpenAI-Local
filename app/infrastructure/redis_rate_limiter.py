from typing import Any

from redis.asyncio import Redis

from app.infrastructure.rate_limiter import InMemoryRateLimiter


class RedisRateLimiter:
    def __init__(
        self,
        url: str,
        key_prefix: str,
        fallback: InMemoryRateLimiter | None = None,
        client: Any | None = None,
    ) -> None:
        self._client = client or Redis.from_url(url, decode_responses=True)
        self._key_prefix = key_prefix.rstrip(":")
        self._fallback = fallback or InMemoryRateLimiter()

    async def allow(self, key: str, limit: int, window_seconds: int = 60) -> bool:
        if limit <= 0:
            return True

        redis_key = f"{self._key_prefix}:{key}"
        try:
            async with self._client.pipeline(transaction=True) as pipeline:
                pipeline.incr(redis_key)
                pipeline.expire(redis_key, window_seconds)
                result = await pipeline.execute()
            return int(result[0]) <= limit
        except Exception:
            return await self._fallback.allow(key, limit, window_seconds)

    async def close(self) -> None:
        await self._client.aclose()
