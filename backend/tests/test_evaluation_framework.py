import pytest
from backend.app.models.domain import RequirementStatus
from backend.app.services.evaluation.metrics import EvaluationMetricsCalculator


def test_compute_requirement_metrics():
    y_true = [
        RequirementStatus.COVERED,
        RequirementStatus.COVERED,
        RequirementStatus.PARTIAL,
        RequirementStatus.MISSING,
    ]
    y_pred = [
        RequirementStatus.COVERED,
        RequirementStatus.PARTIAL,  # 1 mistake
        RequirementStatus.PARTIAL,
        RequirementStatus.MISSING,
    ]

    metrics = EvaluationMetricsCalculator.compute_requirement_metrics(y_true, y_pred)
    assert metrics["accuracy"] == 0.75
    assert "macro_f1" in metrics
    assert "per_class" in metrics
    assert metrics["sample_count"] == 4


def test_compute_rubric_metrics():
    y_true = ["HD", "D", "CR", "P"]
    y_pred = ["HD", "D", "CR", "P"]

    metrics = EvaluationMetricsCalculator.compute_rubric_metrics(y_true, y_pred)
    assert metrics["accuracy"] == 1.0
    assert metrics["cohen_kappa_quadratic"] == 1.0

    # Test with one off-by-one level
    y_pred_off = ["HD", "CR", "CR", "P"]
    metrics_off = EvaluationMetricsCalculator.compute_rubric_metrics(y_true, y_pred_off)
    assert metrics_off["accuracy"] == 0.75
    assert metrics_off["cohen_kappa_quadratic"] > 0.6


def test_evidence_groundedness():
    source_doc = (
        "Global Retail Dynamics migrates workloads to AWS EKS. "
        "Kubernetes provides fine-grained auto-scaling and environment parity."
    )

    valid_quotes = [
        "Global Retail Dynamics migrates workloads to AWS EKS.",
        "fine-grained auto-scaling and environment parity",
    ]

    res = EvaluationMetricsCalculator.compute_evidence_groundedness(valid_quotes, source_doc)
    assert res["groundedness_score"] == 1.0
    assert res["hallucinated_count"] == 0

    hallucinated_quotes = [
        "Completely fabricated sentence that does not exist in the assignment at all."
    ]
    res_hal = EvaluationMetricsCalculator.compute_evidence_groundedness(hallucinated_quotes, source_doc)
    assert res_hal["hallucinated_count"] == 1
    assert res_hal["groundedness_score"] == 0.0
