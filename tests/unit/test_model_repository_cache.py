import pytest

from app.infrastructure.repositories import InMemoryModelRepository


class CountingProvider:
    def __init__(self) -> None:
        self.list_models_calls = 0

    async def list_models(self):
        self.list_models_calls += 1
        return [{"name": "llama3.2:3b"}]


@pytest.mark.asyncio
async def test_list_models_uses_cache_within_ttl():
    provider = CountingProvider()
    repo = InMemoryModelRepository(provider, "llama3.2:3b", cache_ttl_seconds=60)

    first = await repo.list_models()
    second = await repo.list_models()

    assert first == second
    assert provider.list_models_calls == 1


@pytest.mark.asyncio
async def test_invalidate_models_cache_forces_refresh():
    provider = CountingProvider()
    repo = InMemoryModelRepository(provider, "llama3.2:3b", cache_ttl_seconds=60)

    await repo.list_models()
    repo.invalidate_models_cache()
    await repo.list_models()

    assert provider.list_models_calls == 2
