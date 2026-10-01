"""
Candidate 100-Point Scoring Engine.
Implements the 5 evaluation categories, project-quality penalties, and explainability summaries.
"""

import re
from typing import Dict, List, Tuple
from src.config import config
from src.models import ScoreBreakdown


# Signal keyword sets for each evaluation category
ADVANCED_AI_SIGNALS = {
    "agents": ["agent", "agents", "langgraph", "multi-agent", "autogen", "crewai", "tool calling", "tool-calling", "subagent"],
    "rag": ["rag", "retrieval augmented generation", "vector search", "embeddings", "vector db", "chromadb", "pinecone", "qdrant", "weaviate", "faiss"],
    "orchestration": ["orchestration", "stateful", "state management", "chains", "langchain", "llamaindex", "evaluation pipeline", "ragas"],
    "models": ["gemini", "openai", "gpt-4", "claude", "anthropic", "hugging face", "transformer", "fine-tuning", "lora"]
}

PYTHON_BACKEND_SIGNALS = {
    "frameworks": ["fastapi", "django", "flask", "starlette", "rest api"],
    "async": ["asyncio", "async", "await", "concurrency", "event loop"],
    "databases": ["postgresql", "postgres", "redis", "mysql", "mongodb", "sqlite", "sqlalchemy", "alembic", "orm"],
    "core": ["python", "python3", "pydantic", "pytest"]
}

CLOUD_FULLSTACK_SIGNALS = {
    "cloud": ["gcp", "google cloud", "aws", "azure", "serverless", "lambda"],
    "container_devops": ["docker", "kubernetes", "ci/cd", "github actions", "terraform", "nginx"],
    "frontend": ["react", "react.js", "next.js", "nextjs", "typescript", "tailwind", "node.js", "frontend"]
}

ENGINEERING_DEPTH_SIGNALS = {
    "testing": ["pytest", "unittest", "mocking", "test coverage", "integration test", "unit test"],
    "architecture": ["microservices", "clean architecture", "design patterns", "oop", "mvc"],
    "caching_queues": ["caching", "redis cache", "celery", "rabbitmq", "kafka", "message queue", "bullmq"],
    "observability_reliability": ["observability", "logging", "prometheus", "opentelemetry", "rate limiting", "error handling", "failure handling"]
}

# Penalty indicators
SHALLOW_WRAPPER_INDICATORS = [
    r'simple\s+(?:chat|wrapper|call)\s+(?:api|endpoint)',
    r'used\s+openai\s+api\s+to\s+generate\s+text',
    r'streamlined\s+prompt\s+input',
    r'basic\s+chatbot\s+using\s+streamlit'
]

TUTORIAL_INDICATORS = [
    r'todo\s+app',
    r'calculator',
    r'tic\s*tac\s*toe',
    r'weather\s+app\s+using\s+api',
    r'clone\s+of\s+netflix',
    r'movie\s+recommendation\s+system\s+dataset'
]


def score_ai_project_depth(text: str) -> Tuple[float, List[str], str]:
    """
    Score AI / Agentic / RAG Project Depth (max 40.0 pts).
    Rewards real systems (agents, RAG, tool calling, state, orchestration, evaluation).
    """
    text_lower = text.lower()
    score = 0.0
    evidence = []

    # Agentic & Workflow depth (up to 16 pts)
    agent_matches = [w for w in ADVANCED_AI_SIGNALS["agents"] if re.search(r'\b' + re.escape(w) + r'\b', text_lower)]
    if agent_matches:
        if any(w in agent_matches for w in ["langgraph", "multi-agent", "tool calling", "autogen", "crewai"]):
            score += 16.0
            evidence.append(f"Agentic workflows / tool calling ({', '.join(agent_matches[:3])})")
        else:
            score += 10.0
            evidence.append("AI agent implementation")

    # RAG & Retrieval depth (up to 14 pts)
    rag_matches = [w for w in ADVANCED_AI_SIGNALS["rag"] if re.search(r'\b' + re.escape(w) + r'\b', text_lower)]
    if rag_matches:
        if any(w in rag_matches for w in ["vector search", "embeddings", "chromadb", "pinecone", "qdrant", "weaviate", "faiss"]):
            score += 14.0
            evidence.append(f"RAG & vector retrieval pipeline ({', '.join(rag_matches[:3])})")
        else:
            score += 8.0
            evidence.append("RAG architecture")

    # Orchestration / Evaluation depth (up to 6 pts)
    orch_matches = [w for w in ADVANCED_AI_SIGNALS["orchestration"] if re.search(r'\b' + re.escape(w) + r'\b', text_lower)]
    if orch_matches:
        score += 6.0
        evidence.append(f"Orchestration/evaluation ({', '.join(orch_matches[:2])})")

    # LLM Providers / Foundations (up to 4 pts)
    model_matches = [w for w in ADVANCED_AI_SIGNALS["models"] if re.search(r'\b' + re.escape(w) + r'\b', text_lower)]
    if model_matches:
        score += 4.0

    final_score = min(config.weights.AI_PROJECT_DEPTH, score)
    summary = "; ".join(evidence) if evidence else "Basic LLM API interactions."
    return final_score, evidence, summary


