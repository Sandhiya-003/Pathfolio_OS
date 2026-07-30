"""Integration tests for the RAG chat assistant.

These don't call the real Groq API (no network dependency, no cost) -- they
verify auth, request validation, and the graceful-degradation path when
GROQ_API_KEY isn't configured. The retrieval/context-building logic is
exercised for real; only the final LLM call is mocked in test_search-style
unit coverage if you want to add it with `unittest.mock.patch`.
"""


def test_chat_requires_auth(client):
    res = client.post("/api/chat/", json={"message": "hello"})
    assert res.status_code == 401


def test_chat_rejects_empty_message(client, auth_headers):
    res = client.post("/api/chat/", headers=auth_headers, json={"message": ""})
    assert res.status_code == 422


def test_chat_without_groq_key_returns_clean_503(client, auth_headers, monkeypatch):
    from app.core.config import settings
    monkeypatch.setattr(settings, "GROQ_API_KEY", "")

    res = client.post("/api/chat/", headers=auth_headers, json={"message": "What do I have?"})
    assert res.status_code == 503
    assert "GROQ_API_KEY" in res.json()["error"]


def test_chat_with_mocked_groq_response(client, auth_headers, uploaded_document, monkeypatch):
    from unittest.mock import MagicMock
    from app.core.config import settings
    from app.services.chat_service import chat_service

    monkeypatch.setattr(settings, "GROQ_API_KEY", "fake-key-for-testing")

    fake_completion = MagicMock()
    fake_completion.choices = [MagicMock(message=MagicMock(content="You have a Python certificate."))]
    mock_client = MagicMock()
    mock_client.chat.completions.create.return_value = fake_completion
    chat_service._client = mock_client

    res = client.post(
        "/api/chat/", headers=auth_headers, json={"message": "What certificates do I have?"}
    )
    assert res.status_code == 200
    body = res.json()
    assert body["answer"] == "You have a Python certificate."
    assert "sources" in body
    assert "processing_time_ms" in body

    # Reset so this mock doesn't leak into other tests
    chat_service._client = None
