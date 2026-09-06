import hashlib
from fastapi import Depends, Header, HTTPException, Request, status

from app.container import AppContainer


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
        request.state.api_key_fingerprint = hashlib.sha256(token.encode("utf-8")).hexdigest()[:12]
        return

    request.state.is_authenticated = False
    request.state.api_key_fingerprint = None

    if not settings.allow_anonymous_requests:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "message": "API Key is required",
                "type": "authentication_error",
                "code": "api_key_required",
            },
        )
    # Anonymous requests are allowed, but throttled separately.
    if settings.unauth_rate_limit_per_minute <= 0:
        return

    client_ip = request.client.host if request.client else "unknown"
    allowed = await request.app.state.container.rate_limiter.allow(
        key=f"anonymous:{client_ip}",
        limit=settings.unauth_rate_limit_per_minute,
    )
    if not allowed:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            headers={
                "Retry-After": "60",
                "X-RateLimit-Limit": str(settings.unauth_rate_limit_per_minute),
                "X-RateLimit-Remaining": "0",
            },
            detail={
                "message": "Rate limit exceeded for requests without API key",
                "type": "rate_limit_error",
                "code": "unauthenticated_rate_limit_exceeded",
            },
        )

