import pytest
from pydantic import ValidationError
from backend.app.models.domain import RequirementCategory, RequirementStatus, PriorityLevel
from backend.app.models.schemas import (
    Requirement,
    RubricCriterion,
    EvidenceItem,
    RequirementEvaluation,
    RubricEvaluation,
    PriorityItem,
    RequirementsCoverageSummary,
)


def test_requirement_schema():
    req = Requirement(
        id="R1",
        description="Evaluate two architectural patterns.",
        category=RequirementCategory.EXPLICIT,
        mandatory=True,
        source_text="Students must evaluate at least two patterns.",
        source_page=1,
    )
    assert req.id == "R1"
    assert req.mandatory is True


def test_rubric_schema():
    crit = RubricCriterion(
        id="C1",
        name="Critical Analysis",
        weight=30.0,
        levels={"HD": "Outstanding", "D": "Good", "CR": "Adequate", "P": "Basic"},
        source_page=2,
    )
    assert crit.name == "Critical Analysis"
    assert "HD" in crit.levels


def test_requirement_evaluation_validation():
    ev = EvidenceItem(
        page=2,
        section="Section 2",
        chunk_id="chunk_0001",
        quote="Exact quote from draft.",
    )
    evaluation = RequirementEvaluation(
        requirement_id="R1",
        status=RequirementStatus.COVERED,
        confidence=0.95,
        reason="Good evidence found.",
        evidence=[ev],
        recommendation="No changes needed.",
    )
    assert evaluation.status == RequirementStatus.COVERED

    # Invalid confidence should raise ValidationError
    with pytest.raises(ValidationError):
        RequirementEvaluation(
            requirement_id="R1",
            status=RequirementStatus.COVERED,
            confidence=1.5,  # must be <= 1.0
            reason="Invalid",
            recommendation="Invalid",
        )
