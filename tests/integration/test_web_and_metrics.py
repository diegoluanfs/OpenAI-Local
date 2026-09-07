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
    content_security_policy = response.headers["content-security-policy"]
    assert "https://cdn.jsdelivr.net" in content_security_policy
    assert "img-src 'self' data: https://fastapi.tiangolo.com" in content_security_policy
    assert "connect-src 'self' https://cdn.jsdelivr.net" in content_security_policy
    assert response.headers["x-frame-options"] == "DENY"
    assert response.headers["referrer-policy"] == "no-referrer"
    assert stylesheet.status_code == 200
    assert "--accent" in stylesheet.text
    assert script.status_code == 200
    assert "loadStatus" in script.text
    assert "export-button" in response.text
    assert "stream-toggle" in response.text
    assert "error-rate" in response.text
    assert "local-llm:conversation" in script.text
    assert "maxStoredMessages = 100" in script.text
    assert "setInterval" in script.text
    assert "15000" in script.text


def test_swagger_assets_are_allowed_only_on_docs_route():
    app = create_app(Settings(auto_pull_default_model=False))

    with TestClient(app) as client:
        docs_response = client.get("/docs")
        web_response = client.get("/")

    assert docs_response.status_code == 200
    assert "'unsafe-inline'" in docs_response.headers["content-security-policy"]
    assert "'unsafe-inline'" not in web_response.headers["content-security-policy"]


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