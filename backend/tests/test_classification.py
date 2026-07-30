"""Unit tests for ClassificationService and its extractors.

These are pure logic tests -- no HTTP, no database -- so they run fast and
don't require chromadb or a network connection. They do need spaCy's
en_core_web_sm model available for entity extraction to return results,
but classify()/extract_skills()/extract_date() work without it.
"""

from app.services.classification_service import classification_service

CERT_TEXT = (
    "Certificate of Completion\n\n"
    "This certifies that the bearer has successfully completed the course "
    "\"Python for Data Science\" offered by Infosys Springboard.\n\n"
    "Date of completion: 15 March 2024\n\n"
    "Skills demonstrated: Python, Data Analysis, Pandas, NumPy\n"
)

INTERNSHIP_TEXT = (
    "Internship Completion Letter\n\n"
    "This is to certify that the intern completed a 3-month internship in the "
    "Software Engineering team, working with React and Node.js.\n"
    "Internship period: June 2024 to August 2024.\n"
)


def test_classify_certificate_as_certification():
    result = classification_service.classify(CERT_TEXT, "python_certificate.pdf")
    assert result["category"] == "certification"
    assert 0.0 <= result["confidence"] <= 1.0
    assert "reasoning" in result


def test_classify_internship_letter():
    result = classification_service.classify(INTERNSHIP_TEXT, "internship_letter.pdf")
    assert result["category"] == "internship"


def test_classify_falls_back_to_other_for_unrecognized_text():
    result = classification_service.classify(
        "lorem ipsum dolor sit amet consectetur adipiscing elit", "notes.pdf"
    )
    assert result["category"] == "other"
    assert result["confidence"] == 0.5


def test_extract_skills_finds_known_keywords():
    skills = classification_service.extract_skills(CERT_TEXT)
    assert "Python" in skills


def test_extract_skills_is_case_insensitive_and_deduplicated():
    text = "python PYTHON Python pandas"
    skills = classification_service.extract_skills(text)
    assert skills.count("Python") == 1


def test_extract_date_finds_a_date():
    date = classification_service.extract_date(CERT_TEXT)
    assert date is not None
    assert "2024" in date


def test_extract_date_returns_none_for_no_date():
    date = classification_service.extract_date("no dates in here at all")
    assert date is None


def test_extract_title_falls_back_to_filename():
    title = classification_service.extract_title("some body text", "my_certificate.pdf")
    assert "certificate" in title.lower()


def test_process_document_returns_full_pipeline_shape():
    result = classification_service.process_document(CERT_TEXT, "python_certificate.pdf")

    for key in ("title", "category", "confidence", "reasoning", "summary", "skills",
                "organizations", "dates", "locations", "primary_date", "entities"):
        assert key in result

    assert result["category"] == "certification"
    assert "Python" in result["skills"]
