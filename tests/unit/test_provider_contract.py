import pytest

from app.infrastructure.ollama.provider import OllamaProvider


class ContractClient:
    async def chat(self, *args):
        return {"message": {"content": "ok"}}

    async def generate(self, *args):
        return {"response": "ok"}

    async def embeddings(self, *args):
        return {"embedding": [0.1]}

    async def tags(self):
        return {"models": [{"name": "model"}]}

    async def pull(self, model):
        return {"status": "success", "model": model}

    async def close(self):
        return None


@pytest.mark.asyncio
async def test_ollama_provider_contract_delegates_all_operations():
    provider = OllamaProvider(ContractClient())

    assert await provider.chat("model", [], None, None, False) == {"message": {"content": "ok"}}
    assert await provider.completion("model", "prompt", None, None, False) == {"response": "ok"}
    assert await provider.embeddings("model", "text") == {"embedding": [0.1]}
    assert await provider.list_models() == [{"name": "model"}]
    assert await provider.pull_model("model") == {"status": "success", "model": "model"}
    assert await provider.health()
    await provider.close()
