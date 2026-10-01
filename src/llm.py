"""
LLM Provider Adapter & Semantic Evaluator.
Integrates structured output with Gemini models and provides automatic graceful fallback to deterministic evaluation.
"""

import json
import logging
from abc import ABC, abstractmethod
from typing import Dict, Optional, Tuple
from src.config import config
from src.models import LLMEvaluationResult, ScoreBreakdown
from src.scoring import evaluate_candidate_deterministic

logger = logging.getLogger(__name__)


SYSTEM_PROMPT = """You are an expert SDE Technical Hiring Evaluator assessing candidates for an SDE Intern (AI background) role.
Evaluate the candidate's resume based on the following 100-point rubric:
1. AI / Agentic / RAG Project Depth (0 to 40 pts): Reward agents, LangGraph, RAG, vector databases, tool-calling, stateful orchestration, evaluation pipelines.
2. Python & Backend Engineering (0 to 30 pts): Reward Python, FastAPI, async programming, PostgreSQL, Redis in projects over keyword lists.
3. Cloud / Deployment / Full Stack (0 to 15 pts): Reward GCP, Docker, Kubernetes, CI/CD, React/Next.js as supporting frontend signals.
4. Engineering Depth Signals (0 to 5 pts): Reward testing (pytest), architecture, caching, queues, observability, concurrency, failure handling.
5. Project Quality Penalty (0 to 15 pts): Deduct 5-15 pts if an 'AI project' is only a thin wrapper around an API call without workflow/retrieval/state management.

Respond STRICTLY with a valid JSON object conforming to this schema:
{
  "ai_project_depth_score": float (0-40),
  "ai_project_reason": string,
  "python_backend_score": float (0-30),
  "python_backend_reason": string,
  "cloud_fullstack_score": float (0-15),
  "cloud_fullstack_reason": string,
  "engineering_depth_score": float (0-5),
  "engineering_depth_reason": string,
  "penalty_score": float (0-15),
  "penalty_reason": string,
  "project_summary": string,
  "strengths": [string],
  "concerns": [string],
  "matched_skills": [string]
}
"""


class BaseLLMProvider(ABC):
    """Abstract interface for LLM evaluation providers."""

    @abstractmethod
    async def evaluate(self, resume_text: str, candidate_name: str) -> Optional[LLMEvaluationResult]:
        """Evaluate resume text and return structured scoring."""
        pass


class GeminiProvider(BaseLLMProvider):
    """Gemini structured output provider using google-genai SDK."""

    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        self.api_key = api_key or config.GEMINI_API_KEY
        self.model = model or config.LLM_MODEL
        self._client = None
        if self.api_key:
            try:
                from google import genai
                self._client = genai.Client(api_key=self.api_key)
            except Exception as e:
                logger.warning(f"Could not initialize Gemini Client: {e}")

    async def evaluate(self, resume_text: str, candidate_name: str) -> Optional[LLMEvaluationResult]:
        if not self._client:
            return None

        # Truncate text if excessively long to stay within budget
        truncated_text = resume_text[:8000]
        prompt = f"Candidate Name: {candidate_name}\n\nResume Text:\n{truncated_text}\n"

        try:
            # Synchronous SDK call wrapped in async or client.models.generate_content
            response = self._client.models.generate_content(
                model=self.model,
                contents=f"{SYSTEM_PROMPT}\n\n{prompt}",
                config={
                    "response_mime_type": "application/json",
                    "response_schema": LLMEvaluationResult
                }
            )

            if response.parsed and isinstance(response.parsed, LLMEvaluationResult):
                return response.parsed

            if response.text:
                data = json.loads(response.text)
                return LLMEvaluationResult(**data)

            return None
        except Exception as e:
            logger.warning(f"Gemini evaluation failed for '{candidate_name}': {e}. Falling back to deterministic scorer.")
            return None


class CandidateEvaluator:
    """
    Hybrid candidate evaluator that blends LLM semantic depth assessment
    with deterministic rubric rules and graceful offline fallbacks.
    """

    def __init__(self, llm_provider: Optional[BaseLLMProvider] = None):
        self.llm_provider = llm_provider or GeminiProvider()

    async def evaluate(
        self,
        candidate_data: Dict,
        github_score: float,
        github_summary: str,
        use_llm: bool = True
    ) -> Dict:
        """
        Evaluates an eligible candidate, combining GitHub signals and LLM/deterministic scores.
        """
        # 1. First run deterministic baseline
        baseline = evaluate_candidate_deterministic(candidate_data, github_score, github_summary)

        # 2. If LLM is enabled and configured, run semantic evaluation
        if use_llm and self.llm_provider:
            try:
                llm_res = await self.llm_provider.evaluate(
                    resume_text=candidate_data.get("raw_text", ""),
                    candidate_name=candidate_data.get("candidate_name", "")
                )
                if llm_res:
                    # Calculate net AI score
                    net_ai = max(0.0, llm_res.ai_project_depth_score - llm_res.penalty_score)
                    total = round(min(100.0, net_ai + llm_res.python_backend_score + llm_res.cloud_fullstack_score + github_score + llm_res.engineering_depth_score), 1)

                    breakdown = ScoreBreakdown(
                        ai_project_depth=round(net_ai, 1),
                        python_backend=round(llm_res.python_backend_score, 1),
                        cloud_fullstack=round(llm_res.cloud_fullstack_score, 1),
                        github=round(github_score, 1),
                        engineering_depth=round(llm_res.engineering_depth_score, 1)
                    )

                    return {
                        "total_score": total,
                        "score_breakdown": breakdown,
                        "project_summary": llm_res.project_summary,
                        "github_summary": github_summary,
                        "strengths": llm_res.strengths or baseline["strengths"],
                        "concerns": llm_res.concerns or baseline["concerns"]
                    }
            except Exception as e:
                logger.warning(f"Error during LLM evaluation, using deterministic baseline: {e}")

        return baseline
