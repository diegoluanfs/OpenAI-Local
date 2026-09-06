import httpx
import pytest

from app.core.exceptions import OperationNotSupportedError
from app.infrastructure.openai_compatible.client import OpenAICompatibleClient
from app.infrastructure.openai_compatible.provider import OpenAICompatibleProvider


async def make_provider(handler) -> OpenAICompatibleProvider:
    client = OpenAICompatibleClient(
        base_url="http://provider",
        timeout_seconds=5,
        timeout_models_seconds=5,
        timeout_chat_seconds=5,
        timeout_completion_seconds=5,
        timeout_embeddings_seconds=5,
    )
    await client._client.aclose()
    client._client = httpx.AsyncClient(
        transport=httpx.MockTransport(handler),
        base_url="http://provider",
    )
    return OpenAICompatibleProvider(client)


@pytest.mark.asyncio
async def test_openai_compatible_provider_normalizes_chat_and_embeddings():
    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path == "/v1/chat/completions":
            return httpx.Response(
                200,
                json={
                    "choices": [{"message": {"content": "hello"}}],
                    "usage": {"prompt_tokens": 3, "completion_tokens": 2},
                },
            )
        return httpx.Response(200, json={"data": [{"embedding": [0.1, 0.2]}]})

    provider = await make_provider(handler)

    assert await provider.chat("model", [], 0.2, 10, False) == {
        "message": {"content": "hello"},
        "prompt_eval_count": 3,
        "eval_count": 2,
    }
    assert await provider.embeddings("model", "text") == {"embedding": [0.1, 0.2]}
    await provider.close()


@pytest.mark.asyncio
async def test_openai_compatible_provider_normalizes_streaming_completion():
    def handler(_request: httpx.Request) -> httpx.Response:
        body = 'data: {"choices":[{"text":"hello"}]}\n\ndata: [DONE]\n\n'
        return httpx.Response(200, content=body.encode(), headers={"content-type": "text/event-stream"})

    provider = await make_provider(handler)
    stream = await provider.completion("model", "prompt", None, None, True)

    assert not isinstance(stream, dict)
    chunks = [chunk async for chunk in stream]
    assert chunks == [{"response": "hello", "done": False}, {"done": True}]
    await provider.close()


@pytest.mark.asyncio
async def test_openai_compatible_provider_lists_models_and_rejects_pull():
    def handler(_request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={"data": [{"id": "model"}]})

    provider = await make_provider(handler)

    assert await provider.list_models() == [{"name": "model", "id": "model"}]
    with pytest.raises(OperationNotSupportedError):
        await provider.pull_model("model")
    await provider.close()
