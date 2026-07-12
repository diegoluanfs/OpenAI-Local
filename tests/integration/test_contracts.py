from fastapi.testclient import TestClient

from app.core.config import Settings
from app.main import create_app


def test_openapi_contains_ask_contract():
    app = create_app(Settings(auto_pull_default_model=False))

    with TestClient(app) as client:
        response = client.get("/openapi.json")

    assert response.status_code == 200
    payload = response.json()
    ask_post = payload["paths"]["/ask"]["post"]
    assert "responses" in ask_post
    assert "200" in ask_post["responses"]
    schema = ask_post["responses"]["200"]["content"]["application/json"]["schema"]
    assert schema["$ref"].endswith("/AskResponse")


def test_validation_error_uses_standardized_envelope():
    app = create_app(Settings(auto_pull_default_model=False))

    with TestClient(app) as client:
        response = client.post("/ask", json={})

    assert response.status_code == 422
    payload = response.json()
    assert "error" in payload
    assert payload["error"]["type"] == "invalid_request_error"
    assert payload["error"]["code"] == "validation_error"
    assert payload["error"]["path"] == "/ask"
    assert payload["error"]["request_id"]
    assert "timestamp" in payload["error"]
    assert "details" in payload["error"]
