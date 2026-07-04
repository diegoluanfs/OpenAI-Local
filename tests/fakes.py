from collections.abc import AsyncIterator
from typing import Any

from app.domain.interfaces import LLMProvider


class FakeProvider(LLMProvider):
    async def chat(
        self,
        model: str,
        messages: list[dict[str, Any]],
        temperature: float | None,
        max_tokens: int | None,
        stream: bool,
    ) -> dict[str, Any] | AsyncIterator[dict[str, Any]]:
        if stream:
            async def _stream():
                yield {"message": {"content": "hello"}, "done": False}
                yield {"message": {"content": " world"}, "done": True}

            return _stream()
        return {
            "message": {"content": "hello world"},
            "prompt_eval_count": 5,
            "eval_count": 2,
        }

    async def completion(
        self,
        model: str,
        prompt: str,
        temperature: float | None,
        max_tokens: int | None,
        stream: bool,
    ) -> dict[str, Any] | AsyncIterator[dict[str, Any]]:
        if stream:
            async def _stream():
                yield {"response": "foo", "done": False}
                yield {"response": "bar", "done": True}

            return _stream()
        return {"response": "foobar", "prompt_eval_count": 3, "eval_count": 2}

    async def embeddings(self, model: str, text: str) -> dict[str, Any]:
        return {"embedding": [0.1, 0.2, 0.3]}

    async def list_models(self) -> list[dict[str, Any]]:
        return [{"name": "llama3.2:3b"}, {"name": "nomic-embed-text"}]

    async def pull_model(self, model: str) -> dict[str, Any]:
        return {"status": "success", "model": model}

    async def health(self) -> bool:
        return True
