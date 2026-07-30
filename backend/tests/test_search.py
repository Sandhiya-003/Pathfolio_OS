"""Integration tests for the smart retrieval (search) endpoints.

Semantic search quality depends on sentence-transformers + chromadb being
installed for real (not stubbed) -- these tests check the contract (status
codes, response shape, auth scoping) rather than asserting on exact
similarity rankings.
"""


def test_search_requires_auth(client):
    res = client.get("/api/search/", params={"q": "python"})
    assert res.status_code == 401


def test_search_returns_expected_shape(client, auth_headers, uploaded_document):
    res = client.get("/api/search/", headers=auth_headers, params={"q": "python certificate"})
    assert res.status_code == 200
    body = res.json()
    for key in ("query", "total_results", "results", "suggestions", "processing_time_ms"):
        assert key in body


def test_recent_documents_returns_uploaded_doc(client, auth_headers, uploaded_document):
    res = client.get("/api/search/recent", headers=auth_headers)
    assert res.status_code == 200
    ids = [d["id"] for d in res.json()["documents"]]
    assert uploaded_document["document_id"] in ids


def test_recent_documents_is_scoped_per_user(client, uploaded_document):
    import uuid
    other = client.post("/api/auth/register", json={
        "username": f"other_{uuid.uuid4().hex[:8]}",
        "email": f"other_{uuid.uuid4().hex[:8]}@example.com",
        "password": "testpassword123",
    })
    other_headers = {"Authorization": f"Bearer {other.json()['access_token']}"}

    res = client.get("/api/search/recent", headers=other_headers)
    assert res.status_code == 200
    assert res.json()["total"] == 0


def test_documents_by_skill(client, auth_headers, uploaded_document):
    res = client.get("/api/search/by-skill/Python", headers=auth_headers)
    assert res.status_code == 200
    assert res.json()["skill"] == "Python"
