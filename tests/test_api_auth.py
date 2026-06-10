import importlib

import pytest
from fastapi.testclient import TestClient

import devduck.api.vapi_webhook as vapi_webhook


def _reload_app(monkeypatch, api_token, webhook_token=None):
    monkeypatch.setenv("DEVDUCK_API_TOKEN", api_token)
    if webhook_token is None:
        monkeypatch.delenv("DEVDUCK_VAPI_WEBHOOK_TOKEN", raising=False)
    else:
        monkeypatch.setenv("DEVDUCK_VAPI_WEBHOOK_TOKEN", webhook_token)
    return importlib.reload(vapi_webhook).app


def test_auth_required_and_options_bypass(monkeypatch):
    app = _reload_app(monkeypatch, "api-token")

    with TestClient(app) as client:
        health = client.get("/health")
        assert health.status_code == 200

        root = client.get("/")
        assert root.status_code == 200

        unauthorized = client.get("/status")
        assert unauthorized.status_code == 401

        authorized = client.get(
            "/status", headers={"X-DevDuck-Token": "api-token"}
        )
        assert authorized.status_code == 200

        preflight = client.options(
            "/status",
            headers={
                "Origin": "http://localhost",
                "Access-Control-Request-Method": "GET",
            },
        )
        assert preflight.status_code == 200


def test_webhook_token_override(monkeypatch):
    app = _reload_app(monkeypatch, "api-token", webhook_token="webhook-token")

    with TestClient(app) as client:
        with_api_token = client.post(
            "/webhook/vapi",
            json={"message": {"type": "conversation-started"}},
            headers={"X-DevDuck-Token": "api-token"},
        )
        assert with_api_token.status_code == 401

        with_webhook_token = client.post(
            "/webhook/vapi",
            json={"message": {"type": "conversation-started"}},
            headers={"X-DevDuck-Token": "webhook-token"},
        )
        assert with_webhook_token.status_code == 200


def test_placeholder_token_rejected(monkeypatch):
    app = _reload_app(monkeypatch, "replace_with_a_strong_random_token")

    with pytest.raises(
        RuntimeError,
        match="DEVDUCK_API_TOKEN in your .env/environment must be changed",
    ):
        with TestClient(app):
            pass
