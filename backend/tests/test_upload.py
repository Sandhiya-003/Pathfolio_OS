"""Integration tests for the upload pipeline and per-user isolation."""


def test_upload_requires_auth(client):
    res = client.post("/api/upload/single", files={"file": ("x.txt", b"hello", "text/plain")})
    assert res.status_code == 401


def test_upload_rejects_unsupported_file_type(client, auth_headers):
    res = client.post(
        "/api/upload/single",
        headers=auth_headers,
        files={"file": ("archive.zip", b"not a real zip", "application/zip")},
    )
    assert res.status_code == 400


def test_upload_rejects_oversized_file(client, auth_headers, monkeypatch):
    from app.core.config import settings
    monkeypatch.setattr(settings, "MAX_UPLOAD_SIZE_MB", 1)  # 1MB limit for this test

    oversized_content = b"x" * (2 * 1024 * 1024)  # 2MB, over the limit
    res = client.post(
        "/api/upload/single",
        headers=auth_headers,
        files={"file": ("huge_resume.txt", oversized_content, "text/plain")},
    )
    assert res.status_code == 413


def test_upload_single_document_succeeds(uploaded_document):
    assert uploaded_document["category"] == "certification"
    assert "Python" in uploaded_document["skills_found"]
    assert uploaded_document["document_id"]


def test_uploaded_document_appears_in_list(client, auth_headers, uploaded_document):
    res = client.get("/api/documents/", headers=auth_headers)
    assert res.status_code == 200
    ids = [d["id"] for d in res.json()["documents"]]
    assert uploaded_document["document_id"] in ids


def test_duplicate_upload_is_detected(client, auth_headers, sample_certificate_text, tmp_path, uploaded_document):
    file_path = tmp_path / "sample_cert_again.txt"
    file_path.write_text(sample_certificate_text)

    with open(file_path, "rb") as f:
        res = client.post(
            "/api/upload/single",
            headers=auth_headers,
            files={"file": ("sample_cert_again.txt", f, "text/plain")},
        )

    assert res.status_code == 200
    body = res.json()
    assert body["success"] is False
    assert body["duplicate_of"] == uploaded_document["document_id"]


def test_a_user_cannot_see_another_users_documents(client, uploaded_document):
    import uuid
    other = client.post("/api/auth/register", json={
        "username": f"other_{uuid.uuid4().hex[:8]}",
        "email": f"other_{uuid.uuid4().hex[:8]}@example.com",
        "password": "testpassword123",
    })
    other_headers = {"Authorization": f"Bearer {other.json()['access_token']}"}

    res = client.get(f"/api/documents/{uploaded_document['document_id']}", headers=other_headers)
    assert res.status_code == 404

    res = client.get("/api/documents/", headers=other_headers)
    assert res.json()["total"] == 0