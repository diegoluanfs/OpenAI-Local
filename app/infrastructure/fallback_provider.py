from collections.abc import AsyncIterator, Awaitable, Callable
from functools import partial
from typing import Any, TypeVar

from app.core.exceptions import ProviderUnavailableError
from app.domain.interfaces import LLMProvider


T = TypeVar("T")


class FallbackProvider:
    def __init__(self, primary: LLMProvider, fallback: LLMProvider) -> None:
        self._primary = primary
        self._fallback = fallback

    async def chat(
        self,
        model: str,
        messages: list[dict[str, Any]],
        temperature: float | None,
        max_tokens: int | None,
        stream: bool,
    ) -> dict[str, Any] | AsyncIterator[dict[str, Any]]:
        primary_call = partial(self._primary.chat, model, messages, temperature, max_tokens, stream)
        fallback_call = partial(self._fallback.chat, model, messages, temperature, max_tokens, stream)
        if stream:
            return self._stream_with_fallback(primary_call, fallback_call)
        return await self._call_with_fallback(primary_call, fallback_call)

    async def completion(
        self,
        model: str,
        prompt: str,
        temperature: float | None,
        max_tokens: int | None,
        stream: bool,
    ) -> dict[str, Any] | AsyncIterator[dict[str, Any]]:
        primary_call = partial(self._primary.completion, model, prompt, temperature, max_tokens, stream)
        fallback_call = partial(self._fallback.completion, model, prompt, temperature, max_tokens, stream)
        if stream:
            return self._stream_with_fallback(primary_call, fallback_call)
        return await self._call_with_fallback(primary_call, fallback_call)

    async def embeddings(self, model: str, text: str) -> dict[str, Any]:
        return await self._call_with_fallback(
            lambda: self._primary.embeddings(model, text),
            lambda: self._fallback.embeddings(model, text),
        )

    async def list_models(self) -> list[dict[str, Any]]:
        return await self._call_with_fallback(self._primary.list_models, self._fallback.list_models)

    async def pull_model(self, model: str) -> dict[str, Any]:
        return await self._call_with_fallback(
            lambda: self._primary.pull_model(model),
            lambda: self._fallback.pull_model(model),
        )

    async def health(self) -> bool:
        return await self._call_with_fallback(self._primary.health, self._fallback.health)

    async def close(self) -> None:
        await self._primary.close()
        await self._fallback.close()

    async def _call_with_fallback(self, primary_call: Callable[[], Awaitable[T]], fallback_call: Callable[[], Awaitable[T]]) -> T:
        try:
            return await primary_call()
        except ProviderUnavailableError:
            return await fallback_call()

    def _stream_with_fallback(
        self,
        primary_call: Callable[[], Awaitable[AsyncIterator[dict[str, Any]] | dict[str, Any]]],
        fallback_call: Callable[[], Awaitable[AsyncIterator[dict[str, Any]] | dict[str, Any]]],
    ) -> AsyncIterator[dict[str, Any]]:
        async def generator() -> AsyncIterator[dict[str, Any]]:
            started = False
            try:
                primary_stream = await primary_call()
                if isinstance(primary_stream, dict):
                    raise TypeError("Streaming provider returned a dictionary")
                async for chunk in primary_stream:
                    started = True
                    yield chunk
            except ProviderUnavailableError:
                if started:
                    raise
                fallback_stream = await fallback_call()
                if isinstance(fallback_stream, dict):
                    raise TypeError("Streaming fallback provider returned a dictionary")
                async for chunk in fallback_stream:
                    yield chunk

        return generator()
