import pytest
from pydantic import ValidationError

from app.core.config import Settings


def test_ollama_is_the_registered_provider():
    settings = Settings(provider_name="ollama")

    assert settings.provider_name == "ollama"


def test_lmstudio_is_supported_alongside_ollama():
    lmstudio = Settings(provider_name="lmstudio")
    vllm = Settings(provider_name="vllm")

    assert lmstudio.provider_name == "lmstudio"
    assert vllm.provider_name == "vllm"


def test_unimplemented_providers_are_rejected():
    with pytest.raises(ValidationError, match="provider_name"):
        Settings(provider_name="llama_cpp")


def test_fallback_provider_must_differ_from_primary():
    with pytest.raises(ValidationError, match="FALLBACK_PROVIDER_NAME"):
        Settings(provider_name="ollama", fallback_provider_name="ollama")


def test_staging_requires_api_keys_and_disables_anonymous_requests():
    settings = Settings(app_env="staging", allowed_api_keys="staging-key")

    assert settings.app_env == "staging"
    assert settings.allow_anonymous_requests is False
    assert "staging-key" in settings.allowed_api_keys_set

    with pytest.raises(ValidationError, match="ALLOWED_API_KEYS"):
        Settings(app_env="staging")


def test_configurable_httpx_pool_limits_are_supported():
    settings = Settings(
        httpx_max_connections=42,
        httpx_max_keepalive_connections=7,
    )

    assert settings.httpx_max_connections == 42
    assert settings.httpx_max_keepalive_connections == 7


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
