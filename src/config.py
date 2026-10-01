"""
Configuration module for the AI Resume Screening & Ranking System.
Loads environment variables and sets baseline scoring weights and thresholds.
"""

import os
from dataclasses import dataclass
from dotenv import load_dotenv

# Load .env file if available
load_dotenv()


@dataclass(frozen=True)
class ScoringWeights:
    """Baseline weights for the 100-point candidate scoring rubric."""
    AI_PROJECT_DEPTH: float = 40.0
    PYTHON_BACKEND: float = 30.0
    CLOUD_FULLSTACK: float = 15.0
    GITHUB_ACTIVITY: float = 10.0
    ENGINEERING_DEPTH: float = 5.0


@dataclass(frozen=True)
class PenaltyWeights:
    """Project-quality penalty configuration."""
    SHALLOW_API_WRAPPER_MIN: float = 5.0
    SHALLOW_API_WRAPPER_MAX: float = 15.0
    SHALLOW_API_WRAPPER_DEFAULT: float = 10.0
    TUTORIAL_PROJECT: float = 8.0


@dataclass
class AppConfig:
    """Global system configuration."""
    # API Keys
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", os.getenv("GOOGLE_API_KEY", ""))
    GITHUB_TOKEN: str = os.getenv("GITHUB_TOKEN", "")

    # LLM Settings
    LLM_MODEL: str = os.getenv("LLM_MODEL", "gemini-2.5-flash")
    LLM_TIMEOUT_SECONDS: int = int(os.getenv("LLM_TIMEOUT_SECONDS", "15"))

    # GitHub Settings
    GITHUB_CACHE_TTL_SECONDS: int = int(os.getenv("GITHUB_CACHE_TTL_SECONDS", "3600"))
    GITHUB_TIMEOUT_SECONDS: int = int(os.getenv("GITHUB_TIMEOUT_SECONDS", "8"))

    # Concurrency Settings
    DEFAULT_CONCURRENCY: int = int(os.getenv("DEFAULT_CONCURRENCY", "5"))

    # Weights
    weights: ScoringWeights = ScoringWeights()
    penalties: PenaltyWeights = PenaltyWeights()


config = AppConfig()
