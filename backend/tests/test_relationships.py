"""Integration tests for the relationship engine and knowledge graph."""


def test_graph_requires_auth(client):
    res = client.get("/api/relationships/graph")
    assert res.status_code == 401


def test_graph_contains_skill_nodes_after_upload(client, auth_headers, uploaded_document):
    res = client.get("/api/relationships/graph", headers=auth_headers)
    assert res.status_code == 200
    body = res.json()
    assert "nodes" in body and "edges" in body

    skill_nodes = [n for n in body["nodes"] if n["type"] == "skill"]
    assert len(skill_nodes) > 0, "expected at least one skill node linked from the uploaded document"


def test_document_relationships_endpoint(client, auth_headers, uploaded_document):
    doc_id = uploaded_document["document_id"]
    res = client.get(f"/api/relationships/document/{doc_id}", headers=auth_headers)
    assert res.status_code == 200
    body = res.json()
    assert body["document_id"] == doc_id
    assert "relationships" in body
    assert "related_documents" in body


def test_document_relationships_404_for_missing_doc(client, auth_headers):
    res = client.get("/api/relationships/document/does-not-exist", headers=auth_headers)
    assert res.status_code == 404


def test_all_skills_reflects_uploaded_document(client, auth_headers, uploaded_document):
    res = client.get("/api/relationships/skills", headers=auth_headers)
    assert res.status_code == 200
    skills = [s["skill"] for s in res.json()["skills"]]
    assert "Python" in skills


def test_skills_are_scoped_per_user(client, uploaded_document):
    import uuid
    other = client.post("/api/auth/register", json={
        "username": f"other_{uuid.uuid4().hex[:8]}",
        "email": f"other_{uuid.uuid4().hex[:8]}@example.com",
        "password": "testpassword123",
    })
    other_headers = {"Authorization": f"Bearer {other.json()['access_token']}"}

    res = client.get("/api/relationships/skills", headers=other_headers)
    assert res.status_code == 200
    assert res.json()["total_skills"] == 0
