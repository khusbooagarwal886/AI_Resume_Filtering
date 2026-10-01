"""
Unit tests for the 100-Point Scoring Model and Penalty calculations.
"""

from src.scoring import (
    score_ai_project_depth,
    score_python_backend,
    score_cloud_fullstack,
    score_engineering_depth,
    calculate_penalties,
    evaluate_candidate_deterministic
)


def test_ai_project_depth_scoring_and_caps():
    """AI score should properly award agentic & RAG signals up to the 40 pt cap."""
    text = (
        "Engineered autonomous AI agents using LangGraph with tool-calling and multi-agent coordination. "
        "Integrated RAG pipeline with ChromaDB vector search and embeddings for semantic search."
    )
    score, evidence, summary = score_ai_project_depth(text)
    assert score >= 30.0
    assert score <= 40.0
    assert "Agentic" in summary or "RAG" in summary


def test_python_backend_scoring_and_caps():
    """Python backend score should award FastAPI, Asyncio, and Postgres/Redis up to 30 pts."""
    text = "Developed asynchronous FastAPI backend services with asyncio, PostgreSQL database, and Redis caching."
    score, evidence = score_python_backend(text)
    assert score >= 20.0
    assert score <= 30.0


def test_cloud_fullstack_scoring():
    """Cloud & Full stack should score GCP, Docker, and React up to 15 pts."""
    text = "Deployed containerized Docker services on GCP Google Cloud Platform with React frontend."
    score, evidence = score_cloud_fullstack(text)
    assert score >= 10.0
    assert score <= 15.0


def test_engineering_depth_scoring():
    """Engineering depth signals should score testing, architecture, and queues up to 5 pts."""
    text = "Implemented unit testing with pytest, microservices clean architecture, and Celery task queues."
    score, evidence = score_engineering_depth(text)
    assert score >= 4.0
    assert score <= 5.0


def test_shallow_wrapper_penalty():
    """Thin wrappers with simple API calls should receive penalty deduction."""
    text = "Simple chat wrapper using openai api to generate text. Basic chatbot using streamlit."
    penalty, reasons = calculate_penalties(text, ai_score=8.0)
    assert penalty >= 5.0
    assert any("wrapper" in r.lower() for r in reasons)


def test_total_candidate_scoring_end_to_end():
    """Complete candidate evaluation deterministic run."""
    candidate_data = {
        "candidate_name": "Asha Rao",
        "raw_text": (
            "Built a stateful agentic workflow with LangGraph, RAG retrieval, and tool calling. "
            "Backend developed using Python, async FastAPI, PostgreSQL, and Redis. "
            "Deployed with Docker on GCP. Automated unit tests with pytest and CI/CD."
        ),
        "matched_skills": ["Python", "FastAPI", "PostgreSQL", "LangGraph", "Docker", "GCP", "Pytest"]
    }

    result = evaluate_candidate_deterministic(
        candidate_data,
        github_score=8.0,
        github_summary="Recently active with maintained Python repositories."
    )

    assert result["total_score"] >= 75.0
    assert result["score_breakdown"].ai_project_depth >= 30.0
    assert result["score_breakdown"].python_backend >= 20.0
    assert len(result["strengths"]) > 0
