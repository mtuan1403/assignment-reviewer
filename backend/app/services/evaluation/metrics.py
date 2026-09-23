from typing import List, Dict, Any, Optional
import numpy as np
from backend.app.models.domain import RequirementStatus
from backend.app.core.logging import get_logger

logger = get_logger(__name__)


class EvaluationMetricsCalculator:
    """
    Academic Evaluation Framework:
    Computes Precision, Recall, F1, Cohen's Kappa, and Groundedness metrics
    to benchmark Plain LLM vs LLM+RAG vs Rubric-Aware LLM+RAG.
    """

    @staticmethod
    def compute_requirement_metrics(
        y_true: List[RequirementStatus],
        y_pred: List[RequirementStatus],
    ) -> Dict[str, Any]:
        """
        Calculates multi-class Precision, Recall, and F1 for requirement status classification.
        """
        if len(y_true) != len(y_pred):
            raise ValueError(f"Mismatch in truth ({len(y_true)}) and pred ({len(y_pred)}) lengths.")

        labels = [s.value for s in RequirementStatus]
        y_true_str = [s.value if isinstance(s, RequirementStatus) else str(s) for s in y_true]
        y_pred_str = [s.value if isinstance(s, RequirementStatus) else str(s) for s in y_pred]

        per_class: Dict[str, Dict[str, float]] = {}
        precisions = []
        recalls = []
        f1s = []

        for label in labels:
            tp = sum(1 for yt, yp in zip(y_true_str, y_pred_str) if yt == label and yp == label)
            fp = sum(1 for yt, yp in zip(y_true_str, y_pred_str) if yt != label and yp == label)
            fn = sum(1 for yt, yp in zip(y_true_str, y_pred_str) if yt == label and yp != label)

            precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
            recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
            f1 = (2 * precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0

            per_class[label] = {
                "precision": round(precision, 4),
                "recall": round(recall, 4),
                "f1": round(f1, 4),
                "support": sum(1 for yt in y_true_str if yt == label),
            }
            precisions.append(precision)
            recalls.append(recall)
            f1s.append(f1)

        total_correct = sum(1 for yt, yp in zip(y_true_str, y_pred_str) if yt == yp)
        accuracy = total_correct / len(y_true_str) if y_true_str else 0.0

        return {
            "accuracy": round(accuracy, 4),
            "macro_precision": round(float(np.mean(precisions)), 4),
            "macro_recall": round(float(np.mean(recalls)), 4),
            "macro_f1": round(float(np.mean(f1s)), 4),
            "per_class": per_class,
            "sample_count": len(y_true),
        }

    @staticmethod
    def compute_rubric_metrics(
        y_true: List[str],
        y_pred: List[str],
        grade_scale: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        Computes Accuracy, Macro F1, and Quadratic Weighted Cohen's Kappa for ordinal rubric levels.
        """
        if len(y_true) != len(y_pred):
            raise ValueError(f"Mismatch in truth ({len(y_true)}) and pred ({len(y_pred)}) lengths.")

        scale = grade_scale or ["F", "P", "CR", "D", "HD"]
        scale_map = {lvl.upper(): idx for idx, lvl in enumerate(scale)}

        total = len(y_true)
        if total == 0:
            return {"accuracy": 0.0, "cohen_kappa_quadratic": 0.0}

        y_t_upper = [y.upper() for y in y_true]
        y_p_upper = [y.upper() for y in y_pred]

        correct = sum(1 for t, p in zip(y_t_upper, y_p_upper) if t == p)
        accuracy = correct / total

        # Quadratic Weighted Kappa
        N = len(scale)
        observed_matrix = np.zeros((N, N), dtype=float)
        for t, p in zip(y_t_upper, y_p_upper):
            t_idx = scale_map.get(t, 0)
            p_idx = scale_map.get(p, 0)
            observed_matrix[t_idx, p_idx] += 1.0

        hist_true = observed_matrix.sum(axis=1)
        hist_pred = observed_matrix.sum(axis=0)
        expected_matrix = np.outer(hist_true, hist_pred) / total

        weight_matrix = np.zeros((N, N), dtype=float)
        for i in range(N):
            for j in range(N):
                weight_matrix[i, j] = float((i - j) ** 2) / float((N - 1) ** 2)

        numerator = np.sum(weight_matrix * observed_matrix)
        denominator = np.sum(weight_matrix * expected_matrix)

        kappa = 1.0 - (numerator / denominator) if denominator > 0 else 1.0

        return {
            "accuracy": round(accuracy, 4),
            "cohen_kappa_quadratic": round(float(kappa), 4),
            "sample_count": total,
        }

    @staticmethod
    def compute_evidence_groundedness(
        evidence_quotes: List[str],
        source_document_text: str,
    ) -> Dict[str, Any]:
        """
        Measures citation groundedness and verbatim faithfulness against the student document.
        """
        if not evidence_quotes:
            return {"groundedness_score": 1.0, "total_quotes": 0, "hallucinated_count": 0}

        doc_lower = source_document_text.lower()
        verified_count = 0
        hallucinated_count = 0

        for quote in evidence_quotes:
            q_clean = quote.strip().lower()
            if not q_clean:
                continue

            # Check if entire quote or 80% contiguous words exist in doc
            words = q_clean.split()
            if q_clean in doc_lower:
                verified_count += 1
            elif len(words) >= 4:
                window_size = min(len(words), 5)
                found = any(" ".join(words[i : i + window_size]) in doc_lower for i in range(len(words) - window_size + 1))
                if found:
                    verified_count += 1
                else:
                    hallucinated_count += 1
            else:
                hallucinated_count += 1

        total = len(evidence_quotes)
        groundedness = verified_count / total if total > 0 else 1.0

        return {
            "groundedness_score": round(groundedness, 4),
            "total_quotes": total,
            "verified_count": verified_count,
            "hallucinated_count": hallucinated_count,
        }
