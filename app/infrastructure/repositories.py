from app.domain.interfaces import LLMProvider, ModelRepository


class InMemoryModelRepository(ModelRepository):
    def __init__(self, provider: LLMProvider, default_model: str) -> None:
        self._provider = provider
        self._default_model = default_model

    async def list_models(self) -> list[dict]:
        return await self._provider.list_models()

    async def get_default_model(self) -> str:
        return self._default_model

    async def set_default_model(self, model: str) -> str:
        self._default_model = model
        return self._default_model

    async def model_exists(self, model: str) -> bool:
        models = await self.list_models()
        names = {m.get("name", "") for m in models}
        return model in names
