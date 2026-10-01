"""
FastAPI Interface for the AI Resume Screening System.
Provides RESTful endpoints to trigger resume screening runs and query candidate rankings.
"""

from typing import Optional
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from src.models import ScreeningResponse
from src.pipeline import ResumeScreeningPipeline, save_results_to_json

app = FastAPI(
    title="AI Resume Screening & Ranking API",
    version="1.0.0",
    description="Production-minded AI resume screening service evaluating Python/AI candidates."
)

# In-memory storage for latest batch response
_LATEST_SCREENING_RESPONSE: Optional[ScreeningResponse] = None


class ScreenRequest(BaseModel):
    input_dir: str = "./resumes"
    output_path: Optional[str] = "./output/results.json"
    use_llm: bool = True
    concurrency: int = 5


@app.get("/health", tags=["System"])
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "AI Resume Screening Pipeline"}


@app.post("/screen", response_model=ScreeningResponse, tags=["Screening"])
async def trigger_screening(req: ScreenRequest):
    """
    Trigger screening and ranking pipeline on an input folder of resumes.
    """
    global _LATEST_SCREENING_RESPONSE
    pipeline = ResumeScreeningPipeline(concurrency=req.concurrency, use_llm=req.use_llm)

    try:
        response = await pipeline.screen_directory(req.input_dir)
        _LATEST_SCREENING_RESPONSE = response

        if req.output_path:
            save_results_to_json(response, req.output_path, format_type="standard")

        return response
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Screening failed: {e}")


@app.get("/results", response_model=ScreeningResponse, tags=["Results"])
async def get_results():
    """
    Retrieve results of the most recent screening batch.
    """
    if _LATEST_SCREENING_RESPONSE is None:
        raise HTTPException(status_code=404, detail="No screening run has been executed yet. Call POST /screen first.")
    return _LATEST_SCREENING_RESPONSE


@app.get("/candidate/{name}", tags=["Results"])
async def get_candidate_details(name: str):
    """
    Get detailed breakdown for a specific candidate by name or filename.
    """
    if _LATEST_SCREENING_RESPONSE is None:
        raise HTTPException(status_code=404, detail="No screening run executed yet.")

    name_lower = name.lower()
    for candidate in _LATEST_SCREENING_RESPONSE.results:
        if name_lower in candidate.candidate_name.lower() or name_lower in candidate.file_name.lower():
            return candidate

    raise HTTPException(status_code=404, detail=f"Candidate matching '{name}' not found.")
