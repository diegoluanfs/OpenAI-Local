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
    auto_pull_default_model: bool = True

    api_key: str | None = None
    cors_origins: str = "*"
    rate_limit_per_minute: int = 0

    provider_name: str = Field(default="ollama", description="Future extension: vllm, lmstudio, llama_cpp")


@lru_cache
def get_settings() -> Settings:
    return Settings()
