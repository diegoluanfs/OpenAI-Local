from app.container import AppContainer
from app.core.config import Settings
from app.infrastructure.openai_compatible.provider import OpenAICompatibleProvider
from app.infrastructure.ollama.provider import OllamaProvider


def test_container_selects_ollama_by_default():
    container = AppContainer(Settings())

    assert isinstance(container.provider, OllamaProvider)


def test_container_selects_lmstudio_when_configured():
    container = AppContainer(Settings(provider_name="lmstudio"))

    assert isinstance(container.provider, OpenAICompatibleProvider)


def test_container_selects_openai_compatible_provider_for_vllm():
    container = AppContainer(Settings(provider_name="vllm"))

    assert isinstance(container.provider, OpenAICompatibleProvider)