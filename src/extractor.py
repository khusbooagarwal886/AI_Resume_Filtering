"""
Resume Extraction Engine.
Extracts clean plain text and candidate metadata (name, email, phone, links, skills) from PDF/TXT resumes.
"""

import os
import re
from typing import Dict, List, Optional, Tuple
import pypdf


EMAIL_REGEX = re.compile(r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+')
PHONE_REGEX = re.compile(r'(?:\+?\d{1,3}[-.\s]?)?\(?\d{3,5}\)?[-.\s]?\d{3,5}[-.\s]?\d{3,5}')
GITHUB_REGEX = re.compile(r'(?:https?://)?(?:www\.)?github\.com/([a-zA-Z0-9_-]+)', re.IGNORECASE)
LINKEDIN_REGEX = re.compile(r'(?:https?://)?(?:www\.)?linkedin\.com/in/([a-zA-Z0-9_-]+)', re.IGNORECASE)

KNOWN_SKILLS = [
    # Python & Backend
    "python", "python3", "fastapi", "django", "flask", "postgresql", "postgres", "redis",
    "asyncio", "celery", "rabbitmq", "kafka", "sqlite", "mysql", "mongodb", "sqlalchemy",
    "pydantic", "alembic", "rest api", "graphql", "grpc", "microservices",
    # AI / LLM / RAG / Agentic
    "langchain", "langgraph", "llamaindex", "rag", "agentic", "agents", "tool calling",
    "vector search", "embeddings", "multi-agent", "evaluation", "evaluation pipeline",
    "chromadb", "pinecone", "qdrant", "weaviate", "faiss", "gemini", "openai", "gpt-4",
    "claude", "anthropic", "hugging face", "huggingface", "transformers", "autogen", "crewai",
    "google adk", "genai", "prompt engineering", "fine-tuning", "lora",
    # Cloud & DevOps
    "docker", "kubernetes", "gcp", "google cloud", "aws", "azure", "ci/cd", "github actions",
    "terraform", "linux", "nginx", "vercel", "render",
    # Full Stack / Frontend Supporting
    "react", "react.js", "next.js", "nextjs", "typescript", "javascript", "tailwind", "node.js",
    # Engineering Depth
    "pytest", "unittest", "caching", "concurrency", "multithreading", "multiprocessing",
    "observability", "logging", "prometheus", "opentelemetry", "rate limiting"
]


def extract_text_from_pdf(file_path: str) -> Tuple[str, Dict]:
    """Extract raw text and document metadata from a PDF resume."""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Resume file not found: {file_path}")

    try:
        reader = pypdf.PdfReader(file_path)
        pages_text = []
        for page in reader.pages:
            extracted = page.extract_text()
            if extracted:
                pages_text.append(extracted)
        full_text = "\n".join(pages_text).strip()
        metadata = dict(reader.metadata or {})
        return full_text, metadata
    except Exception as e:
        raise ValueError(f"Failed to read PDF {file_path}: {e}") from e


def extract_candidate_name(text: str, metadata: Dict, filename: str) -> str:
    """
    Heuristic candidate name extraction with fallback strategies for various resume layouts.
    """
    lines = [line.strip() for line in text.splitlines() if line.strip()]

    # Check for metadata author if clean and not a system/tool name
    meta_author = str(metadata.get('/Author') or metadata.get('Author') or '').strip()
    invalid_authors = ('canva', 'microsoft word', 'microsoft account', 'resume', 'cv', 'user', 'author', 'admin')
    if meta_author and len(meta_author.split()) in (2, 3) and meta_author.lower() not in invalid_authors:
        return meta_author.title()

    bad_prefixes = (
        'phone', 'email', 'linkedin', 'github', 'http', 'https', 'www.',
        'resume', 'curriculum', 'contact', '/', '+', '•', '-', '#', 'address', 'summary'
    )

    # Strategy 1: Scan top 12 lines for a clear candidate name
    for line in lines[:12]:
        # Split glued lower-to-upper (e.g. "KumarDehradun" -> "Kumar Dehradun")
        separated_line = re.sub(r'([a-z])([A-Z])', r'\1 \2', line)
        # Handle attached email/mobile/location/city
        clean_line = separated_line
        clean_line = re.split(r'(?i)(?:email|mobile|phone|linkedin|github|portfolio|\+|@|—|–|\||,)', clean_line)[0].strip()
        clean_line = re.sub(r'[^a-zA-Z\s\.]', '', clean_line).strip()

        # Remove trailing city/state names if merged
        clean_line = re.sub(r'(?i)\b(?:dehradun|hyderabad|bengaluru|bangalore|mumbai|delhi|uttarakhand|india|west bengal|tamil nadu)\b.*$', '', clean_line).strip()

        words = clean_line.split()
        if not (1 <= len(words) <= 4) or len(clean_line) < 3 or len(clean_line) > 35:
            continue

        if any(line.lower().startswith(p) for p in bad_prefixes):
            continue

        if any(role in clean_line.lower() for role in [
            'developer', 'engineer', 'architect', 'analyst', 'student',
            'intern', 'full stack', 'backend', 'frontend', 'education',
            'experience', 'summary', 'skills', 'projects', 'certification',
            'btech', 'b.tech', 'mca', 'bca', 'bachelor', 'master', 'science',
            'microsoft account'
        ]):
            continue

        return clean_line

    # Strategy 2: Scan for all-caps standalone name block anywhere in top 20 lines
    for line in lines[:20]:
        cleaned = re.sub(r'[^a-zA-Z\s]', '', line).strip()
        words = cleaned.split()
        if 2 <= len(words) <= 4 and cleaned.isupper() and len(cleaned) < 30:
            if not any(header in cleaned for header in ['SUMMARY', 'EDUCATION', 'EXPERIENCE', 'PROJECTS', 'SKILLS', 'LANGUAGES', 'TOOLS', 'MICROSOFT ACCOUNT']):
                return cleaned.title()

    # Strategy 3: Clean up base filename
    base_name = os.path.splitext(os.path.basename(filename))[0]
    clean_base = re.sub(r'[_\-]+', ' ', base_name).strip()
    return clean_base.title()


def extract_candidate_metadata(text: str, metadata: Dict, filename: str) -> Dict:
    """Extract contact info, links, and matched skills from resume text."""
    name = extract_candidate_name(text, metadata, filename)
    
    # Extract Email
    emails = EMAIL_REGEX.findall(text)
    email = emails[0] if emails else ""

    # Extract Phone
    phones = PHONE_REGEX.findall(text)
    phone = phones[0] if phones else ""

    # Extract GitHub Username
    gh_matches = GITHUB_REGEX.findall(text)
    gh_username = gh_matches[0] if gh_matches else ""
    # Secondary check: text might have "GitHub: username" or "github.com/ username"
    if not gh_username:
        gh_fallback = re.findall(r'(?i)github(?:\.com)?[\s:/]+([a-zA-Z0-9_-]+)', text)
        if gh_fallback and gh_fallback[0].lower() not in ('com', 'http', 'https', 'profile', 'link'):
            gh_username = gh_fallback[0]

    # Extract LinkedIn
    li_matches = LINKEDIN_REGEX.findall(text)
    li_username = li_matches[0] if li_matches else ""

    # Extract matched skills
    matched_skills = []
    text_lower = text.lower()
    for skill in KNOWN_SKILLS:
        pattern = r'\b' + re.escape(skill) + r'\b'
        if re.search(pattern, text_lower):
            matched_skills.append(skill.title() if len(skill) > 3 else skill.upper())

    # De-duplicate matched skills preserving order
    unique_skills = []
    for s in matched_skills:
        if s not in unique_skills:
            unique_skills.append(s)

    return {
        "candidate_name": name,
        "email": email,
        "phone": phone,
        "github_username": gh_username,
        "github_url": f"https://github.com/{gh_username}" if gh_username else "",
        "linkedin_url": f"https://linkedin.com/in/{li_username}" if li_username else "",
        "matched_skills": unique_skills,
        "raw_text": text
    }


def parse_resume_file(file_path: str) -> Dict:
    """
    High-level resume parser supporting PDF, TXT, and DOCX files.
    Returns structured candidate information or raises an exception for unreadable files.
    """
    ext = os.path.splitext(file_path)[1].lower()
    filename = os.path.basename(file_path)

    if ext == ".pdf":
        text, metadata = extract_text_from_pdf(file_path)
    elif ext in (".txt", ".md"):
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            text = f.read()
        metadata = {}
    elif ext == ".docx":
        # Optional docx support
        try:
            import docx  # type: ignore
            doc = docx.Document(file_path)
            text = "\n".join([p.text for p in doc.paragraphs])
            metadata = {}
        except ImportError:
            raise ValueError("python-docx is not installed to process .docx files.")
    else:
        raise ValueError(f"Unsupported file format: {ext}")

    if not text or len(text.strip()) < 20:
        raise ValueError(f"Resume {filename} contains insufficient text or is empty.")

    parsed = extract_candidate_metadata(text, metadata, filename)
    parsed["file_name"] = filename
    parsed["file_path"] = file_path
    return parsed
