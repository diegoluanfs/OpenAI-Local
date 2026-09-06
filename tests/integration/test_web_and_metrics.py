from fastapi.testclient import TestClient

from app.core.config import Settings
from app.main import create_app


def test_web_interface_is_served():
    app = create_app(Settings(auto_pull_default_model=False))

    with TestClient(app) as client:
        response = client.get("/")
        stylesheet = client.get("/web/styles.css")
        script = client.get("/web/app.js")

    assert response.status_code == 200
    assert "Local LLM" in response.text
    assert response.headers["x-content-type-options"] == "nosniff"
    assert response.headers["x-frame-options"] == "DENY"
    assert response.headers["referrer-policy"] == "no-referrer"
    assert stylesheet.status_code == 200
    assert "--accent" in stylesheet.text
    assert script.status_code == 200
    assert "loadStatus" in script.text


def test_metrics_endpoint_is_prometheus_compatible():
    app = create_app(Settings(auto_pull_default_model=False))

    with TestClient(app) as client:
        client.get("/health/live")
        response = client.get("/metrics")

    assert response.status_code == 200
    assert "text/plain" in response.headers["content-type"]
    assert "local_llm_requests_total" in response.text


def test_request_body_limit_rejects_oversized_payload():
    app = create_app(Settings(auto_pull_default_model=False, max_request_body_bytes=32))

    with TestClient(app) as client:
        response = client.post("/ask", json={"question": "x" * 100})

    assert response.status_code == 413
    assert response.json()["error"]["code"] == "request_body_too_large"