"""
Unit tests for Resume Extraction and Metadata Parsing.
"""

from src.extractor import extract_candidate_name, extract_candidate_metadata


def test_extract_candidate_name_clean():
    """Verify standard candidate name extraction from top of resume text."""
    text = (
        "Kartikay Sinha\n"
        "Phone: +91-7488615976 | Email: kartikay.sinha17@gmail.com\n"
        "LinkedIn: linkedin.com/in/kartikaysinha | GitHub: github.com/KS1745\n"
        "Full Stack Developer specializing in React and Python."
    )
    name = extract_candidate_name(text, {}, "candidate_01.pdf")
    assert name == "Kartikay Sinha"


def test_extract_candidate_name_with_merged_fields():
    """Verify name extraction when email/location are appended to name."""
    text = (
        "Atul KumarDehradun, Uttarakhand, India\n"
        "LinkedIn: atul-kumar07 Email: atulofficial02@gmail.com\n"
        "B.Tech in Computer Science."
    )
    name = extract_candidate_name(text, {}, "candidate_25.pdf")
    assert "Atul Kumar" in name


def test_extract_candidate_metadata_fields():
    """Verify extraction of email, phone, github username, and skills."""
    text = (
        "Jane Doe\n"
        "Email: jane.doe@example.com | Phone: +1 555-123-4567\n"
        "GitHub: https://github.com/janedoe-dev | LinkedIn: linkedin.com/in/janedoe\n"
        "Skills: Python, FastAPI, Docker, GCP, LangChain, PostgreSQL, Pytest"
    )
    meta = extract_candidate_metadata(text, {}, "jane_doe.pdf")
    assert meta["email"] == "jane.doe@example.com"
    assert meta["github_username"] == "janedoe-dev"
    assert "Python" in meta["matched_skills"]
    assert "Fastapi" in meta["matched_skills"] or "FastAPI" in meta["matched_skills"]
    assert "Docker" in meta["matched_skills"]
