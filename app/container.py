import time

from app.core.config import Settings
from app.domain.rate_limiter import RateLimiter
from app.infrastructure.ollama.client import OllamaClient
from app.infrastructure.ollama.provider import OllamaProvider
from app.infrastructure.repositories import InMemoryModelRepository
from app.infrastructure.rate_limiter import InMemoryRateLimiter
from app.infrastructure.redis_rate_limiter import RedisRateLimiter
from app.services.health_service import HealthService
from app.services.llm_service import LLMService


class AppContainer:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.started_at = time.time()

        ollama_client = OllamaClient(
            base_url=settings.ollama_url,
            timeout_seconds=settings.timeout_seconds,
            timeout_tags_seconds=settings.timeout_tags_seconds,
            timeout_chat_seconds=settings.timeout_chat_seconds,
            timeout_generate_seconds=settings.timeout_generate_seconds,
            timeout_embeddings_seconds=settings.timeout_embeddings_seconds,
            timeout_pull_seconds=settings.timeout_pull_seconds,
            max_connections=settings.httpx_max_connections,
            max_keepalive_connections=settings.httpx_max_keepalive_connections,
        )
        self.provider = OllamaProvider(ollama_client)
        memory_rate_limiter = InMemoryRateLimiter()
        rate_limiter: RateLimiter = memory_rate_limiter
        if settings.rate_limit_backend == "redis" and settings.redis_url:
            rate_limiter = RedisRateLimiter(
                url=settings.redis_url,
                key_prefix=settings.redis_key_prefix,
                fallback=memory_rate_limiter,
            )
        self.rate_limiter = rate_limiter
        self.models = InMemoryModelRepository(
            self.provider,
            settings.default_model,
            cache_ttl_seconds=settings.model_cache_ttl_seconds,
        )
        self.llm_service = LLMService(self.provider, self.models, settings.embedding_model)
        self.health_service = HealthService(self.provider, self.models, self.started_at)

    async def close(self) -> None:
        await self.provider.close()
        close_rate_limiter = getattr(self.rate_limiter, "close", None)
        if close_rate_limiter:
            await close_rate_limiter()
