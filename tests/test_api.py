"""
API Endpoint integration tests using FastAPI TestClient.
"""

from fastapi.testclient import TestClient
from src.api import app

client = TestClient(app)


def test_health_check_endpoint():
    """Verify GET /health returns 200 OK and healthy status."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_screen_endpoint_and_get_results():
    """Verify POST /screen triggers execution and GET /results returns data."""
    payload = {
        "input_dir": "./resumes",
        "output_path": "./output/results.json",
        "use_llm": False,
        "concurrency": 5
    }
    screen_resp = client.post("/screen", json=payload)
    assert screen_resp.status_code == 200
    data = screen_resp.json()
    assert "batch_summary" in data
    assert "results" in data
    assert data["batch_summary"]["total_resumes"] == 50

    # Test GET /results
    results_resp = client.get("/results")
    assert results_resp.status_code == 200
    assert results_resp.json()["batch_summary"]["eligible"] > 0
