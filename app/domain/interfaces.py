from collections.abc import AsyncIterator
from typing import Any, Protocol


class LLMProvider(Protocol):
    async def chat(
        self,
        model: str,
        messages: list[dict[str, Any]],
        temperature: float | None,
        max_tokens: int | None,
        stream: bool,
    ) -> dict[str, Any] | AsyncIterator[dict[str, Any]]: ...

    async def completion(
        self,
        model: str,
        prompt: str,
        temperature: float | None,
        max_tokens: int | None,
        stream: bool,
    ) -> dict[str, Any] | AsyncIterator[dict[str, Any]]: ...

    async def embeddings(self, model: str, text: str) -> dict[str, Any]: ...

    async def list_models(self) -> list[dict[str, Any]]: ...

    async def pull_model(self, model: str) -> dict[str, Any]: ...

    async def health(self) -> bool: ...


class ModelRepository(Protocol):
    async def list_models(self, force_refresh: bool = False) -> list[dict[str, Any]]: ...

    async def get_default_model(self) -> str: ...

    async def set_default_model(self, model: str) -> str: ...

    async def model_exists(self, model: str) -> bool: ...

    def invalidate_models_cache(self) -> None: ...
