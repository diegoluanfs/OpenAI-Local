import time

from app.domain.interfaces import LLMProvider, ModelRepository


class InMemoryModelRepository(ModelRepository):
    def __init__(self, provider: LLMProvider, default_model: str, cache_ttl_seconds: float = 5.0) -> None:
        self._provider = provider
        self._default_model = default_model
        self._cache_ttl_seconds = cache_ttl_seconds
        self._models_cache: list[dict] | None = None
        self._models_cache_expire_at: float = 0.0

    async def list_models(self, force_refresh: bool = False) -> list[dict]:
        now = time.time()
        if not force_refresh and self._models_cache is not None and now < self._models_cache_expire_at:
            return self._models_cache

        models = await self._provider.list_models()
        self._models_cache = models
        self._models_cache_expire_at = now + self._cache_ttl_seconds
        return models

    async def get_default_model(self) -> str:
        return self._default_model

    async def set_default_model(self, model: str) -> str:
        self._default_model = model
        return self._default_model

    async def model_exists(self, model: str) -> bool:
        models = await self.list_models()
        names = {m.get("name", "") for m in models}
        return model in names

    def invalidate_models_cache(self) -> None:
        self._models_cache = None
        self._models_cache_expire_at = 0.0
