import pytest
from pydantic import ValidationError

from app.core.config import Settings


def test_ollama_is_the_registered_provider():
    settings = Settings(provider_name="ollama")

    assert settings.provider_name == "ollama"


def test_unsupported_provider_fails_explicitly():
    with pytest.raises(ValidationError, match="Unsupported provider"):
        Settings(provider_name="vllm")


def test_file_based_secrets_are_loaded_for_production(tmp_path, monkeypatch):
    api_key_file = tmp_path / "api.key"
    allowed_keys_file = tmp_path / "allowed-keys.txt"
    api_key_file.write_text("file-api-key\n", encoding="utf-8")
    allowed_keys_file.write_text("prod-key-a, prod-key-b\n", encoding="utf-8")

    monkeypatch.setenv("API_KEY_FILE", str(api_key_file))
    monkeypatch.setenv("ALLOWED_API_KEYS_FILE", str(allowed_keys_file))

    settings = Settings(app_env="production")

    assert settings.api_key == "file-api-key"
    assert settings.allowed_api_keys == "prod-key-a, prod-key-b"
    assert "prod-key-a" in settings.allowed_api_keys_set
    assert "file-api-key" in settings.allowed_api_keys_set
