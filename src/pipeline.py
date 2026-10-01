"""
End-to-End Batch Screening Pipeline.
Coordinates ingestion, hard filtering, GitHub enrichment, scoring, and output generation.
"""

import asyncio
import csv
import json
import logging
import os
from typing import List, Optional
from src.config import config
from src.extractor import parse_resume_file
from src.filters import evaluate_eligibility
from src.github import enrich_github_profile
from src.llm import CandidateEvaluator
from src.models import BatchSummary, CandidateResult, ScoreBreakdown, ScreeningResponse

logger = logging.getLogger(__name__)


class ResumeScreeningPipeline:
    """Async pipeline for screening, ranking, and explaining candidate resumes."""

    def __init__(self, concurrency: int = config.DEFAULT_CONCURRENCY, use_llm: bool = True):
        self.concurrency = concurrency
        self.use_llm = use_llm
        self.semaphore = asyncio.Semaphore(concurrency)
        self.evaluator = CandidateEvaluator()

    async def process_single_resume(self, file_path: str) -> Optional[CandidateResult]:
        """Process a single candidate resume through extraction, filtering, and scoring."""
        async with self.semaphore:
            filename = os.path.basename(file_path)
            try:
                # 1. Parse File
                parsed = parse_resume_file(file_path)
            except Exception as e:
                logger.error(f"Failed to parse resume '{filename}': {e}")
                return None

            # 2. Hard Eligibility Filter
            eligibility = evaluate_eligibility(parsed)

            if not eligibility.eligible:
                # Candidate is rejected by hard rules
                return CandidateResult(
                    rank=None,
                    candidate_name=parsed["candidate_name"],
                    file_name=filename,
                    eligible=False,
                    total_score=0.0,
                    score_breakdown=ScoreBreakdown(),
                    matched_skills=eligibility.matched_skills,
                    project_summary="Rejected by hard eligibility criteria.",
                    github_summary="Skipped due to ineligibility.",
                    strengths=[],
                    concerns=[],
                    rejection_reasons=eligibility.rejection_reasons
                )

            # 3. GitHub Enrichment (for eligible candidates)
            gh_score, gh_summary = await enrich_github_profile(parsed.get("github_username"))

            # 4. Scoring & LLM/Deterministic Evaluation
            eval_result = await self.evaluator.evaluate(
                candidate_data=parsed,
                github_score=gh_score,
                github_summary=gh_summary,
                use_llm=self.use_llm
            )

            return CandidateResult(
                rank=None,  # Assigned after ranking all eligible candidates
                candidate_name=parsed["candidate_name"],
                file_name=filename,
                eligible=True,
                total_score=eval_result["total_score"],
                score_breakdown=eval_result["score_breakdown"],
                matched_skills=parsed["matched_skills"],
                project_summary=eval_result["project_summary"],
                github_summary=eval_result["github_summary"],
                strengths=eval_result["strengths"],
                concerns=eval_result["concerns"],
                rejection_reasons=[]
            )

    async def screen_directory(self, input_dir: str) -> ScreeningResponse:
        """Process all resumes in an input folder and return ranked results."""
        if not os.path.exists(input_dir):
            raise FileNotFoundError(f"Input directory not found: {input_dir}")

        supported_exts = (".pdf", ".docx", ".txt", ".md")
        file_paths = [
            os.path.join(input_dir, f)
            for f in sorted(os.listdir(input_dir))
            if os.path.splitext(f)[1].lower() in supported_exts
        ]

        total_files = len(file_paths)
        if total_files == 0:
            return ScreeningResponse(
                batch_summary=BatchSummary(
                    total_resumes=0,
                    successfully_parsed=0,
                    eligible=0,
                    rejected=0,
                    failed_unreadable=0
                ),
                results=[]
            )

        # Run concurrent batch extraction and scoring
        tasks = [self.process_single_resume(fp) for fp in file_paths]
        processed_results = await asyncio.gather(*tasks)

        valid_results: List[CandidateResult] = []
        failed_count = 0

        for r in processed_results:
            if r is None:
                failed_count += 1
            else:
                valid_results.append(r)

        # Separate eligible and rejected candidates
        eligible_candidates = [c for c in valid_results if c.eligible]
        rejected_candidates = [c for c in valid_results if not c.eligible]

        # Rank eligible candidates descending by total_score
        eligible_candidates.sort(key=lambda c: c.total_score, reverse=True)
        for idx, candidate in enumerate(eligible_candidates, start=1):
            candidate.rank = idx

        # Combined results list: ranked eligible first, then rejected
        final_results = eligible_candidates + rejected_candidates

        summary = BatchSummary(
            total_resumes=total_files,
            successfully_parsed=len(valid_results),
            eligible=len(eligible_candidates),
            rejected=len(rejected_candidates),
            failed_unreadable=failed_count
        )

        return ScreeningResponse(batch_summary=summary, results=final_results)


def save_results_to_json(response: ScreeningResponse, output_path: str, format_type: str = "standard") -> None:
    """
    Saves screening results to a JSON file.
    - 'standard': outputs the exact JSON array as requested in Section 7 of the assignment PDF.
    - 'detailed': outputs full object including batch_summary and results list.
    """
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)

    if format_type == "standard":
        data_to_dump = [r.model_dump() for r in response.results]
    else:
        data_to_dump = response.model_dump()

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data_to_dump, f, indent=2, ensure_ascii=False)


def save_results_to_csv(response: ScreeningResponse, output_path: str) -> None:
    """Exports candidate screening results to CSV format."""
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)

    fieldnames = [
        "rank", "candidate_name", "file_name", "eligible", "total_score",
        "ai_project_depth", "python_backend", "cloud_fullstack", "github", "engineering_depth",
        "matched_skills", "rejection_reasons", "project_summary", "github_summary"
    ]

    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for r in response.results:
            writer.writerow({
                "rank": r.rank or "",
                "candidate_name": r.candidate_name,
                "file_name": r.file_name,
                "eligible": r.eligible,
                "total_score": r.total_score,
                "ai_project_depth": r.score_breakdown.ai_project_depth,
                "python_backend": r.score_breakdown.python_backend,
                "cloud_fullstack": r.score_breakdown.cloud_fullstack,
                "github": r.score_breakdown.github,
                "engineering_depth": r.score_breakdown.engineering_depth,
                "matched_skills": ", ".join(r.matched_skills),
                "rejection_reasons": ", ".join(r.rejection_reasons),
                "project_summary": r.project_summary,
                "github_summary": r.github_summary
            })
