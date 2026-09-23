from fastapi.testclient import TestClient
from pathlib import Path
from backend.app.main import app

client = TestClient(app)
SAMPLE_DIR = Path(__file__).resolve().parent.parent.parent / "sample_data"


def test_health_endpoint():
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "llm_provider" in data


def test_sample_review_endpoint():
    response = client.post("/api/reviews/sample")
    assert response.status_code == 200
    data = response.json()
    assert "review_id" in data
    assert data["status"] == "processing"

    review_id = data["review_id"]
    prog_res = client.get(f"/api/reviews/{review_id}/progress")
    assert prog_res.status_code == 200
    prog_data = prog_res.json()
    assert "stage" in prog_data


def test_upload_invalid_file_type():
    files = {
        "spec_file": ("spec.exe", b"invalid executable", "application/octet-stream"),
        "rubric_file": ("rubric.pdf", b"%PDF-1.4...", "application/pdf"),
        "draft_file": ("draft.pdf", b"%PDF-1.4...", "application/pdf"),
    }
    response = client.post("/api/reviews/start", files=files)
    assert response.status_code == 400
    assert "Invalid file extension" in response.json()["detail"]


def test_start_review_without_rubric():
    files = {
        "spec_file": ("spec.txt", b"Specification text...", "text/plain"),
        "draft_file": ("draft.txt", b"Student draft text...", "text/plain"),
    }
    response = client.post("/api/reviews/start", files=files)
    assert response.status_code == 200
    data = response.json()
    assert "review_id" in data
    assert data["status"] == "processing"
