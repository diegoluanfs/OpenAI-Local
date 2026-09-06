from collections.abc import AsyncIterator
from typing import Any

import httpx

from app.core.exceptions import ModelNotFoundError, ProviderUnavailableError


class OpenAICompatibleClient:
    def __init__(
        self,
        base_url: str,
        timeout_seconds: float,
        timeout_models_seconds: float,
        timeout_chat_seconds: float,
        timeout_completion_seconds: float,
        timeout_embeddings_seconds: float,
        max_connections: int = 20,
        max_keepalive_connections: int = 5,
    ) -> None:
        limits = httpx.Limits(
            max_connections=max_connections,
            max_keepalive_connections=max_keepalive_connections,
        )
        self._client = httpx.AsyncClient(
            base_url=base_url.rstrip("/"),
            timeout=timeout_seconds,
            limits=limits,
        )
        self._timeout_models_seconds = timeout_models_seconds
        self._timeout_chat_seconds = timeout_chat_seconds
        self._timeout_completion_seconds = timeout_completion_seconds
        self._timeout_embeddings_seconds = timeout_embeddings_seconds

    async def close(self) -> None:
        await self._client.aclose()

    async def models(self) -> list[dict[str, Any]]:
        try:
            response = await self._client.get("/v1/models", timeout=self._timeout_models_seconds)
            self._raise_for_status(response, "")
            return response.json().get("data", [])
        except httpx.TimeoutException as exc:
            raise ProviderUnavailableError("OpenAI-compatible models request timed out.") from exc

    async def chat(
        self,
        model: str,
        messages: list[dict[str, Any]],
        temperature: float | None,
        max_tokens: int | None,
        stream: bool,
    ) -> dict[str, Any] | AsyncIterator[dict[str, Any]]:
        payload = self._generation_payload(model, temperature, max_tokens)
        payload.update({"messages": messages, "stream": stream})
        if not stream:
            response = await self._post("/v1/chat/completions", payload, self._timeout_chat_seconds, model)
            body = response.json()
            choice = (body.get("choices") or [{}])[0]
            message = choice.get("message", {})
            return {
                "message": {"content": message.get("content", "")},
                "prompt_eval_count": body.get("usage", {}).get("prompt_tokens", 0),
                "eval_count": body.get("usage", {}).get("completion_tokens", 0),
            }

        return self._stream("/v1/chat/completions", payload, self._timeout_chat_seconds, model, "chat")

    async def completion(
        self,
        model: str,
        prompt: str,
        temperature: float | None,
        max_tokens: int | None,
        stream: bool,
    ) -> dict[str, Any] | AsyncIterator[dict[str, Any]]:
        payload = self._generation_payload(model, temperature, max_tokens)
        payload.update({"prompt": prompt, "stream": stream})
        if not stream:
            response = await self._post("/v1/completions", payload, self._timeout_completion_seconds, model)
            body = response.json()
            choice = (body.get("choices") or [{}])[0]
            return {
                "response": choice.get("text", ""),
                "prompt_eval_count": body.get("usage", {}).get("prompt_tokens", 0),
                "eval_count": body.get("usage", {}).get("completion_tokens", 0),
            }

        return self._stream("/v1/completions", payload, self._timeout_completion_seconds, model, "completion")

    async def embeddings(self, model: str, text: str) -> dict[str, Any]:
        response = await self._post(
            "/v1/embeddings",
            {"model": model, "input": text},
            self._timeout_embeddings_seconds,
            model,
        )
        data = (response.json().get("data") or [{}])[0]
        return {"embedding": data.get("embedding", [])}

    async def health(self) -> bool:
        await self.models()
        return True

    def _generation_payload(self, model: str, temperature: float | None, max_tokens: int | None) -> dict[str, Any]:
        payload: dict[str, Any] = {"model": model}
        if temperature is not None:
            payload["temperature"] = temperature
        if max_tokens is not None:
            payload["max_tokens"] = max_tokens
        return payload

    async def _post(self, path: str, payload: dict[str, Any], timeout: float, model: str) -> httpx.Response:
        try:
            response = await self._client.post(path, json=payload, timeout=timeout)
        except httpx.TimeoutException as exc:
            raise ProviderUnavailableError("OpenAI-compatible request timed out.") from exc
        self._raise_for_status(response, model)
        return response

    def _stream(
        self,
        path: str,
        payload: dict[str, Any],
        timeout: float,
        model: str,
        operation: str,
    ) -> AsyncIterator[dict[str, Any]]:
        async def generator() -> AsyncIterator[dict[str, Any]]:
            try:
                async with self._client.stream("POST", path, json=payload, timeout=timeout) as response:
                    self._raise_for_status(response, model)
                    async for line in response.aiter_lines():
                        if not line or line == "data: [DONE]":
                            if line == "data: [DONE]":
                                yield {"done": True}
                            continue
                        if line.startswith("data: "):
                            body = httpx.Response(200, content=line[6:]).json()
                            choice = (body.get("choices") or [{}])[0]
                            if operation == "chat":
                                content = choice.get("delta", {}).get("content", "")
                                yield {"message": {"content": content}, "done": False}
                            else:
                                yield {"response": choice.get("text", ""), "done": False}
            except httpx.TimeoutException as exc:
                raise ProviderUnavailableError(f"OpenAI-compatible {operation} stream timed out.") from exc

        return generator()

    def _raise_for_status(self, response: httpx.Response, model: str) -> None:
        if response.status_code == 404:
            raise ModelNotFoundError(f"Model '{model}' not found in OpenAI-compatible provider.")
        if response.status_code >= 400:
            try:
                message = response.json().get("error", {}).get("message")
            except Exception:
                message = response.text
            raise ProviderUnavailableError(f"OpenAI-compatible request failed: {message}")
