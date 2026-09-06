import asyncio
import time
from collections import defaultdict, deque

from app.core.metrics import observe_request
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


class MetricsMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        started_at = time.perf_counter()
        response = await call_next(request)
        observe_request(request.method, request.url.path, response.status_code, started_at)
        return response


class InferenceConcurrencyMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, limit: int) -> None:
        super().__init__(app)
        self.limit = limit
        self.semaphore = asyncio.Semaphore(limit) if limit > 0 else None

    async def dispatch(self, request: Request, call_next):
        is_inference = request.url.path == "/ask" or request.url.path.startswith("/v1/")
        if not is_inference or self.semaphore is None:
            return await call_next(request)

        if self.semaphore.locked():
            return JSONResponse(
                status_code=429,
                content={
                    "error": {
                        "message": "Inference concurrency limit reached",
                        "type": "rate_limit_error",
                        "code": "inference_concurrency_limit_reached",
                    }
                },
            )

        async with self.semaphore:
            return await call_next(request)