def score_python_backend(text: str) -> Tuple[float, List[str]]:
    """
    Score Python & Backend Engineering (max 30.0 pts).
    Rewards Python, FastAPI, async programming, PostgreSQL, Redis in projects/work.
    """
    text_lower = text.lower()
    score = 0.0
    evidence = []

    # Python core & usage in projects (up to 8 pts)
    if "python" in text_lower:
        score += 8.0
        evidence.append("Core Python proficiency")

    # FastAPI / Backend Frameworks (up to 8 pts)
    framework_matches = [w for w in PYTHON_BACKEND_SIGNALS["frameworks"] if re.search(r'\b' + re.escape(w) + r'\b', text_lower)]
    if framework_matches:
        if "fastapi" in framework_matches:
            score += 8.0
            evidence.append("FastAPI REST backend")
        else:
            score += 6.0
            evidence.append(f"Backend framework ({framework_matches[0]})")

    # Async programming (up to 6 pts)
    async_matches = [w for w in PYTHON_BACKEND_SIGNALS["async"] if re.search(r'\b' + re.escape(w) + r'\b', text_lower)]
    if async_matches:
        score += 6.0
        evidence.append("Asyncio / asynchronous programming")

    # Databases (PostgreSQL / Redis / SQL) (up to 8 pts)
    db_matches = [w for w in PYTHON_BACKEND_SIGNALS["databases"] if re.search(r'\b' + re.escape(w) + r'\b', text_lower)]
    if db_matches:
        if "postgresql" in db_matches or "postgres" in db_matches:
            score += 5.0
            evidence.append("PostgreSQL database")
        if "redis" in db_matches:
            score += 3.0
            evidence.append("Redis caching/queues")
        elif not evidence or "PostgreSQL" not in evidence[-1]:
            score += 4.0
            evidence.append(f"Database ({', '.join(db_matches[:2])})")

    final_score = min(config.weights.PYTHON_BACKEND, score)
    return final_score, evidence


def score_cloud_fullstack(text: str) -> Tuple[float, List[str]]:
    """
    Score Cloud / Deployment / Full Stack (max 15.0 pts).
    Rewards GCP, Docker, deployment, with React/Next.js as supporting signals.
    """
    text_lower = text.lower()
    score = 0.0
    evidence = []

    # Cloud (GCP / AWS / Azure) (up to 6 pts)
    cloud_matches = [w for w in CLOUD_FULLSTACK_SIGNALS["cloud"] if re.search(r'\b' + re.escape(w) + r'\b', text_lower)]
    if cloud_matches:
        if "gcp" in cloud_matches or "google cloud" in cloud_matches:
            score += 6.0
            evidence.append("GCP cloud experience")
        else:
            score += 4.0
            evidence.append(f"Cloud deployment ({cloud_matches[0].upper()})")

    # Containerization & DevOps (Docker / K8s / CI/CD) (up to 5 pts)
    devops_matches = [w for w in CLOUD_FULLSTACK_SIGNALS["container_devops"] if re.search(r'\b' + re.escape(w) + r'\b', text_lower)]
    if devops_matches:
        score += 5.0
        evidence.append(f"Containerization/DevOps ({', '.join(devops_matches[:2])})")

    # Frontend Supporting (React / Next.js) (up to 4 pts)
    frontend_matches = [w for w in CLOUD_FULLSTACK_SIGNALS["frontend"] if re.search(r'\b' + re.escape(w) + r'\b', text_lower)]
    if frontend_matches:
        score += 4.0
        evidence.append(f"Supporting frontend stack ({', '.join(frontend_matches[:2])})")

    final_score = min(config.weights.CLOUD_FULLSTACK, score)
    return final_score, evidence


