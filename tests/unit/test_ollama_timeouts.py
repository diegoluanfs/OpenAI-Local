import httpx
import pytest
from typing import Any, cast

from app.core.exceptions import ProviderUnavailableError
from app.infrastructure.ollama.client import OllamaClient


class TimeoutHttpClient:
    async def get(self, *args, **kwargs):
        raise httpx.ReadTimeout("timed out")

    async def post(self, *args, **kwargs):
        raise httpx.ReadTimeout("timed out")

    async def aclose(self):
        return None


class ResponseHttpClient:
    def __init__(self, status_code: int, payload: dict):
        self.response = httpx.Response(status_code, json=payload)

    async def post(self, *args, **kwargs):
        return self.response

    async def aclose(self):
        return None


def create_client() -> OllamaClient:
    client = OllamaClient("http://unused", 1, 1, 1, 1, 1, 1)
    cast(Any, client)._client = TimeoutHttpClient()
    return client


@pytest.mark.asyncio
async def test_tags_timeout_becomes_provider_error():
    with pytest.raises(ProviderUnavailableError, match="tags request timed out"):
        await create_client().tags()


@pytest.mark.asyncio
async def test_chat_timeout_becomes_provider_error():
    with pytest.raises(ProviderUnavailableError, match="chat request timed out"):
        await create_client().chat("model", [], None, None, False)


@pytest.mark.asyncio
async def test_embeddings_timeout_becomes_provider_error():
    with pytest.raises(ProviderUnavailableError, match="embeddings request timed out"):
        await create_client().embeddings("model", "text")


@pytest.mark.asyncio
async def test_missing_model_becomes_model_not_found_error():
    client = create_client()
    client._client = ResponseHttpClient(404, {"error": "not found"})

    from app.core.exceptions import ModelNotFoundError

    with pytest.raises(ModelNotFoundError, match="model"):
        await client.generate("model", "prompt", None, None, False)


@pytest.mark.asyncio
async def test_provider_server_error_becomes_provider_error():
    client = create_client()
    client._client = ResponseHttpClient(500, {"error": "upstream failure"})

    with pytest.raises(ProviderUnavailableError, match="upstream failure"):
        await client.generate("model", "prompt", None, None, False)
