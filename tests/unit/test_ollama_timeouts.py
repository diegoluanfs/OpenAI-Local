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
