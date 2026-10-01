"""
Pydantic data schemas for Candidate Information, Scoring, Eligibility, and Screening Reports.
"""

from typing import List, Optional
from pydantic import BaseModel, Field


class EligibilityResult(BaseModel):
    """Result of hard rule-based eligibility screening."""
    candidate: str
    eligible: bool
    rejection_reasons: List[str] = Field(default_factory=list)
    matched_skills: List[str] = Field(default_factory=list)


class ScoreBreakdown(BaseModel):
    """Detailed score breakdown across the 5 evaluation categories."""
    ai_project_depth: float = Field(default=0.0, description="Score for AI/Agentic/RAG project depth (0-40)")
    python_backend: float = Field(default=0.0, description="Score for Python & backend engineering (0-30)")
    cloud_fullstack: float = Field(default=0.0, description="Score for Cloud/Deployment/Full Stack (0-15)")
    github: float = Field(default=0.0, description="Score for GitHub activity & relevant repos (0-10)")
    engineering_depth: float = Field(default=0.0, description="Score for testing, architecture & depth signals (0-5)")


class CandidateResult(BaseModel):
    """Final screening result for a single candidate resume."""
    rank: Optional[int] = Field(default=None, description="Final candidate rank (1-indexed for eligible)")
    candidate_name: str = Field(..., description="Full name of candidate")
    file_name: str = Field(..., description="Source resume file name")
    eligible: bool = Field(..., description="Whether candidate passed hard eligibility filters")
    total_score: float = Field(default=0.0, description="Total 100-point score (0 for rejected)")
    score_breakdown: ScoreBreakdown = Field(default_factory=ScoreBreakdown)
    matched_skills: List[str] = Field(default_factory=list)
    project_summary: str = Field(default="", description="Summary of key projects & implementation depth")
    github_summary: str = Field(default="", description="Summary of public GitHub activity")
    strengths: List[str] = Field(default_factory=list)
    concerns: List[str] = Field(default_factory=list)
    rejection_reasons: List[str] = Field(default_factory=list)


class BatchSummary(BaseModel):
    """Aggregate statistics for a resume screening batch."""
    total_resumes: int
    successfully_parsed: int
    eligible: int
    rejected: int
    failed_unreadable: int


class ScreeningResponse(BaseModel):
    """Complete batch screening output with summary and ranked list."""
    batch_summary: BatchSummary
    results: List[CandidateResult]


class LLMEvaluationResult(BaseModel):
    """Structured response schema for LLM semantic project evaluations."""
    ai_project_depth_score: float = Field(..., ge=0.0, le=40.0)
    ai_project_reason: str
    python_backend_score: float = Field(..., ge=0.0, le=30.0)
    python_backend_reason: str
    cloud_fullstack_score: float = Field(..., ge=0.0, le=15.0)
    cloud_fullstack_reason: str
    engineering_depth_score: float = Field(..., ge=0.0, le=5.0)
    engineering_depth_reason: str
    penalty_score: float = Field(default=0.0, ge=0.0, le=15.0)
    penalty_reason: str = Field(default="")
    project_summary: str
    strengths: List[str] = Field(default_factory=list)
    concerns: List[str] = Field(default_factory=list)
    matched_skills: List[str] = Field(default_factory=list)
