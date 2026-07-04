import time

import psutil

from app.domain.interfaces import LLMProvider, ModelRepository


class HealthService:
    def __init__(self, provider: LLMProvider, models: ModelRepository, started_at: float) -> None:
        self._provider = provider
        self._models = models
        self._started_at = started_at

    async def status(self) -> dict:
        process = psutil.Process()
        memory_mb = process.memory_info().rss / (1024 * 1024)
        try:
            ollama_online = await self._provider.health()
        except Exception:
            ollama_online = False

        return {
            "api_online": True,
            "ollama_online": ollama_online,
            "default_model": await self._models.get_default_model(),
            "memory_used_mb": round(memory_mb, 2),
            "uptime_seconds": round(time.time() - self._started_at, 2),
        }
