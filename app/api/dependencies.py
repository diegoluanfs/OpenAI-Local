import time
from collections import defaultdict, deque

from fastapi import Depends, Header, HTTPException, Request, status

from app.container import AppContainer


_unauth_request_buckets: dict[str, deque[float]] = defaultdict(deque)


def get_container(request: Request) -> AppContainer:
    return request.app.state.container


def get_llm_service(container: AppContainer = Depends(get_container)):
    return container.llm_service


def get_health_service(container: AppContainer = Depends(get_container)):
    return container.health_service


async def validate_api_key(
    request: Request,
    authorization: str | None = Header(default=None),
    x_api_key: str | None = Header(default=None),
) -> None:
    settings = request.app.state.settings
    allowed_keys = settings.allowed_api_keys_set

    token = None
    if authorization and authorization.lower().startswith("bearer "):
        token = authorization.split(" ", 1)[1].strip()
    elif x_api_key:
        token = x_api_key.strip()

    if token:
        if token not in allowed_keys:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={
                    "message": "Invalid API Key",
                    "type": "authentication_error",
                    "code": "invalid_api_key",
                },
            )
        request.state.is_authenticated = True
        return

    request.state.is_authenticated = False

    # Anonymous requests are allowed, but throttled separately.
    if settings.unauth_rate_limit_per_minute <= 0:
        return

    now = time.time()
    window_start = now - 60
    client_ip = request.client.host if request.client else "unknown"
    bucket = _unauth_request_buckets[client_ip]
    while bucket and bucket[0] < window_start:
        bucket.popleft()

    if len(bucket) >= settings.unauth_rate_limit_per_minute:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail={
                "message": "Rate limit exceeded for requests without API key",
                "type": "rate_limit_error",
                "code": "unauthenticated_rate_limit_exceeded",
            },
        )

    bucket.append(now)
