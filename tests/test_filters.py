"""
Unit tests for Hard Eligibility Filtering rules.
"""

from src.filters import evaluate_eligibility, check_python_evidence, check_ai_agentic_evidence


def test_python_evidence_detection():
    """Verify that Python stack terms are detected accurately."""
    has_py, matches = check_python_evidence("Experienced in Python, FastAPI, and PostgreSQL.")
    assert has_py is True
    assert "python" in matches
    assert "fastapi" in matches

    has_no_py, matches_none = check_python_evidence("Worked with Java, Spring Boot, React, and MySQL.")
    assert has_no_py is False
    assert len(matches_none) == 0


def test_ai_agentic_evidence_detection():
    """Verify that AI, RAG, and Agentic frameworks are detected."""
    has_ai, matches = check_ai_agentic_evidence("Built a stateful multi-agent system using LangGraph and ChromaDB vector search.")
    assert has_ai is True
    assert any("langgraph" in m for m in matches)
    assert any("agent" in m for m in matches)

    has_no_ai, matches_none = check_ai_agentic_evidence("Built standard CRUD REST APIs with Django and PostgreSQL.")
    assert has_no_ai is False


def test_hard_eligibility_rejection_for_non_python():
    """Reject candidate with no Python experience even if AI keywords exist."""
    candidate = {
        "candidate_name": "Java Dev",
        "raw_text": "Java, Spring Boot, OpenAI API, React",
        "matched_skills": ["Java", "React"]
    }
    result = evaluate_eligibility(candidate)
    assert result.eligible is False
    assert any("Python" in r for r in result.rejection_reasons)


def test_hard_eligibility_rejection_for_non_ai():
    """Reject candidate with strong Python but zero AI/agentic/RAG project exposure."""
    candidate = {
        "candidate_name": "Pure Backend Dev",
        "raw_text": "5 years Python, Django, FastAPI, Redis, PostgreSQL backend engineering.",
        "matched_skills": ["Python", "FastAPI", "PostgreSQL", "Redis"]
    }
    result = evaluate_eligibility(candidate)
    assert result.eligible is False
    assert any("AI/agentic" in r for r in result.rejection_reasons)


def test_hard_eligibility_passing_with_python_and_ai():
    """Pass candidate with both Python and AI/agentic project evidence."""
    candidate = {
        "candidate_name": "Asha Rao",
        "raw_text": "Python engineer developing agentic workflows with LangGraph, FastAPI, and RAG vector search.",
        "matched_skills": ["Python", "FastAPI", "LangGraph", "RAG"]
    }
    result = evaluate_eligibility(candidate)
    assert result.eligible is True
    assert len(result.rejection_reasons) == 0


def test_hard_eligibility_accepts_react_and_javascript_when_python_and_ai_present():
    """Do NOT reject candidates just because JavaScript / React / Next.js is also present."""
    candidate = {
        "candidate_name": "Full Stack AI Engineer",
        "raw_text": "Full stack engineer building Next.js, React frontend and Python FastAPI backend with LangChain RAG.",
        "matched_skills": ["Python", "FastAPI", "React", "Next.js", "LangChain"]
    }
    result = evaluate_eligibility(candidate)
    assert result.eligible is True
    assert len(result.rejection_reasons) == 0
