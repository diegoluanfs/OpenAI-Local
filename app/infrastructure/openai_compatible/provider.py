from collections.abc import AsyncIterator
from typing import Any

from app.core.exceptions import OperationNotSupportedError
from app.domain.interfaces import LLMProvider
from app.infrastructure.openai_compatible.client import OpenAICompatibleClient


class OpenAICompatibleProvider(LLMProvider):
    def __init__(self, client: OpenAICompatibleClient) -> None:
        self._client = client

    async def chat(
        self,
        model: str,
        messages: list[dict[str, Any]],
        temperature: float | None,
        max_tokens: int | None,
        stream: bool,
    ) -> dict[str, Any] | AsyncIterator[dict[str, Any]]:
        return await self._client.chat(model, messages, temperature, max_tokens, stream)

    async def completion(
        self,
        model: str,
        prompt: str,
        temperature: float | None,
        max_tokens: int | None,
        stream: bool,
    ) -> dict[str, Any] | AsyncIterator[dict[str, Any]]:
        return await self._client.completion(model, prompt, temperature, max_tokens, stream)

    async def embeddings(self, model: str, text: str) -> dict[str, Any]:
        return await self._client.embeddings(model, text)

    async def list_models(self) -> list[dict[str, Any]]:
        models = await self._client.models()
        return [{"name": model.get("id", ""), **model} for model in models]

    async def pull_model(self, model: str) -> dict[str, Any]:
        raise OperationNotSupportedError(f"Model pulling is not supported by the OpenAI-compatible provider: {model}")

    async def health(self) -> bool:
        return await self._client.health()

    async def close(self) -> None:
        await self._client.close()
