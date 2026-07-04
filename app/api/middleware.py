import time
from collections import defaultdict, deque

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse


class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, limit_per_minute: int) -> None:
        super().__init__(app)
        self.limit_per_minute = limit_per_minute
        self.requests: dict[str, deque[float]] = defaultdict(deque)

    async def dispatch(self, request: Request, call_next):
        if self.limit_per_minute <= 0:
            return await call_next(request)

        client = request.client.host if request.client else "unknown"
        now = time.time()
        window_start = now - 60

        bucket = self.requests[client]
        while bucket and bucket[0] < window_start:
            bucket.popleft()

        if len(bucket) >= self.limit_per_minute:
            return JSONResponse(
                status_code=429,
                content={
                    "error": {
                        "message": "Rate limit exceeded",
                        "type": "rate_limit_error",
                        "code": "rate_limit_exceeded",
                    }
                },
            )

        bucket.append(now)
        return await call_next(request)
