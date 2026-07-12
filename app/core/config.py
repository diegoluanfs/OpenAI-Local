from functools import lru_cache
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "Local LLM Server"
    host: str = "0.0.0.0"
    port: int = 8000
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "INFO"

    ollama_url: str = "http://ollama:11434"
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

    api_key: str | None = None
    allowed_api_keys: str = (
        "local-api-key-01,local-api-key-02,local-api-key-03,local-api-key-04,local-api-key-05,"
        "local-api-key-06,local-api-key-07,local-api-key-08,local-api-key-09,local-api-key-10"
    )
    unauth_rate_limit_per_minute: int = 30
    cors_origins: str = "*"
    rate_limit_per_minute: int = 0

    provider_name: str = Field(default="ollama", description="Future extension: vllm, lmstudio, llama_cpp")

    @property
    def allowed_api_keys_set(self) -> set[str]:
        keys = {key.strip() for key in self.allowed_api_keys.split(",") if key.strip()}
        if self.api_key:
            keys.add(self.api_key.strip())
        return keys


@lru_cache
def get_settings() -> Settings:
    return Settings()
