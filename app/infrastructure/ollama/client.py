from collections.abc import AsyncIterator
from typing import Any

import httpx

from app.core.exceptions import ModelNotFoundError, ProviderUnavailableError


class OllamaClient:
    def __init__(
        self,
        base_url: str,
        timeout_seconds: float,
        timeout_tags_seconds: float,
        timeout_chat_seconds: float,
        timeout_generate_seconds: float,
        timeout_embeddings_seconds: float,
        timeout_pull_seconds: float,
    ) -> None:
        self._client = httpx.AsyncClient(base_url=base_url, timeout=timeout_seconds)
        self._timeout_tags_seconds = timeout_tags_seconds
        self._timeout_chat_seconds = timeout_chat_seconds
        self._timeout_generate_seconds = timeout_generate_seconds
        self._timeout_embeddings_seconds = timeout_embeddings_seconds
        self._timeout_pull_seconds = timeout_pull_seconds

    async def close(self) -> None:
        await self._client.aclose()

    async def tags(self) -> dict[str, Any]:
        try:
            response = await self._client.get("/api/tags", timeout=self._timeout_tags_seconds)
            response.raise_for_status()
            return response.json()
        except httpx.TimeoutException as exc:
            raise ProviderUnavailableError("Ollama tags request timed out.") from exc
        except httpx.HTTPError as exc:
            raise ProviderUnavailableError("Unable to connect to Ollama.") from exc

    async def pull(self, model: str) -> dict[str, Any]:
        final_chunk: dict[str, Any] = {}
        pull_timeout = None if self._timeout_pull_seconds <= 0 else self._timeout_pull_seconds
        async with self._client.stream(
            "POST",
            "/api/pull",
            json={"name": model, "stream": True},
            timeout=pull_timeout,
        ) as response:
            self._raise_for_status(response, model)
            async for line in response.aiter_lines():
                if not line:
                    continue
                final_chunk = httpx.Response(200, content=line).json()

        return final_chunk

    async def chat(
        self,
        model: str,
        messages: list[dict[str, Any]],
        temperature: float | None,
        max_tokens: int | None,
        stream: bool,
    ) -> dict[str, Any] | AsyncIterator[dict[str, Any]]:
        payload: dict[str, Any] = {
            "model": model,
            "messages": messages,
            "stream": stream,
            "options": {},
        }
        if temperature is not None:
            payload["options"]["temperature"] = temperature
        if max_tokens is not None:
            payload["options"]["num_predict"] = max_tokens
        if not payload["options"]:
            payload.pop("options")

        if not stream:
            try:
                response = await self._client.post("/api/chat", json=payload, timeout=self._timeout_chat_seconds)
            except httpx.TimeoutException as exc:
                raise ProviderUnavailableError("Ollama chat request timed out.") from exc
            self._raise_for_status(response, model)
            return response.json()

        return self._stream_json("/api/chat", payload, self._timeout_chat_seconds)

    async def generate(
        self,
        model: str,
        prompt: str,
        temperature: float | None,
        max_tokens: int | None,
        stream: bool,
    ) -> dict[str, Any] | AsyncIterator[dict[str, Any]]:
        payload: dict[str, Any] = {
            "model": model,
            "prompt": prompt,
            "stream": stream,
            "options": {},
        }
        if temperature is not None:
            payload["options"]["temperature"] = temperature
        if max_tokens is not None:
            payload["options"]["num_predict"] = max_tokens
        if not payload["options"]:
            payload.pop("options")

        if not stream:
            try:
                response = await self._client.post(
                    "/api/generate",
                    json=payload,
                    timeout=self._timeout_generate_seconds,
                )
            except httpx.TimeoutException as exc:
                raise ProviderUnavailableError("Ollama generate request timed out.") from exc
            self._raise_for_status(response, model)
            return response.json()

        return self._stream_json("/api/generate", payload, self._timeout_generate_seconds)

    async def embeddings(self, model: str, text: str) -> dict[str, Any]:
        try:
            response = await self._client.post(
                "/api/embeddings",
                json={"model": model, "prompt": text},
                timeout=self._timeout_embeddings_seconds,
            )
        except httpx.TimeoutException as exc:
            raise ProviderUnavailableError("Ollama embeddings request timed out.") from exc
        self._raise_for_status(response, model)
        return response.json()

    async def _stream_json(
        self,
        path: str,
        payload: dict[str, Any],
        timeout_seconds: float,
    ) -> AsyncIterator[dict[str, Any]]:
        async def generator() -> AsyncIterator[dict[str, Any]]:
            try:
                async with self._client.stream("POST", path, json=payload, timeout=timeout_seconds) as response:
                    self._raise_for_status(response, str(payload.get("model", "")))
                    async for line in response.aiter_lines():
                        if not line:
                            continue
                        yield httpx.Response(200, content=line).json()
            except httpx.TimeoutException as exc:
                operation = "chat" if path == "/api/chat" else "generate"
                raise ProviderUnavailableError(f"Ollama {operation} stream timed out.") from exc

        return generator()

    def _raise_for_status(self, response: httpx.Response, model: str) -> None:
        if response.status_code == 404:
            raise ModelNotFoundError(f"Model '{model}' not found in Ollama.")
        if response.status_code >= 400:
            try:
                message = response.json().get("error")
            except Exception:
                message = response.text
            raise ProviderUnavailableError(f"Ollama request failed: {message}")
