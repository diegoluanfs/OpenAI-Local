import httpx
import pytest
from fastapi import FastAPI

from app.core.config import Settings
from app.main import create_app


class StreamingService:
    async def chat_completion_stream(self, _request):
        yield 'data: {"choices":[{"delta":{"content":"hello"}}]}\n\n'
        yield 'data: [DONE]\n\n'


def _app() -> FastAPI:
    app = create_app(Settings(auto_pull_default_model=False))
    app.state.container.llm_service = StreamingService()
    return app


@pytest.mark.asyncio
async def test_chat_completion_stream_returns_sse_and_done_marker():
    transport = httpx.ASGITransport(app=_app())

    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/v1/chat/completions",
            json={
                "model": "test-model",
                "messages": [{"role": "user", "content": "hello"}],
                "stream": True,
            },
        )

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/event-stream")
    assert "hello" in response.text
    assert response.text.endswith("data: [DONE]\n\n")