from functools import lru_cache
from typing import Literal

from pydantic import Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_env: Literal["development", "test", "staging", "production"] = "development"
    app_name: str = "Local LLM Server"
    host: str = "0.0.0.0"
    port: int = 8000
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "INFO"

    ollama_url: str = "http://ollama:11434"
    lmstudio_url: str = "http://host.docker.internal:1234"
    default_model: str = "llama3.2:3b"
    embedding_model: str = "nomic-embed-text"
    timeout_seconds: float = 120.0
    timeout_tags_seconds: float = 10.0
    timeout_chat_seconds: float = 120.0
    timeout_generate_seconds: float = 120.0
    timeout_embeddings_seconds: float = 60.0
    timeout_pull_seconds: float = 0.0
    auto_pull_default_model: bool = True
    model_cache_ttl_seconds: float = 5.0

    api_key_file: str | None = None
    api_key: str | None = None
    allowed_api_keys_file: str | None = None
    allowed_api_keys: str = ""
    allow_anonymous_requests: bool = True
    unauth_rate_limit_per_minute: int = 30
    cors_origins: str = "*"
    rate_limit_per_minute: int = 0
    inference_concurrency_limit: int = 2
    max_request_body_bytes: int = 1_048_576
    httpx_max_connections: int = 20
    httpx_max_keepalive_connections: int = 5
    rate_limit_backend: Literal["memory", "redis"] = "memory"
    redis_url: str | None = None
    redis_key_prefix: str = "local-llm:ratelimit"

    provider_name: Literal["ollama", "lmstudio"] = Field(
        default="ollama",
        description="Configured model provider",
    )

    @model_validator(mode="before")
    @classmethod
    def load_secret_files(cls, data: object) -> object:
        if not isinstance(data, dict):
            return data

        resolved = dict(data)

        for secret_key, file_key in (("api_key", "api_key_file"), ("allowed_api_keys", "allowed_api_keys_file")):
            current_value = resolved.get(secret_key)
            if current_value is not None and str(current_value).strip():
                continue
            file_path = resolved.get(file_key)
            if not file_path:
                continue
            try:
                with open(file_path, "r", encoding="utf-8") as file_obj:
                    secret_value = file_obj.read().strip()
            except OSError as exc:  # pragma: no cover - validation error path
                raise ValueError(f"Could not read secret file for {secret_key}: {file_path}") from exc

            if secret_value:
                resolved[secret_key] = secret_value

        return resolved

    @model_validator(mode="after")
    def validate_production_security(self) -> "Settings":
        supported_providers = {"ollama", "lmstudio"}
        if self.provider_name not in supported_providers:
            raise ValueError(
                f"Unsupported provider '{self.provider_name}'. Registered providers: {sorted(supported_providers)}"
            )
        if self.app_env in {"staging", "production"} and not self.allowed_api_keys_set:
            raise ValueError("ALLOWED_API_KEYS must be configured when APP_ENV is staging or production")
        if self.app_env in {"staging", "production"}:
            self.allow_anonymous_requests = False
        return self

    @property
    def allowed_api_keys_set(self) -> set[str]:
        keys = {key.strip() for key in self.allowed_api_keys.split(",") if key.strip()}
        if self.api_key:
            keys.add(self.api_key.strip())
        return keys


@lru_cache
def get_settings() -> Settings:
    return Settings()
