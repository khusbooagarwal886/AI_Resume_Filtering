"""
Rule-Based Hard Eligibility Filter.
Enforces the mandatory minimum requirements:
1. Genuine Python stack evidence.
2. Meaningful AI / LLM / RAG / Agentic project or framework evidence.
"""

import re
from typing import Dict, List, Tuple
from src.models import EligibilityResult


# Python stack detection patterns
PYTHON_PATTERNS = [
    r'\bpython(?:3)?\b',
    r'\bfastapi\b',
    r'\bdjango\b',
    r'\bflask\b',
    r'\bpytorch\b',
    r'\bpandas\b',
    r'\bnumpy\b',
    r'\bscikit[-_]?learn\b',
    r'\basyncio\b',
    r'\bcelery\b',
    r'\bsqlalchemy\b',
    r'\bpydantic\b',
    r'\bpytest\b',
    r'\bstreamlit\b'
]

# AI / Agentic / RAG / LLM evidence patterns
AI_AGENTIC_PATTERNS = [
    r'\blangchain\b',
    r'\blanggraph\b',
    r'\bllamaindex\b',
    r'\brag\b',
    r'\bretrieval[\s-]augmented\b',
    r'\bagentic\b',
    r'\b(?:ai|autonomous|llm)\s+agents?\b',
    r'\btool[\s-]calling\b',
    r'\bmulti[\s-]agent\b',
    r'\bvector\s+(?:db|database|search|embeddings?)\b',
    r'\bembeddings?\b',
    r'\bchromadb\b',
    r'\bpinecone\b',
    r'\bqdrant\b',
    r'\bweaviate\b',
    r'\bfaiss\b',
    r'\bgoogle\s+adk\b',
    r'\bautogen\b',
    r'\bcrewai\b',
    r'\bllms?\b',
    r'\bgenai\b',
    r'\bgenerative\s+ai\b',
    r'\bprompt\s+engineering\b',
    r'\btransformers?\b',
    r'\bhugging\s*face\b',
    r'\bfine[-_\s]tuning\b',
    r'\bevaluation\s+pipelines?\b',
    r'\bgpt[-_]?(?:4|3\.5|4o)\b',
    r'\bclaude\b',
    r'\bgemini\b'
]

COMPILED_PYTHON = [re.compile(p, re.IGNORECASE) for p in PYTHON_PATTERNS]
COMPILED_AI = [re.compile(p, re.IGNORECASE) for p in AI_AGENTIC_PATTERNS]


def check_python_evidence(text: str) -> Tuple[bool, List[str]]:
    """Check for explicit Python language and ecosystem evidence."""
    matched = []
    for pattern in COMPILED_PYTHON:
        matches = pattern.findall(text)
        if matches:
            matched.extend([m.lower() for m in matches])
    return (len(matched) > 0, list(set(matched)))


def check_ai_agentic_evidence(text: str) -> Tuple[bool, List[str]]:
    """Check for explicit AI, LLM, RAG, or Agentic framework/project evidence."""
    matched = []
    for pattern in COMPILED_AI:
        matches = pattern.findall(text)
        if matches:
            matched.extend([m.lower() for m in matches])
    return (len(matched) > 0, list(set(matched)))


def evaluate_eligibility(candidate_data: Dict) -> EligibilityResult:
    """
    Evaluates candidate eligibility based strictly on hard criteria:
    - Python evidence is REQUIRED.
    - AI / Agentic / RAG project evidence is REQUIRED.
    - Profiles having JavaScript/React/Java are ACCEPTED as long as Python + AI are also present.
    """
    candidate_name = candidate_data.get("candidate_name", "Unknown Candidate")
    raw_text = candidate_data.get("raw_text", "")
    matched_skills = candidate_data.get("matched_skills", [])

    has_python, python_matches = check_python_evidence(raw_text)
    has_ai, ai_matches = check_ai_agentic_evidence(raw_text)

    rejection_reasons = []

    if not has_python:
        rejection_reasons.append("No evidence of Python stack (Python/FastAPI/Flask/Django/PyTorch)")

    if not has_ai:
        rejection_reasons.append("No AI/agentic project evidence (LLMs, RAG, LangChain, Agents, Vector Search)")

    is_eligible = (has_python and has_ai)

    return EligibilityResult(
        candidate=candidate_name,
        eligible=is_eligible,
        rejection_reasons=rejection_reasons,
        matched_skills=matched_skills
    )
