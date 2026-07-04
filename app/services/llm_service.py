import json
import logging
import time
import uuid
from collections.abc import AsyncIterator
from typing import Any

from app.core.exceptions import ModelNotFoundError, ProviderUnavailableError
from app.domain.interfaces import LLMProvider, ModelRepository
from app.schemas.openai import AskRequest, ChatCompletionRequest, CompletionRequest, EmbeddingRequest


class LLMService:
    def __init__(self, provider: LLMProvider, models: ModelRepository, embedding_model: str) -> None:
        self._provider = provider
        self._models = models
        self._embedding_model = embedding_model
        self._logger = logging.getLogger("local_llm.service")

    async def chat_completion(self, request: ChatCompletionRequest) -> dict[str, Any]:
        model = request.model or await self._models.get_default_model()
        self._validate_model_name(model)

        response = await self._provider.chat(
            model=model,
            messages=[m.model_dump() for m in request.messages],
            temperature=request.temperature,
            max_tokens=request.max_tokens,
            stream=False,
        )
        assert isinstance(response, dict)

        content = response.get("message", {}).get("content", "")
        usage = self._extract_usage(response)
        self._logger.info("chat_completed", extra={"model": model, "usage": usage})
        return {
            "id": f"chatcmpl-{uuid.uuid4().hex[:12]}",
            "object": "chat.completion",
            "created": int(time.time()),
            "model": model,
            "choices": [
                {
                    "index": 0,
                    "message": {"role": "assistant", "content": content},
                    "finish_reason": "stop",
                }
            ],
            "usage": usage,
        }

    async def chat_completion_stream(self, request: ChatCompletionRequest) -> AsyncIterator[str]:
        model = request.model or await self._models.get_default_model()
        self._validate_model_name(model)

        stream = await self._provider.chat(
            model=model,
            messages=[m.model_dump() for m in request.messages],
            temperature=request.temperature,
            max_tokens=request.max_tokens,
            stream=True,
        )
        assert not isinstance(stream, dict)

        async for chunk in stream:
            delta = chunk.get("message", {}).get("content", "")
            payload = {
                "id": f"chatcmpl-{uuid.uuid4().hex[:12]}",
                "object": "chat.completion.chunk",
                "created": int(time.time()),
                "model": model,
                "choices": [{"index": 0, "delta": {"content": delta}, "finish_reason": None}],
            }
            yield f"data: {json.dumps(payload)}\n\n"
            if chunk.get("done"):
                done_payload = {
                    "id": f"chatcmpl-{uuid.uuid4().hex[:12]}",
                    "object": "chat.completion.chunk",
                    "created": int(time.time()),
                    "model": model,
                    "choices": [{"index": 0, "delta": {}, "finish_reason": "stop"}],
                }
                yield f"data: {json.dumps(done_payload)}\n\n"
                break
        yield "data: [DONE]\n\n"

    async def completion(self, request: CompletionRequest) -> dict[str, Any]:
        model = request.model or await self._models.get_default_model()
        self._validate_model_name(model)
        prompt = request.prompt[0] if isinstance(request.prompt, list) else request.prompt

        response = await self._provider.completion(model, prompt, request.temperature, request.max_tokens, False)
        assert isinstance(response, dict)
        text = response.get("response", "")
        usage = self._extract_usage(response)
        self._logger.info("completion_completed", extra={"model": model, "usage": usage})

        return {
            "id": f"cmpl-{uuid.uuid4().hex[:12]}",
            "object": "text_completion",
            "created": int(time.time()),
            "model": model,
            "choices": [{"text": text, "index": 0, "finish_reason": "stop"}],
            "usage": usage,
        }

    async def completion_stream(self, request: CompletionRequest) -> AsyncIterator[str]:
        model = request.model or await self._models.get_default_model()
        self._validate_model_name(model)
        prompt = request.prompt[0] if isinstance(request.prompt, list) else request.prompt

        stream = await self._provider.completion(model, prompt, request.temperature, request.max_tokens, True)
        assert not isinstance(stream, dict)

        async for chunk in stream:
            payload = {
                "id": f"cmpl-{uuid.uuid4().hex[:12]}",
                "object": "text_completion",
                "created": int(time.time()),
                "model": model,
                "choices": [{"text": chunk.get("response", ""), "index": 0, "finish_reason": None}],
            }
            yield f"data: {json.dumps(payload)}\n\n"
            if chunk.get("done"):
                break
        yield "data: [DONE]\n\n"

    async def embeddings(self, request: EmbeddingRequest) -> dict[str, Any]:
        model = request.model or self._embedding_model
        response = await self._provider.embeddings(model, request.input)
        vector = response.get("embedding", [])
        self._logger.info("embedding_completed", extra={"model": model, "vector_size": len(vector)})
        return {
            "object": "list",
            "data": [{"object": "embedding", "index": 0, "embedding": vector}],
            "model": model,
            "usage": {"prompt_tokens": 0, "total_tokens": 0},
        }

    async def ask(self, request: AskRequest) -> dict[str, Any]:
        model = request.model or await self._resolve_public_model()
        prompt_parts: list[str] = []
        if request.system_prompt:
            prompt_parts.append(f"System: {request.system_prompt}")
        prompt_parts.append(f"User: {request.question}")
        prompt_parts.append("Assistant:")

        completion_request = CompletionRequest(
            model=model,
            prompt="\n".join(prompt_parts),
            temperature=request.temperature,
            max_tokens=request.max_tokens,
            stream=False,
        )
        completion_response = await self.completion(completion_request)
        answer = completion_response["choices"][0]["text"]

        return {
            "question": request.question,
            "answer": answer,
            "model": completion_response["model"],
            "usage": completion_response["usage"],
        }

    async def _resolve_public_model(self) -> str:
        default_model = await self._models.get_default_model()
        if await self._models.model_exists(default_model):
            return default_model

        models = await self._models.list_models()
        if models:
            first_model = str(models[0].get("name", "")).strip()
            if first_model:
                return first_model

        self._logger.info("pulling_public_default_model", extra={"model": default_model})
        await self.pull_model(default_model)

        if await self._models.model_exists(default_model):
            return default_model

        models = await self._models.list_models()
        if models:
            first_model = str(models[0].get("name", "")).strip()
            if first_model:
                return first_model

        raise ProviderUnavailableError(
            "No local models are installed yet. Configure DEFAULT_MODEL or pull a model before using /ask."
        )

    async def ensure_model_available(self, model: str) -> bool:
        return await self._models.model_exists(model)

    async def list_models(self) -> list[dict[str, Any]]:
        return await self._models.list_models()

    async def get_default_model(self) -> str:
        return await self._models.get_default_model()

    async def set_default_model(self, model: str) -> str:
        return await self._models.set_default_model(model)

    async def pull_model(self, model: str) -> dict[str, Any]:
        return await self._provider.pull_model(model)

    def _extract_usage(self, response: dict[str, Any]) -> dict[str, int]:
        prompt = int(response.get("prompt_eval_count", 0) or 0)
        completion = int(response.get("eval_count", 0) or 0)
        return {"prompt_tokens": prompt, "completion_tokens": completion, "total_tokens": prompt + completion}

    def _validate_model_name(self, model: str) -> None:
        if not model.strip():
            raise ModelNotFoundError("Model name cannot be empty.")
