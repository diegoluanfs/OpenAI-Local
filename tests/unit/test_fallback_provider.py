import pytest

from app.core.exceptions import ProviderUnavailableError
from app.infrastructure.fallback_provider import FallbackProvider


class StubProvider:
    def __init__(self, *, fail=False, fail_after_chunk=False):
        self.fail = fail
        self.fail_after_chunk = fail_after_chunk
        self.closed = False

    async def chat(self, model, messages, temperature, max_tokens, stream):
        if not stream:
            if self.fail:
                raise ProviderUnavailableError("offline")
            return {"message": {"content": "primary"}}

        async def stream_response():
            if self.fail:
                raise ProviderUnavailableError("offline")
            yield {"message": {"content": "primary"}, "done": False}
            if self.fail_after_chunk:
                raise ProviderUnavailableError("offline")

        return stream_response()

    async def completion(self, *args, **kwargs):
        return {"response": "ok"}

    async def embeddings(self, model, text):
        if self.fail:
            raise ProviderUnavailableError("offline")
        return {"embedding": [1.0]}

    async def list_models(self):
        return []

    async def pull_model(self, model):
        return {"status": "ok"}

    async def health(self):
        if self.fail:
            raise ProviderUnavailableError("offline")
        return True

    async def close(self):
        self.closed = True


@pytest.mark.asyncio
async def test_fallback_uses_secondary_for_unavailable_non_stream_request():
    provider = FallbackProvider(StubProvider(fail=True), StubProvider())

    response = await provider.chat("model", [], None, None, False)

    assert response == {"message": {"content": "primary"}}


@pytest.mark.asyncio
async def test_fallback_uses_secondary_before_streaming_starts():
    provider = FallbackProvider(StubProvider(fail=True), StubProvider())

    stream = await provider.chat("model", [], None, None, True)
    chunks = [chunk async for chunk in stream]

    assert chunks == [{"message": {"content": "primary"}, "done": False}]


@pytest.mark.asyncio
async def test_fallback_does_not_retry_after_streaming_started():
    provider = FallbackProvider(StubProvider(fail_after_chunk=True), StubProvider())
    stream = await provider.chat("model", [], None, None, True)

    with pytest.raises(ProviderUnavailableError):
        _ = [chunk async for chunk in stream]


@pytest.mark.asyncio
async def test_fallback_closes_both_providers():
    primary = StubProvider()
    secondary = StubProvider()
    provider = FallbackProvider(primary, secondary)

    await provider.close()

    assert primary.closed is True
    assert secondary.closed is True
