"""Integration tests for the digital journey timeline."""


def test_timeline_requires_auth(client):
    res = client.get("/api/timeline/")
    assert res.status_code == 401


def test_timeline_is_empty_for_fresh_user(client, auth_headers):
    res = client.get("/api/timeline/", headers=auth_headers)
    assert res.status_code == 200
    body = res.json()
    assert body["total_events"] == 0
    assert body["timeline"] == []


def test_timeline_contains_uploaded_document(client, auth_headers, uploaded_document):
    res = client.get("/api/timeline/", headers=auth_headers)
    assert res.status_code == 200
    body = res.json()
    assert body["total_events"] >= 1

    all_event_ids = [
        event["id"]
        for year_block in body["timeline"]
        for event in year_block["events"]
    ]
    assert uploaded_document["document_id"] in all_event_ids


def test_timeline_groups_by_2024_for_sample_certificate(client, auth_headers, uploaded_document):
    res = client.get("/api/timeline/", headers=auth_headers)
    years = [block["year"] for block in res.json()["timeline"]]
    assert 2024 in years
    assert all(isinstance(y, int) for y in years), "timeline years must all be ints, not a mix of str/int"


def test_timeline_stats_endpoint(client, auth_headers, uploaded_document):
    res = client.get("/api/timeline/stats", headers=auth_headers)
    assert res.status_code == 200


def test_timeline_is_scoped_per_user(client, uploaded_document):
    import uuid
    other = client.post("/api/auth/register", json={
        "username": f"other_{uuid.uuid4().hex[:8]}",
        "email": f"other_{uuid.uuid4().hex[:8]}@example.com",
        "password": "testpassword123",
    })
    other_headers = {"Authorization": f"Bearer {other.json()['access_token']}"}

    res = client.get("/api/timeline/", headers=other_headers)
    assert res.json()["total_events"] == 0
