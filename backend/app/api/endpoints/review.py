import shutil
import uuid
from pathlib import Path
from typing import Optional
from fastapi import APIRouter, UploadFile, File, BackgroundTasks, HTTPException, status

from backend.app.core.config import settings
from backend.app.core.logging import get_logger
from backend.app.models.schemas import OverallReview, ProgressStatus
from backend.app.services.pipeline.orchestrator import ReviewPipelineOrchestrator
from backend.app.services.parser.base import ParsingException, EmptyDocumentException, ScannedDocumentException

logger = get_logger(__name__)
router = APIRouter()

# Shared singleton orchestrator
orchestrator = ReviewPipelineOrchestrator()

ALLOWED_EXTENSIONS = {".pdf", ".docx", ".doc", ".txt"}


def validate_file(file: UploadFile, field_name: str):
    suffix = Path(file.filename or "").suffix.lower()
    if suffix not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid file extension for {field_name} ('{file.filename}'). Supported formats: PDF, DOCX, TXT.",
        )


def run_pipeline_task(spec_path: Path, rubric_path: Optional[Path], draft_path: Path, review_id: str):
    try:
        orchestrator.run_review(
            spec_path=spec_path,
            rubric_path=rubric_path,
            draft_path=draft_path,
            review_id=review_id,
        )
    except (EmptyDocumentException, ScannedDocumentException, ParsingException) as e:
        logger.error(f"Document parsing error in task {review_id}: {e}")
    except Exception as e:
        logger.error(f"Unhandled error in task {review_id}: {e}", exc_info=True)


@router.post("/start", response_model=dict)
async def start_review(
    background_tasks: BackgroundTasks,
    spec_file: UploadFile = File(...),
    draft_file: UploadFile = File(...),
    rubric_file: Optional[UploadFile] = File(None),
):
    validate_file(spec_file, "Assignment Specification")
    validate_file(draft_file, "Student Draft")
    if rubric_file and rubric_file.filename:
        validate_file(rubric_file, "Rubric")

    review_id = str(uuid.uuid4())
    upload_dir = settings.uploads_dir / review_id
    upload_dir.mkdir(parents=True, exist_ok=True)

    spec_path = upload_dir / f"spec_{spec_file.filename}"
    draft_path = upload_dir / f"draft_{draft_file.filename}"

    with open(spec_path, "wb") as buffer:
        shutil.copyfileobj(spec_file.file, buffer)
    with open(draft_path, "wb") as buffer:
        shutil.copyfileobj(draft_file.file, buffer)

    rubric_path: Optional[Path] = None
    if rubric_file and rubric_file.filename:
        rubric_path = upload_dir / f"rubric_{rubric_file.filename}"
        with open(rubric_path, "wb") as buffer:
            shutil.copyfileobj(rubric_file.file, buffer)

    # Initialize progress status
    orchestrator.get_progress(review_id)

    # Execute in background
    background_tasks.add_task(
        run_pipeline_task,
        spec_path=spec_path,
        rubric_path=rubric_path,
        draft_path=draft_path,
        review_id=review_id,
    )

    return {
        "review_id": review_id,
        "message": "Assignment review initiated successfully.",
        "status": "processing",
    }


@router.post("/sample", response_model=dict)
async def start_sample_review(background_tasks: BackgroundTasks):
    sample_dir = Path(__file__).resolve().parent.parent.parent.parent.parent / "sample_data"
    spec_path = sample_dir / "sample_specification.txt"
    rubric_path = sample_dir / "sample_rubric.txt"
    draft_path = sample_dir / "sample_student_draft.txt"

    if not (spec_path.exists() and rubric_path.exists() and draft_path.exists()):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sample assignment files were not found on the server.",
        )

    review_id = str(uuid.uuid4())
    upload_dir = settings.uploads_dir / review_id
    upload_dir.mkdir(parents=True, exist_ok=True)

    dest_spec = upload_dir / spec_path.name
    dest_rubric = upload_dir / rubric_path.name
    dest_draft = upload_dir / draft_path.name

    shutil.copy(spec_path, dest_spec)
    shutil.copy(rubric_path, dest_rubric)
    shutil.copy(draft_path, dest_draft)

    background_tasks.add_task(
        run_pipeline_task,
        spec_path=dest_spec,
        rubric_path=dest_rubric,
        draft_path=dest_draft,
        review_id=review_id,
    )

    return {
        "review_id": review_id,
        "message": "Sample assignment review initiated successfully.",
        "status": "processing",
    }


@router.get("/{review_id}/progress", response_model=ProgressStatus)
def get_review_progress(review_id: str):
    return orchestrator.get_progress(review_id)


@router.get("/{review_id}", response_model=OverallReview)
def get_review_details(review_id: str):
    review = orchestrator.load_review(review_id)
    if not review:
        prog = orchestrator.get_progress(review_id)
        if prog.error:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Review failed during processing: {prog.error}",
            )
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Review '{review_id}' is still in progress or does not exist.",
        )
    return review


@router.get("/{review_id}/chunks")
def get_review_chunks(review_id: str):
    try:
        chunks = orchestrator.vector_store.get_all_chunks(review_id)
        return {"review_id": review_id, "total_chunks": len(chunks), "chunks": chunks}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch indexed chunks: {e}")
