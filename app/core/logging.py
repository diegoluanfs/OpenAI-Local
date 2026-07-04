import logging
import time

from pythonjsonlogger import jsonlogger
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request


def setup_logging(level: str) -> None:
    root = logging.getLogger()
    root.setLevel(level)

    if root.handlers:
        for handler in root.handlers:
            root.removeHandler(handler)

    handler = logging.StreamHandler()
    formatter = jsonlogger.JsonFormatter(
        "%(asctime)s %(levelname)s %(name)s %(message)s %(method)s %(path)s %(status_code)s %(duration_ms)s"
    )
    handler.setFormatter(formatter)
    root.addHandler(handler)


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        logger = logging.getLogger("local_llm.request")
        start = time.perf_counter()
        try:
            response = await call_next(request)
            duration_ms = round((time.perf_counter() - start) * 1000, 2)
            logger.info(
                "request_completed",
                extra={
                    "method": request.method,
                    "path": request.url.path,
                    "status_code": response.status_code,
                    "duration_ms": duration_ms,
                },
            )
            response.headers["X-Process-Time-Ms"] = str(duration_ms)
            return response
        except Exception:
            duration_ms = round((time.perf_counter() - start) * 1000, 2)
            logger.exception(
                "request_failed",
                extra={
                    "method": request.method,
                    "path": request.url.path,
                    "status_code": 500,
                    "duration_ms": duration_ms,
                },
            )
            raise
