import asyncio

import httpx
import pytest

from app.core.config import Settings
from app.main import create_app


class BlockingStreamingService:
    def __init__(self) -> None:
        self.started = asyncio.Event()
        self.release = asyncio.Event()

    async def chat_completion_stream(self, _request):
        self.started.set()
        yield 'data: {"choices":[{"delta":{"content":"chunk"}}]}\n\n'
        await self.release.wait()
        yield "data: [DONE]\n\n"


@pytest.mark.asyncio
async def test_streaming_request_holds_inference_concurrency_slot():
    app = create_app(Settings(auto_pull_default_model=False, inference_concurrency_limit=1))
    service = BlockingStreamingService()
    app.state.container.llm_service = service
    transport = httpx.ASGITransport(app=app)
    payload = {
        "model": "test-model",
        "messages": [{"role": "user", "content": "hello"}],
        "stream": True,
    }

    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        first_request = asyncio.create_task(client.post("/v1/chat/completions", json=payload))
        await asyncio.wait_for(service.started.wait(), timeout=1)
        second_response = await asyncio.wait_for(
            client.post("/v1/chat/completions", json=payload),
            timeout=1,
        )
        service.release.set()
        await first_request

    assert second_response.status_code == 429
    assert second_response.json()["error"]["code"] == "inference_concurrency_limit_reached"