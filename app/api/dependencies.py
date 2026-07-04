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
    if not settings.api_key:
        return

    token = None
    if authorization and authorization.lower().startswith("bearer "):
        token = authorization.split(" ", 1)[1].strip()
    elif x_api_key:
        token = x_api_key

    if token != settings.api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"message": "Invalid API Key", "type": "authentication_error"},
        )
