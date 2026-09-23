from enum import Enum


class DocumentType(str, Enum):
    ASSIGNMENT_SPEC = "assignment_spec"
    RUBRIC = "rubric"
    STUDENT_DRAFT = "student_draft"


class RequirementCategory(str, Enum):
    EXPLICIT = "explicit"
    OPTIONAL_SUGGESTION = "optional_suggestion"
    FORMATTING = "formatting"
    ASSESSMENT = "assessment"
    DELIVERABLE = "deliverable"


class RequirementStatus(str, Enum):
    COVERED = "COVERED"
    PARTIAL = "PARTIAL"
    MISSING = "MISSING"
    UNCLEAR = "UNCLEAR"


class PriorityLevel(str, Enum):
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


class PipelineStage(str, Enum):
    IDLE = "idle"
    UPLOADING = "uploading"
    PARSING = "parsing"
    EXTRACTING_REQUIREMENTS = "extracting_requirements"
    EXTRACTING_RUBRIC = "extracting_rubric"
    CHUNKING_ASSIGNMENT = "chunking_assignment"
    INDEXING_VECTORS = "indexing_vectors"
    EVALUATING_REQUIREMENTS = "evaluating_requirements"
    EVALUATING_RUBRIC = "evaluating_rubric"
    GROUNDING_EVIDENCE = "grounding_evidence"
    SYNTHESIZING_REVIEW = "synthesizing_review"
    COMPLETED = "completed"
    FAILED = "failed"
