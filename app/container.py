import time

from app.core.config import Settings
from app.infrastructure.ollama.client import OllamaClient
from app.infrastructure.ollama.provider import OllamaProvider
from app.infrastructure.repositories import InMemoryModelRepository
from app.services.health_service import HealthService
from app.services.llm_service import LLMService


class AppContainer:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.started_at = time.time()

        ollama_client = OllamaClient(settings.ollama_url, settings.timeout_seconds)
        self.provider = OllamaProvider(ollama_client)
        self.models = InMemoryModelRepository(self.provider, settings.default_model)
        self.llm_service = LLMService(self.provider, self.models, settings.embedding_model)
        self.health_service = HealthService(self.provider, self.models, self.started_at)

    async def close(self) -> None:
        await self.provider.close()
