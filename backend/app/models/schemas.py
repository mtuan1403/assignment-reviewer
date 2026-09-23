from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field
from backend.app.models.domain import (
    DocumentType,
    RequirementCategory,
    RequirementStatus,
    PriorityLevel,
    PipelineStage,
)


class DocumentMetadata(BaseModel):
    filename: str
    document_type: DocumentType
    page_count: int
    paragraph_count: int
    char_count: int


class DocumentChunk(BaseModel):
    chunk_id: str
    document_type: DocumentType
    page: int
    section: str = "General"
    text: str
    token_count: int = 0


class Requirement(BaseModel):
    id: str = Field(description="Unique requirement ID, e.g. R1, R2")
    description: str = Field(description="Clear, concise description of the requirement")
    category: RequirementCategory = Field(default=RequirementCategory.EXPLICIT)
    mandatory: bool = Field(default=True, description="Whether this is mandatory or optional")
    source_text: str = Field(description="Exact excerpt from the assignment spec")
    source_page: int = Field(default=1, description="Page number where the requirement appears")


class RequirementExtractionResult(BaseModel):
    requirements: List[Requirement] = Field(default_factory=list)


class RubricCriterion(BaseModel):
    id: str = Field(description="Unique criterion ID, e.g. C1, C2")
    name: str = Field(description="Name of the criterion, e.g. Critical Analysis")
    weight: Optional[float] = Field(default=None, description="Percentage weight if specified")
    levels: Dict[str, str] = Field(
        default_factory=dict,
        description="Map of performance level name (e.g. HD, D, CR, P, or High/Med/Low) to descriptor text",
    )
    source_page: int = Field(default=1, description="Page number where the criterion appears")


class RubricExtractionResult(BaseModel):
    criteria: List[RubricCriterion] = Field(default_factory=list)


class EvidenceItem(BaseModel):
    page: int
    section: str = "General"
    chunk_id: str
    quote: str
    relevance_score: float = 1.0


class RequirementEvaluation(BaseModel):
    requirement_id: str
    status: RequirementStatus
    confidence: float = Field(ge=0.0, le=1.0)
    reason: str
    evidence: List[EvidenceItem] = Field(default_factory=list)
    recommendation: str


class RubricEvaluation(BaseModel):
    criterion_id: str
    criterion_name: str
    estimated_level: str
    confidence: float = Field(ge=0.0, le=1.0)
    strengths: List[str] = Field(default_factory=list)
    weaknesses: List[str] = Field(default_factory=list)
    evidence: List[EvidenceItem] = Field(default_factory=list)
    recommendations: List[str] = Field(default_factory=list)


class PriorityItem(BaseModel):
    priority: PriorityLevel
    issue: str
    why_it_matters: str
    evidence: List[EvidenceItem] = Field(default_factory=list)
    suggested_action: str


class RequirementsCoverageSummary(BaseModel):
    total: int
    covered: int
    partial: int
    missing: int
    unclear: int
    coverage_percentage: float


class OverallReview(BaseModel):
    review_id: str
    created_at: str
    summary: str
    requirements_coverage: RequirementsCoverageSummary
    rubric_alignment: Dict[str, Any]
    requirement_evaluations: List[RequirementEvaluation] = Field(default_factory=list)
    rubric_evaluations: List[RubricEvaluation] = Field(default_factory=list)
    main_strengths: List[str] = Field(default_factory=list)
    main_weaknesses: List[str] = Field(default_factory=list)
    priority_improvements: List[PriorityItem] = Field(default_factory=list)
    evidence_summary: str
    llm_provider: str = "mock"
    llm_model: str = "offline-engine"
    limitations_disclaimer: str = (
        "AI-estimated rubric alignment and requirement analysis are for educational feedback and self-review purposes only. "
        "This is not an official university grade, marking decision, or academic assessment."
    )



class ProgressStatus(BaseModel):
    review_id: str
    stage: PipelineStage
    percent: int
    message: str
    logs: List[str] = Field(default_factory=list)
    error: Optional[str] = None
