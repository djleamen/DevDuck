import importlib

from fastapi.testclient import TestClient

import devduck.api.vapi_webhook as vapi_webhook


def _reload_module(monkeypatch, api_token="api-token"):
    monkeypatch.setenv("DEVDUCK_API_TOKEN", api_token)
    monkeypatch.delenv("DEVDUCK_VAPI_WEBHOOK_TOKEN", raising=False)
    return importlib.reload(vapi_webhook)


def test_store_and_retrieve_context_round_trip(monkeypatch):
    module = _reload_module(monkeypatch)
    headers = {"X-DevDuck-Token": "api-token"}

    with TestClient(module.app) as client:
        stored = client.post(
            "/store_context",
            json={
                "name": "store_context",
                "parameters": {"snippet_id": "s1", "context": "some code"},
            },
            headers=headers,
        )
        assert stored.status_code == 200

        retrieved = client.post(
            "/retrieve_context",
            json={"name": "retrieve_context", "parameters": {"snippet_id": "s1"}},
            headers=headers,
        )
        assert retrieved.status_code == 200
        assert retrieved.json()["context"] == "some code"


def test_retrieve_missing_context_returns_404(monkeypatch):
    module = _reload_module(monkeypatch)
    headers = {"X-DevDuck-Token": "api-token"}

    with TestClient(module.app) as client:
        missing = client.post(
            "/retrieve_context",
            json={
                "name": "retrieve_context",
                "parameters": {"snippet_id": "does-not-exist"},
            },
            headers=headers,
        )
        assert missing.status_code == 404


def test_retrieve_stored_falsy_context_is_found(monkeypatch):
    # A stored-but-falsy value (empty string) still means the key exists, so
    # retrieval must return 200 with that value rather than a misleading 404.
    module = _reload_module(monkeypatch)
    module.app_state.context_store["empty"] = ""
    headers = {"X-DevDuck-Token": "api-token"}

    with TestClient(module.app) as client:
        retrieved = client.post(
            "/retrieve_context",
            json={"name": "retrieve_context", "parameters": {"snippet_id": "empty"}},
            headers=headers,
        )
        assert retrieved.status_code == 200
        assert retrieved.json()["context"] == ""
