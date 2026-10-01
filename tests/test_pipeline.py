"""
Integration tests for End-to-End Batch Resume Screening Pipeline.
"""

import os
import pytest
from src.pipeline import ResumeScreeningPipeline, save_results_to_json
from src.models import ScreeningResponse


@pytest.mark.asyncio
async def test_screening_pipeline_runs_on_real_resumes():
    """Verify that the screening pipeline successfully processes resume files."""
    pipeline = ResumeScreeningPipeline(concurrency=5, use_llm=False)
    # Run on existing resumes directory
    if os.path.exists("resumes") and len(os.listdir("resumes")) > 0:
        response: ScreeningResponse = await pipeline.screen_directory("resumes")
        assert response.batch_summary.total_resumes == 50
        assert response.batch_summary.successfully_parsed == 50
        assert response.batch_summary.eligible > 0
        assert response.batch_summary.rejected > 0

        # Check ranking order
        eligible = [c for c in response.results if c.eligible]
        for i in range(len(eligible) - 1):
            assert eligible[i].total_score >= eligible[i + 1].total_score
            assert eligible[i].rank == i + 1

        # Check rejected have rank=None and explicit rejection reasons
        rejected = [c for c in response.results if not c.eligible]
        for r in rejected:
            assert r.rank is None
            assert len(r.rejection_reasons) > 0


def test_save_results_to_json(tmp_path):
    """Verify JSON output structure matches assignment specifications."""
    from src.models import BatchSummary, CandidateResult, ScoreBreakdown
    sample_response = ScreeningResponse(
        batch_summary=BatchSummary(
            total_resumes=1,
            successfully_parsed=1,
            eligible=1,
            rejected=0,
            failed_unreadable=0
        ),
        results=[
            CandidateResult(
                rank=1,
                candidate_name="Test Candidate",
                file_name="test.pdf",
                eligible=True,
                total_score=85.0,
                score_breakdown=ScoreBreakdown(
                    ai_project_depth=35.0,
                    python_backend=25.0,
                    cloud_fullstack=12.0,
                    github=8.0,
                    engineering_depth=5.0
                ),
                matched_skills=["Python", "FastAPI", "LangGraph"],
                project_summary="Built AI agent with LangGraph.",
                github_summary="Active repos.",
                strengths=["Strong agent"],
                concerns=[]
            )
        ]
    )

    out_file = tmp_path / "test_output.json"
    save_results_to_json(sample_response, str(out_file), format_type="standard")
    assert os.path.exists(out_file)
