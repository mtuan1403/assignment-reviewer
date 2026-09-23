from pathlib import Path
import pytest
from backend.app.services.pipeline.orchestrator import ReviewPipelineOrchestrator
from backend.app.services.llm.mock_provider import MockProvider
from backend.app.services.vector_store.chroma_service import ChromaVectorStore
from backend.app.models.domain import PipelineStage

SAMPLE_DIR = Path(__file__).resolve().parent.parent.parent / "sample_data"


def test_full_pipeline_run(tmp_path):
    vector_store = ChromaVectorStore(persist_directory=tmp_path / "vector_db")
    llm = MockProvider()
    orchestrator = ReviewPipelineOrchestrator(vector_store=vector_store, llm_provider=llm)

    spec_file = SAMPLE_DIR / "sample_specification.txt"
    rubric_file = SAMPLE_DIR / "sample_rubric.txt"
    draft_file = SAMPLE_DIR / "sample_student_draft.txt"

    review_id = "test_pipeline_run_01"
    review = orchestrator.run_review(
        spec_path=spec_file,
        rubric_path=rubric_file,
        draft_path=draft_file,
        review_id=review_id,
    )

    assert review.review_id == review_id
    assert len(review.requirement_evaluations) > 0
    assert len(review.rubric_evaluations) > 0
    assert review.requirements_coverage.total == len(review.requirement_evaluations)
    assert len(review.priority_improvements) > 0
    assert "not an official university grade" in review.limitations_disclaimer

    # Check progress tracking
    progress = orchestrator.get_progress(review_id)
    assert progress.stage == PipelineStage.COMPLETED
    assert progress.percent == 100
    assert len(progress.logs) > 0


def test_pipeline_run_without_rubric(tmp_path):
    vector_store = ChromaVectorStore(persist_directory=tmp_path / "vector_db_no_rubric")
    llm = MockProvider()
    orchestrator = ReviewPipelineOrchestrator(vector_store=vector_store, llm_provider=llm)

    spec_file = SAMPLE_DIR / "sample_specification.txt"
    draft_file = SAMPLE_DIR / "sample_student_draft.txt"

    review_id = "test_pipeline_no_rubric_02"
    review = orchestrator.run_review(
        spec_path=spec_file,
        rubric_path=None,  # Optional rubric omitted
        draft_path=draft_file,
        review_id=review_id,
    )

    assert review.review_id == review_id
    assert len(review.requirement_evaluations) > 0
    assert review.requirements_coverage.total == len(review.requirement_evaluations)
    assert review.summary != ""
    assert len(review.priority_improvements) > 0
