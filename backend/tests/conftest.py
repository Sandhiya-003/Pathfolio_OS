"""Shared pytest fixtures.

These are integration tests: they run against the real FastAPI app (`app.main.app`)
with the real database file, so they need the full stack installed
(`pip install -r requirements.txt` and `python -m spacy download en_core_web_sm`).

Each test registers a fresh, randomly-named user so runs don't collide with
each other or with real data, and cleans up the documents it creates.
"""

import uuid

import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture(scope="session")
def client():
    with TestClient(app) as c:
        yield c


@pytest.fixture()
def auth_headers(client):
    """Register a throwaway user and return an Authorization header for them."""
    suffix = uuid.uuid4().hex[:10]
    payload = {
        "username": f"test_{suffix}",
        "email": f"test_{suffix}@example.com",
        "password": "testpassword123",
    }
    res = client.post("/api/auth/register", json=payload)
    assert res.status_code == 201, res.text
    token = res.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture()
def sample_certificate_text():
    return (
        "Certificate of Completion\n\n"
        "This certifies that the bearer has successfully completed the course "
        "\"Python for Data Science\" offered by Infosys Springboard.\n\n"
        "Date of completion: 15 March 2024\n\n"
        "Skills demonstrated: Python, Data Analysis, Pandas, NumPy\n"
    )


@pytest.fixture()
def uploaded_document(client, auth_headers, sample_certificate_text, tmp_path):
    """Upload one sample document for the test user and return the response JSON."""
    file_path = tmp_path / "sample_cert.txt"
    file_path.write_text(sample_certificate_text)

    with open(file_path, "rb") as f:
        res = client.post(
            "/api/upload/single",
            headers=auth_headers,
            files={"file": ("sample_cert.txt", f, "text/plain")},
        )
    assert res.status_code == 200, res.text
    body = res.json()
    assert body["success"] is True
    return body
