from fastapi.testclient import TestClient

from app.api.dependencies import _unauth_request_buckets
from app.core.config import Settings
from app.infrastructure.repositories import InMemoryModelRepository
from app.main import create_app
from app.services.llm_service import LLMService
from tests.fakes import FakeProvider


def _create_client() -> TestClient:
    _unauth_request_buckets.clear()
    settings = Settings(
        auto_pull_default_model=False,
        unauth_rate_limit_per_minute=1,
        allowed_api_keys="k1,k2,k3,k4,k5,k6,k7,k8,k9,k10",
    )
    app = create_app(settings)
    app.state.container.llm_service = LLMService(
        FakeProvider(),
        InMemoryModelRepository(FakeProvider(), "llama3.2:3b"),
        "nomic-embed-text",
    )
    return TestClient(app)


def test_ask_allows_request_with_valid_api_key():
    with _create_client() as client:
        response = client.post(
            "/ask",
            headers={"X-API-Key": "k1"},
            json={"question": "me fale algo curto"},
        )

    assert response.status_code == 200
    payload = response.json()
    assert "answer" in payload


def test_ask_rejects_invalid_api_key():
    with _create_client() as client:
        response = client.post(
            "/ask",
            headers={"X-API-Key": "invalid-key"},
            json={"question": "teste"},
        )

    assert response.status_code == 401
    payload = response.json()
    assert payload["error"]["code"] == "invalid_api_key"


def test_ask_limits_anonymous_requests_per_minute():
    with _create_client() as client:
        first = client.post("/ask", json={"question": "primeira"})
        second = client.post("/ask", json={"question": "segunda"})

    assert first.status_code == 200
    assert second.status_code == 429
    payload = second.json()
    assert payload["error"]["code"] == "unauthenticated_rate_limit_exceeded"
