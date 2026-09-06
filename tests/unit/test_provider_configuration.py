import pytest
from pydantic import ValidationError

from app.core.config import Settings


def test_ollama_is_the_registered_provider():
    settings = Settings(provider_name="ollama")

    assert settings.provider_name == "ollama"


def test_unsupported_provider_fails_explicitly():
    with pytest.raises(ValidationError, match="Unsupported provider"):
        Settings(provider_name="vllm")
