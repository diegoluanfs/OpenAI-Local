import time
from collections import defaultdict, deque


class InMemoryRateLimiter:
    def __init__(self) -> None:
        self._buckets: dict[str, deque[float]] = defaultdict(deque)

    async def allow(self, key: str, limit: int, window_seconds: int = 60) -> bool:
        if limit <= 0:
            return True

        now = time.time()
        bucket = self._buckets[key]
        window_start = now - window_seconds
        while bucket and bucket[0] < window_start:
            bucket.popleft()

        if len(bucket) >= limit:
            return False

        bucket.append(now)
        return True

    def clear(self) -> None:
        self._buckets.clear()
