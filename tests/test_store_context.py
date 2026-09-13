import importlib

from fastapi.testclient import TestClient

import devduck.api.vapi_webhook as vapi_webhook


def _reload_module(monkeypatch, api_token="api-token"):
    monkeypatch.setenv("DEVDUCK_API_TOKEN", api_token)
    monkeypatch.delenv("DEVDUCK_VAPI_WEBHOOK_TOKEN", raising=False)
    return importlib.reload(vapi_webhook)


def test_store_and_retrieve_empty_context_round_trip(monkeypatch):
    # A valid but falsy context (empty string) must be storable and then
    # retrievable end to end, rather than being rejected at store time with a
    # 400 or returned as a misleading 404 on retrieval.
    module = _reload_module(monkeypatch)
    headers = {"X-DevDuck-Token": "api-token"}

    with TestClient(module.app) as client:
        stored = client.post(
            "/store_context",
            json={
                "name": "store_context",
                "parameters": {"snippet_id": "empty", "context": ""},
            },
            headers=headers,
        )
        assert stored.status_code == 200

        retrieved = client.post(
            "/retrieve_context",
            json={"name": "retrieve_context", "parameters": {"snippet_id": "empty"}},
            headers=headers,
        )
        assert retrieved.status_code == 200
        assert retrieved.json()["context"] == ""

    # The falsy value is retained in the store under its key.
    assert module.app_state.context_store["empty"] == ""


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


def test_store_missing_context_returns_400(monkeypatch):
    module = _reload_module(monkeypatch)
    headers = {"X-DevDuck-Token": "api-token"}

    with TestClient(module.app) as client:
        missing = client.post(
            "/store_context",
            json={
                "name": "store_context",
                "parameters": {"snippet_id": "s1"},
            },
            headers=headers,
        )
        assert missing.status_code == 400


def test_store_missing_snippet_id_returns_400(monkeypatch):
    module = _reload_module(monkeypatch)
    headers = {"X-DevDuck-Token": "api-token"}

    with TestClient(module.app) as client:
        missing = client.post(
            "/store_context",
            json={
                "name": "store_context",
                "parameters": {"context": "some code"},
            },
            headers=headers,
        )
        assert missing.status_code == 400
