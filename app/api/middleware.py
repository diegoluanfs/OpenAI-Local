import asyncio
import time
from collections import defaultdict, deque

from app.core.metrics import observe_request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, StreamingResponse


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
                headers={
                    "Retry-After": "60",
                    "X-RateLimit-Limit": str(self.limit_per_minute),
                    "X-RateLimit-Remaining": "0",
                },
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
                headers={
                    "Retry-After": "1",
                    "X-Inference-Concurrency-Limit": str(self.limit),
                },
                content={
                    "error": {
                        "message": "Inference concurrency limit reached",
                        "type": "rate_limit_error",
                        "code": "inference_concurrency_limit_reached",
                    }
                },
            )

        await self.semaphore.acquire()
        try:
            response = await call_next(request)
        except Exception:
            self.semaphore.release()
            raise

        if not isinstance(response, StreamingResponse):
            self.semaphore.release()
            return response

        body_iterator = response.body_iterator

        async def guarded_body():
            try:
                async for chunk in body_iterator:
                    yield chunk
            finally:
                self.semaphore.release()

        response.body_iterator = guarded_body()
        return response


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "no-referrer"
        response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
        script_sources = "'self' https://cdn.jsdelivr.net"
        if request.url.path == "/docs":
            script_sources += " 'unsafe-inline'"
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; "
            "img-src 'self' data: https://fastapi.tiangolo.com; "
            "style-src 'self' https://cdn.jsdelivr.net https://fonts.googleapis.com; "
            "font-src 'self' https://fonts.gstatic.com; "
            f"script-src {script_sources}; "
            "connect-src 'self' https://cdn.jsdelivr.net"
        )
        return response


class RequestBodyLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, max_body_bytes: int) -> None:
        super().__init__(app)
        self.max_body_bytes = max_body_bytes

    async def dispatch(self, request: Request, call_next):
        content_length = request.headers.get("content-length")
        if self.max_body_bytes > 0 and content_length:
            try:
                body_size = int(content_length)
            except ValueError:
                body_size = 0

            if body_size > self.max_body_bytes:
                return JSONResponse(
                    status_code=413,
                    content={
                        "error": {
                            "message": "Request body exceeds configured limit",
                            "type": "request_too_large",
                            "code": "request_body_too_large",
                        }
                    },
                )

        return await call_next(request)
