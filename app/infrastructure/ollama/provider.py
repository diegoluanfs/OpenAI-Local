from collections.abc import AsyncIterator
from typing import Any

from app.domain.interfaces import LLMProvider
from app.infrastructure.ollama.client import OllamaClient


class OllamaProvider(LLMProvider):
    def __init__(self, client: OllamaClient) -> None:
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
        return await self._client.generate(model, prompt, temperature, max_tokens, stream)

    async def embeddings(self, model: str, text: str) -> dict[str, Any]:
        return await self._client.embeddings(model, text)

    async def list_models(self) -> list[dict[str, Any]]:
        result = await self._client.tags()
        return result.get("models", [])

    async def pull_model(self, model: str) -> dict[str, Any]:
        return await self._client.pull(model)

    async def health(self) -> bool:
        await self._client.tags()
        return True

    async def close(self) -> None:
        await self._client.close()
