"""
GitHub Profile & Activity Enrichment Module.
Queries the public GitHub REST API with caching, rate-limit tolerance, and graceful fallbacks.
"""

import time
from typing import Dict, Optional, Tuple
import httpx
from src.config import config


# In-memory cache for GitHub API calls: username -> (timestamp, score, summary)
_GITHUB_CACHE: Dict[str, Tuple[float, float, str]] = {}


def calculate_github_score(user_data: Dict, repos_data: list) -> Tuple[float, str]:
    """
    Computes a 0-10 point GitHub score:
    - 0-5 points for recent activity (recent repo updates, public repos count).
    - 0-5 points for maintained/relevant repositories (Python, AI, LLM, RAG topics/languages, stars, forks).
    """
    public_repos = user_data.get("public_repos", 0)
    followers = user_data.get("followers", 0)

    # 1. Activity Score (0 - 5 points)
    activity_score = 0.0
    if public_repos >= 10:
        activity_score += 3.0
    elif public_repos >= 4:
        activity_score += 2.0
    elif public_repos >= 1:
        activity_score += 1.0

    # Check recent update timestamps in top repos
    has_recent_update = False
    relevant_repo_count = 0
    total_stars = 0

    ai_keywords = {"python", "rag", "agent", "llm", "fastapi", "langchain", "machine-learning", "ai"}

    for repo in repos_data[:10]:
        lang = str(repo.get("language") or "").lower()
        topics = [t.lower() for t in repo.get("topics", [])]
        name = str(repo.get("name") or "").lower()
        desc = str(repo.get("description") or "").lower()
        stars = repo.get("stargazers_count", 0)
        total_stars += stars

        if repo.get("updated_at", "").startswith(("2024", "2025", "2026")):
            has_recent_update = True

        # Check for Python / AI relevance
        is_relevant = (
            lang in ("python", "jupyter notebook")
            or any(kw in topics for kw in ai_keywords)
            or any(kw in name for kw in ai_keywords)
            or any(kw in desc for kw in ai_keywords)
        )
        if is_relevant:
            relevant_repo_count += 1

    if has_recent_update:
        activity_score += 2.0
    activity_score = min(5.0, activity_score)

    # 2. Relevance & Maintenance Score (0 - 5 points)
    repo_score = 0.0
    if relevant_repo_count >= 4:
        repo_score += 3.5
    elif relevant_repo_count >= 2:
        repo_score += 2.5
    elif relevant_repo_count >= 1:
        repo_score += 1.5

    if total_stars > 5 or followers > 5:
        repo_score += 1.5
    repo_score = min(5.0, repo_score)

    total_score = round(min(10.0, activity_score + repo_score), 1)

    summary_parts = []
    if has_recent_update:
        summary_parts.append("Recent engineering activity")
    summary_parts.append(f"{public_repos} public repos ({relevant_repo_count} Python/AI related)")
    if total_stars > 0:
        summary_parts.append(f"{total_stars} stars")

    summary = "; ".join(summary_parts) + "."
    return total_score, summary


async def enrich_github_profile(username: Optional[str]) -> Tuple[float, str]:
    """
    Enriches candidate data using public GitHub API.
    Handles rate limits, network timeouts, and non-existent usernames gracefully.
    """
    if not username:
        return 0.0, "No GitHub profile provided."

    clean_username = username.strip().lower()
    now = time.time()

    # Check cache
    if clean_username in _GITHUB_CACHE:
        cache_time, score, summary = _GITHUB_CACHE[clean_username]
        if now - cache_time < config.GITHUB_CACHE_TTL_SECONDS:
            return score, summary

    headers = {
        "Accept": "application/vnd.github.v3+json",
        "User-Agent": "Kasparro-Resume-Screening/1.0"
    }
    if config.GITHUB_TOKEN:
        headers["Authorization"] = f"Bearer {config.GITHUB_TOKEN}"

    try:
        async with httpx.AsyncClient(timeout=config.GITHUB_TIMEOUT_SECONDS) as client:
            # Fetch user profile
            user_resp = await client.get(
                f"https://api.github.com/users/{username}",
                headers=headers
            )

            if user_resp.status_code == 404:
                result = (0.0, f"GitHub username '{username}' not found.")
                _GITHUB_CACHE[clean_username] = (now, result[0], result[1])
                return result

            if user_resp.status_code == 403:
                # Rate limited
                result = (2.0, f"GitHub profile '{username}' found (API rate limited).")
                _GITHUB_CACHE[clean_username] = (now, result[0], result[1])
                return result

            if user_resp.status_code != 200:
                result = (1.0, f"GitHub profile '{username}' found (HTTP {user_resp.status_code}).")
                _GITHUB_CACHE[clean_username] = (now, result[0], result[1])
                return result

            user_data = user_resp.json()

            # Fetch user repos
            repos_resp = await client.get(
                f"https://api.github.com/users/{username}/repos?sort=updated&per_page=10",
                headers=headers
            )
            repos_data = repos_resp.json() if repos_resp.status_code == 200 else []

            score, summary = calculate_github_score(user_data, repos_data)
            _GITHUB_CACHE[clean_username] = (now, score, summary)
            return score, summary

    except httpx.RequestError as e:
        # Network error / offline fallback
        fallback = (2.0, f"GitHub profile '{username}' noted (offline/network timeout).")
        _GITHUB_CACHE[clean_username] = (now, fallback[0], fallback[1])
        return fallback
    except Exception as e:
        fallback = (0.0, f"GitHub enrichment failed for '{username}': {e}")
        return fallback
