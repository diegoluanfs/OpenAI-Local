import asyncio
from datetime import datetime, timezone
import logging

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.middleware import RateLimitMiddleware
from app.api.routes import ask, chat, completions, embeddings, health, models
from app.container import AppContainer
from app.core.config import Settings, get_settings
from app.core.exceptions import LocalLLMError
from app.core.logging import RequestLoggingMiddleware, setup_logging


def _parse_cors(origins: str) -> list[str]:
    if origins.strip() == "*":
        return ["*"]
    return [origin.strip() for origin in origins.split(",") if origin.strip()]


def _error_response(
    request: Request,
    status_code: int,
    message: str,
    error_type: str,
    code: str,
    details: list[dict] | None = None,
) -> JSONResponse:
    request_id = getattr(request.state, "request_id", None)
    payload = {
        "error": {
            "message": message,
            "type": error_type,
            "code": code,
            "request_id": request_id,
            "path": request.url.path,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
    }
    if details:
        payload["error"]["details"] = details
    return JSONResponse(status_code=status_code, content=payload)


def create_app(settings: Settings | None = None) -> FastAPI:
    settings = settings or get_settings()
    setup_logging(settings.log_level)

    app = FastAPI(
        title="Local LLM Server",
        description="OpenAI-compatible local LLM server powered by Ollama.",
        version="1.0.0",
    )
    app.state.settings = settings
    app.state.container = AppContainer(settings)

    app.add_middleware(RequestLoggingMiddleware)
    app.add_middleware(RateLimitMiddleware, limit_per_minute=settings.rate_limit_per_minute)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=_parse_cors(settings.cors_origins),
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(chat.router)
    app.include_router(completions.router)
    app.include_router(embeddings.router)
    app.include_router(ask.router)
    app.include_router(models.router)
    app.include_router(health.router)

    logger = logging.getLogger("local_llm.app")

    @app.exception_handler(LocalLLMError)
    async def local_llm_error_handler(request: Request, exc: LocalLLMError):
        logger.exception("domain_error")
        return _error_response(
            request=request,
            status_code=status.HTTP_400_BAD_REQUEST,
            message=str(exc),
            error_type="local_llm_error",
            code="bad_request",
        )

    @app.exception_handler(RequestValidationError)
    async def validation_error_handler(request: Request, exc: RequestValidationError):
        return _error_response(
            request=request,
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            message="Validation failed",
            error_type="invalid_request_error",
            code="validation_error",
            details=exc.errors(),
        )

    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException):
        detail = exc.detail
        if isinstance(detail, dict):
            message = str(detail.get("message", "Request failed"))
            error_type = str(detail.get("type", "http_error"))
            code = str(detail.get("code", "http_error"))
            details = detail.get("details")
        else:
            message = str(detail)
            error_type = "http_error"
            code = "http_error"
            details = None

        return _error_response(
            request=request,
            status_code=exc.status_code,
            message=message,
            error_type=error_type,
            code=code,
            details=details,
        )

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(request: Request, _: Exception):
        logger.exception("unhandled_error")
        return _error_response(
            request=request,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message="Internal server error",
            error_type="internal_server_error",
            code="internal_error",
        )

    @app.on_event("startup")
    async def startup_event():
        if settings.auto_pull_default_model:
            async def _pull_default_model() -> None:
                try:
                    if not await app.state.container.llm_service.ensure_model_available(settings.default_model):
                        logger.info("pulling_default_model", extra={"model": settings.default_model})
                        await app.state.container.llm_service.pull_model(settings.default_model)
                except Exception:
                    logger.exception("failed_to_pull_default_model")

            asyncio.create_task(_pull_default_model())

    @app.on_event("shutdown")
    async def shutdown_event():
        await app.state.container.close()

    return app


app = create_app()