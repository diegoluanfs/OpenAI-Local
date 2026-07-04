from fastapi.testclient import TestClient

from app.core.config import Settings
from app.main import create_app


def test_health_endpoint_returns_expected_fields(monkeypatch):
    settings = Settings(auto_pull_default_model=False)
    app = create_app(settings)

    with TestClient(app) as client:
        response = client.get("/health")

    assert response.status_code == 200
    payload = response.json()
    assert "api_online" in payload
    assert "ollama_online" in payload
    assert "default_model" in payload
