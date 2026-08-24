"""Regression tests for the search-returns-everything bug.

Root cause was two-fold: the ChromaDB collection was created without
specifying cosine distance (defaulted to raw L2, making the similarity
math wrong), and search never filtered by relevance -- it just returned
up to `limit` results regardless of how irrelevant they were. With a
small archive, that meant every search returned every document.
"""

import time


def _upload_text(client, auth_headers, tmp_path, filename, content):
    path = tmp_path / filename
    path.write_text(content)
    with open(path, "rb") as f:
        res = client.post(
            "/api/upload/single",
            headers=auth_headers,
            files={"file": (filename, f, "text/plain")},
        )
    assert res.status_code == 200, res.text
    body = res.json()
    assert body["success"] is True, body.get("message")
    return body["document_id"]


def test_search_distinguishes_between_unrelated_documents(client, auth_headers, tmp_path):
    aws_id = _upload_text(
        client, auth_headers, tmp_path, "aws_certificate.txt",
        "AWS Cloud Practitioner Certificate\n\n"
        "This certifies completion of the AWS Cloud Practitioner course covering "
        "cloud computing fundamentals, EC2, S3, and IAM.\nIssued: June 2024.",
    )
    cooking_id = _upload_text(
        client, auth_headers, tmp_path, "cooking_workshop.txt",
        "Certificate of Participation\n\n"
        "This certifies attendance at a traditional South Indian cooking workshop "
        "covering regional recipes, spice blending, and food presentation.\n"
        "Issued: March 2023.",
    )

    # ChromaDB indexing can lag a beat behind the SQLite write in some setups;
    # this keeps the test robust without hardcoding a long sleep.
    time.sleep(0.5)

    res = client.get("/api/search/", headers=auth_headers, params={"q": "AWS cloud certification", "limit": 10})
    assert res.status_code == 200
    body = res.json()

    result_ids = [r["document_id"] for r in body["results"]]

    assert aws_id in result_ids, "The AWS certificate should show up for an AWS query"
    assert cooking_id not in result_ids, (
        "A cooking workshop certificate should NOT show up for an AWS cloud query -- "
        "if this fails, search is falling back to 'return everything' again"
    )


def test_search_does_not_return_every_document_for_every_query(client, auth_headers, tmp_path):
    _upload_text(client, auth_headers, tmp_path, "doc1.txt", "Internship completion letter for a marketing role at a retail company.")
    _upload_text(client, auth_headers, tmp_path, "doc2.txt", "Certificate for completing a advanced organic chemistry laboratory course.")
    _upload_text(client, auth_headers, tmp_path, "doc3.txt", "Achievement award for winning a regional chess tournament.")

    time.sleep(0.5)

    res = client.get("/api/search/", headers=auth_headers, params={"q": "chess tournament achievement", "limit": 10})
    assert res.status_code == 200
    body = res.json()

    # The core regression: a specific query should not return all 3 unrelated documents.
    assert body["total_results"] < 3, (
        f"Expected search to filter out unrelated documents, but got {body['total_results']} "
        "results for a query that should only match one of them"
    )


def test_category_listing_is_exact_and_empty_categories_are_honest(client, auth_headers, tmp_path):
    certificate_id = _upload_text(
        client, auth_headers, tmp_path, "cloud_certificate.txt",
        "AWS Cloud Practitioner certificate covering EC2, S3, IAM, and cloud security.",
    )
    _upload_text(
        client, auth_headers, tmp_path, "internship_letter.txt",
        "Internship completion letter for a frontend React engineering placement.",
    )

    certificates = client.get(
        "/api/search/", headers=auth_headers, params={"q": "show all my certificates"}
    )
    assert certificates.status_code == 200
    certificate_results = certificates.json()
    assert certificate_results["total_results"] == 1
    assert [r["document_id"] for r in certificate_results["results"]] == [certificate_id]
    assert {r["category"] for r in certificate_results["results"]} == {"certification"}

    resumes = client.get(
        "/api/search/", headers=auth_headers, params={"q": "show all my resumes"}
    )
    assert resumes.status_code == 200
    assert resumes.json()["total_results"] == 0
    assert resumes.json()["results"] == []
