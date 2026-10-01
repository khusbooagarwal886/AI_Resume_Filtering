# AI Resume Screening & Ranking System

A production-minded, explainable AI resume screening system designed for SDE Intern (AI/Agentic Systems) candidate evaluation. Ingests candidate resumes, executes strict rule-based eligibility filtering, enriches profiles with GitHub telemetry, and scores candidates across a 100-point rubric with actionable reasoning.

---

## 🚀 Quick Start

### 1. Environment Setup
```bash
# Clone or navigate to the repository
cd Kasparro

# Create & activate a virtual environment
python -m venv venv
# Windows:
.\venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Environment Variables (Optional)
Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```
* `GEMINI_API_KEY`: *(Optional)* Adds semantic LLM-backed evaluation. If omitted, the system runs with 100% functionality using the deterministic heuristic engine.
* `GITHUB_TOKEN`: *(Optional)* Increases GitHub API rate limits from 60 to 5,000 requests/hour.

---

## 💻 How to Run

### Command Line Interface (CLI)
Run the screening pipeline across all resumes in the `./resumes` directory:
```bash
# Basic run with output saved to ./output/results.json
python main.py --input ./resumes --output ./output/results.json

# Export both JSON and CSV
python main.py --input ./resumes --output ./output/results.json --csv ./output/results.csv

# Run in pure deterministic mode (no API calls)
python main.py --input ./resumes --output ./output/results.json --no-llm
```

### FastAPI REST Service
Start the interactive API server:
```bash
python main.py --serve --port 8000
```
Then visit **`http://localhost:8000/docs`** for interactive Swagger documentation.

**API Endpoints:**
* `POST /screen` – Trigger batch screening on a directory (`{"input_dir": "./resumes"}`).
* `GET /results` – Retrieve the latest ranked results and batch summary.
* `GET /candidate/{name}` – Query deep evaluation breakdown for a specific candidate.
* `GET /health` – Health check endpoint.

---

## 🧪 Running Tests
Execute the full unit and integration test suite:
```bash
pytest -v
```

---

## 📂 Project Architecture

```
Kasparro/
├── resumes/                      # Ingested PDF candidate resumes
├── output/
│   ├── results.json              # Standard machine-readable ranked results
│   └── results.csv               # CSV export
├── src/
│   ├── config.py                 # Central configuration, scoring weights & thresholds
│   ├── models.py                 # Pydantic schemas (Results, Scores, Batch Summary)
│   ├── extractor.py              # Robust PDF text parsing & metadata extraction
│   ├── filters.py                # Strict rule-based Python & AI eligibility filters
│   ├── scoring.py                # 100-point rubric engine & penalty calculator
│   ├── github.py                 # GitHub profile enrichment with caching & fallbacks
│   ├── llm.py                    # Gemini LLM adapter with graceful fallbacks
│   ├── pipeline.py               # Async batch processor with bounded concurrency
│   └── api.py                    # FastAPI service application
├── tests/
│   ├── test_extractor.py         # Tests for text extraction & name heuristics
│   ├── test_filters.py           # Tests for hard eligibility filtering
│   ├── test_scoring.py           # Tests for rubric weights & shallow wrapper penalties
│   └── test_pipeline.py          # Integration tests for batch screening
├── main.py                       # CLI entrypoint with terminal table reporting
├── requirements.txt              # Production dependencies
├── .env.example                  # Template configuration file
└── README.md                     # Documentation & design decisions
```

---

## 🎯 Design Decisions

### 1. Hard Filtering Strategy
* **Rule-Based Pre-Filter**: Performed deterministically *outside* the LLM. This eliminates unnecessary token costs, prevents hallucinations from admitting unqualified candidates, and guarantees strict enforcement of core criteria.
* **Two-Condition Gating**:
  1. **Python Stack Evidence**: Requires explicit evidence of Python and its core ecosystem (`python`, `fastapi`, `django`, `flask`, `pytorch`, `asyncio`, `sqlalchemy`).
  2. **AI / Agentic / RAG Evidence**: Requires concrete exposure to AI systems (`langchain`, `langgraph`, `llamaindex`, `rag`, `vector search`, `chromadb`, `tool-calling`, `multi-agent`, `eval pipelines`).
* **Permissive Stack Allowance**: Candidates with supporting frontend skills (e.g. JavaScript, React, Next.js) are **not** rejected as long as Python + AI conditions are satisfied.

### 2. 100-Point Scoring Strategy
* **AI / Agentic / RAG Project Depth (40 pts)**: Rewards end-to-end AI implementations—autonomous agents, stateful graphs, vector retrieval, embeddings, and tool orchestration.
* **Python & Backend Engineering (30 pts)**: Rewards FastAPI, async programming (`asyncio`), and robust databases (`PostgreSQL`, `Redis`).
* **Cloud / Deployment / Full Stack (15 pts)**: Rewards Docker, GCP, CI/CD pipelines, and React/Next.js when integrated into end-to-end architectures.
* **GitHub Telemetry (10 pts)**: Quantifies recent engineering velocity (0–5 pts) and maintained repositories relevant to Python/AI (0–5 pts).
* **Engineering Depth Signals (5 pts)**: Rewards production discipline including `pytest`, clean architecture, caching, task queues, and observability.
* **Project Quality Penalties**: Deducts 5–15 points for shallow API wrappers (e.g., basic Prompt + Streamlit chatbots with no retrieval or state management) and generic tutorial clones.

### 3. AI / LLM Usage & Robustness
* **Structured Output**: Uses Pydantic schemas for predictable JSON serialization.
* **Pluggable Provider Abstraction**: LLM logic is encapsulated behind `BaseLLMProvider` so models can be swapped effortlessly.
* **Zero-Crash Degradation**: If an LLM call fails, times out, or API quota is exceeded, the system automatically falls back to the deterministic rubric without crashing the batch.

### 4. GitHub Scoring & Rate-Limit Handling
* **In-Memory TTL Cache**: Prevents duplicate HTTP requests across runs for the same candidate.
* **Non-Blocking Fallback**: Rate limits (403), private profiles, or network timeouts assign a neutral fallback score and record an enrichment note instead of halting the pipeline.

---

## 🔭 If I Had More Time

1. **Semantic Vector Chunking for Complex Resumes**: Implement chunk-level embedding search over multi-page project descriptions to extract nuanced evidence of system complexity and deployment ownership.
2. **Deep GitHub Commit & PR Analysis**: Query commit history and PR reviews to differentiate between active solo codebase development vs. forked repositories.
3. **Interactive Visual Dashboard**: Build a lightweight Next.js/React frontend with interactive score filters, skill radar charts, and resume side-by-side comparison views.
4. **Automated Skill Discrepancy Verification**: Cross-reference claimed resume skills against actual repository languages and commit frequency to detect inflated skill lists.
