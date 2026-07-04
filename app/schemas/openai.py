from typing import Any, Literal

from pydantic import BaseModel, Field


class ChatMessage(BaseModel):
    role: Literal["system", "user", "assistant", "tool"]
    content: str


class ChatCompletionRequest(BaseModel):
    model: str | None = None
    messages: list[ChatMessage]
    temperature: float | None = Field(default=None, ge=0.0, le=2.0)
    max_tokens: int | None = Field(default=None, ge=1)
    stream: bool = False


class CompletionRequest(BaseModel):
    model: str | None = None
    prompt: str | list[str]
    temperature: float | None = Field(default=None, ge=0.0, le=2.0)
    max_tokens: int | None = Field(default=None, ge=1)
    stream: bool = False


class EmbeddingRequest(BaseModel):
    model: str | None = None
    input: str


class AskRequest(BaseModel):
    question: str = Field(examples=["Me fale algo interessante sobre IA local."])
    model: str | None = Field(default=None, examples=["llama3.2:3b"])
    system_prompt: str | None = Field(default=None, examples=["Responda em portugues de forma objetiva."])
    temperature: float | None = Field(default=0.7, ge=0.0, le=2.0, examples=[0.7])
    max_tokens: int | None = Field(default=256, ge=1, examples=[256])


class SetDefaultModelRequest(BaseModel):
    model: str


class PullModelRequest(BaseModel):
    model: str


class Usage(BaseModel):
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0


class AskResponse(BaseModel):
    question: str
    answer: str
    model: str
    usage: Usage


class HealthResponse(BaseModel):
    api_online: bool
    ollama_online: bool
    default_model: str
    memory_used_mb: float
    uptime_seconds: float


class ModelStatusResponse(BaseModel):
    model: str
    available: bool
    provider: str = "ollama"


class OpenAIErrorResponse(BaseModel):
    error: dict[str, Any]
