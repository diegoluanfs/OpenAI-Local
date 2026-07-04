import pytest

from app.infrastructure.repositories import InMemoryModelRepository
from app.schemas.openai import AskRequest, ChatCompletionRequest, ChatMessage, CompletionRequest, EmbeddingRequest
from app.services.llm_service import LLMService
from tests.fakes import FakeProvider


@pytest.mark.asyncio
async def test_chat_completion_returns_openai_format():
    service = LLMService(FakeProvider(), InMemoryModelRepository(FakeProvider(), "llama3.2:3b"), "nomic-embed-text")
    request = ChatCompletionRequest(messages=[ChatMessage(role="user", content="Oi")])

    result = await service.chat_completion(request)

    assert result["object"] == "chat.completion"
    assert result["choices"][0]["message"]["content"] == "hello world"
    assert result["usage"]["total_tokens"] == 7


@pytest.mark.asyncio
async def test_text_completion_returns_openai_format():
    service = LLMService(FakeProvider(), InMemoryModelRepository(FakeProvider(), "llama3.2:3b"), "nomic-embed-text")
    request = CompletionRequest(prompt="teste")

    result = await service.completion(request)

    assert result["object"] == "text_completion"
    assert result["choices"][0]["text"] == "foobar"


@pytest.mark.asyncio
async def test_embeddings_returns_list_shape():
    service = LLMService(FakeProvider(), InMemoryModelRepository(FakeProvider(), "llama3.2:3b"), "nomic-embed-text")
    request = EmbeddingRequest(input="text")

    result = await service.embeddings(request)

    assert result["object"] == "list"
    assert result["data"][0]["object"] == "embedding"


@pytest.mark.asyncio
async def test_ask_returns_simple_answer_shape():
    service = LLMService(FakeProvider(), InMemoryModelRepository(FakeProvider(), "llama3.2:3b"), "nomic-embed-text")
    request = AskRequest(question="O que e FastAPI?")

    result = await service.ask(request)

    assert result["question"] == "O que e FastAPI?"
    assert result["answer"] == "hello world"
    assert result["model"] == "llama3.2:3b"