def score_engineering_depth(text: str) -> Tuple[float, List[str]]:
    """
    Score Engineering Depth Signals (max 5.0 pts).
    Rewards testing, architecture, queues, observability, concurrency, failure handling.
    """
    text_lower = text.lower()
    score = 0.0
    evidence = []

    # Testing (pytest / unit testing) (up to 2 pts)
    test_matches = [w for w in ENGINEERING_DEPTH_SIGNALS["testing"] if re.search(r'\b' + re.escape(w) + r'\b', text_lower)]
    if test_matches:
        score += 2.0
        evidence.append("Automated testing / pytest")

    # Caching / Queues / Observability (up to 2 pts)
    cq_matches = [w for w in ENGINEERING_DEPTH_SIGNALS["caching_queues"] if re.search(r'\b' + re.escape(w) + r'\b', text_lower)]
    obs_matches = [w for w in ENGINEERING_DEPTH_SIGNALS["observability_reliability"] if re.search(r'\b' + re.escape(w) + r'\b', text_lower)]
    if cq_matches or obs_matches:
        score += 2.0
        if cq_matches:
            evidence.append(f"Queues/Caching ({cq_matches[0]})")
        if obs_matches:
            evidence.append(f"Observability/Resilience ({obs_matches[0]})")

    # Architecture / Design Patterns (up to 1 pt)
    arch_matches = [w for w in ENGINEERING_DEPTH_SIGNALS["architecture"] if re.search(r'\b' + re.escape(w) + r'\b', text_lower)]
    if arch_matches:
        score += 1.0
        evidence.append(f"Architecture patterns ({arch_matches[0]})")

    final_score = min(config.weights.ENGINEERING_DEPTH, score)
    return final_score, evidence


def calculate_penalties(text: str, ai_score: float) -> Tuple[float, List[str]]:
    """
    Calculate penalties for shallow API wrappers and boilerplate tutorial projects:
    - Deduct 5-15 pts if an 'AI project' is only a thin wrapper around an API call without workflow/retrieval.
    - Deduct points for tutorial-style projects without details.
    """
    text_lower = text.lower()
    penalties = 0.0
    reasons = []

    # Shallow wrapper check: has simple API call mention but minimal AI depth (< 15 pts)
    if ai_score < 15.0 and any(kw in text_lower for kw in ["openai api", "chatgpt api", "gemini api", "generate response"]):
        penalty_amount = 8.0
        penalties += penalty_amount
        reasons.append(f"Deducted {penalty_amount} pts: Shallow LLM API wrapper without stateful retrieval/workflow.")

    # Tutorial project check
    for pattern in TUTORIAL_INDICATORS:
        if re.search(pattern, text_lower):
            penalty_amount = 4.0
            penalties += penalty_amount
            reasons.append(f"Deducted {penalty_amount} pts: Generic tutorial-style project listed.")
            break

    return min(15.0, penalties), reasons


def evaluate_candidate_deterministic(candidate_data: Dict, github_score: float, github_summary: str) -> Dict:
    """
    Runs the comprehensive deterministic scoring algorithm across all 5 rubric categories.
    """
    raw_text = candidate_data.get("raw_text", "")
    matched_skills = candidate_data.get("matched_skills", [])

    # Score each category
    ai_score, ai_evidence, project_summary = score_ai_project_depth(raw_text)
    py_score, py_evidence = score_python_backend(raw_text)
    cloud_score, cloud_evidence = score_cloud_fullstack(raw_text)
    eng_score, eng_evidence = score_engineering_depth(raw_text)

    # Calculate penalties
    penalty_score, penalty_reasons = calculate_penalties(raw_text, ai_score)

    # Net AI Score after penalties (clamped to 0)
    adjusted_ai_score = max(0.0, ai_score - penalty_score)

    # Compute Total Score (0-100)
    total_score = round(min(100.0, max(0.0, adjusted_ai_score + py_score + cloud_score + github_score + eng_score)), 1)

    score_breakdown = ScoreBreakdown(
        ai_project_depth=round(adjusted_ai_score, 1),
        python_backend=round(py_score, 1),
        cloud_fullstack=round(cloud_score, 1),
        github=round(github_score, 1),
        engineering_depth=round(eng_score, 1)
    )

    # Compile Strengths & Concerns
    strengths = []
    strengths.extend(ai_evidence[:2])
    strengths.extend(py_evidence[:2])
    if cloud_evidence:
        strengths.append(cloud_evidence[0])

    concerns = []
    concerns.extend(penalty_reasons)
    if "Redis" not in [s.title() for s in matched_skills] and "redis" not in raw_text.lower():
        concerns.append("Limited Redis evidence")
    if "PostgreSQL" not in [s.title() for s in matched_skills] and "postgresql" not in raw_text.lower():
        concerns.append("Limited PostgreSQL evidence")
    if ai_score < 20.0:
        concerns.append("Limited agentic orchestration depth")

    return {
        "total_score": total_score,
        "score_breakdown": score_breakdown,
        "project_summary": project_summary or "Engineered Python & AI applications.",
        "github_summary": github_summary,
        "strengths": strengths,
        "concerns": concerns[:3]  # keep top 3 concerns
    }
