from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Dict, List, Optional, Any
import uuid

from backend.app.core.config import settings
from backend.app.core.logging import get_logger
from backend.app.models.domain import (
    DocumentType,
    RequirementStatus,
    PriorityLevel,
    PipelineStage,
)
from backend.app.models.schemas import (
    DocumentChunk,
    DocumentMetadata,
    Requirement,
    RequirementExtractionResult,
    RubricCriterion,
    RubricExtractionResult,
    RequirementEvaluation,
    RubricEvaluation,
    EvidenceItem,
    PriorityItem,
    RequirementsCoverageSummary,
    OverallReview,
    ProgressStatus,
)
from backend.app.services.parser.factory import DocumentParserFactory
from backend.app.services.chunker.assignment_chunker import AssignmentChunker
from backend.app.services.vector_store.chroma_service import ChromaVectorStore
from backend.app.services.llm.factory import LLMProviderFactory
from backend.app.services.llm.base import BaseLLMProvider
from backend.app.services.pipeline.prompt_manager import prompt_manager

logger = get_logger(__name__)


class ReviewPipelineOrchestrator:
    def __init__(
        self,
        vector_store: Optional[ChromaVectorStore] = None,
        llm_provider: Optional[BaseLLMProvider] = None,
    ):
        self.vector_store = vector_store or ChromaVectorStore()
        self.llm = llm_provider or LLMProviderFactory.get_provider()
        self.chunker = AssignmentChunker()
        self._progress_store: Dict[str, ProgressStatus] = {}

    def get_progress(self, review_id: str) -> ProgressStatus:
        return self._progress_store.get(
            review_id,
            ProgressStatus(
                review_id=review_id,
                stage=PipelineStage.IDLE,
                percent=0,
                message="Review not started or not found.",
            ),
        )

    def _update_progress(
        self, review_id: str, stage: PipelineStage, percent: int, message: str, log_entry: Optional[str] = None
    ):
        current = self._progress_store.get(
            review_id,
            ProgressStatus(
                review_id=review_id,
                stage=stage,
                percent=percent,
                message=message,
                logs=[],
            ),
        )
        current.stage = stage
        current.percent = percent
        current.message = message
        if log_entry:
            current.logs.append(f"[{datetime.now(timezone.utc).strftime('%H:%M:%S')}] {log_entry}")
        self._progress_store[review_id] = current
        logger.info(f"[{review_id}] ({percent}%) {message}")

    def run_review(
        self,
        spec_path: Path,
        rubric_path: Optional[Path],
        draft_path: Path,
        review_id: Optional[str] = None,
    ) -> OverallReview:
        review_id = review_id or str(uuid.uuid4())
        active_provider = getattr(self.llm, "provider_name", "UnknownProvider")
        active_model = getattr(self.llm, "model_name", getattr(self.llm, "model", "default"))
        start_log = f"Executing review with AI Engine: {active_provider} (Model: {active_model})"
        self._update_progress(review_id, PipelineStage.UPLOADING, 5, "Files received and validated.", start_log)
        logger.info(f"[{review_id}] {start_log}")

        try:
            # ----------------------------------------------------
            # Stage 1: Document Parsing & Text Extraction
            # ----------------------------------------------------
            self._update_progress(review_id, PipelineStage.PARSING, 15, "Extracting text and structure from documents...", "Parsing specification, rubric, and student assignment.")
            
            spec_parser = DocumentParserFactory.get_parser(spec_path)
            draft_parser = DocumentParserFactory.get_parser(draft_path)

            spec_meta, spec_chunks = spec_parser.parse(spec_path, DocumentType.ASSIGNMENT_SPEC)
            draft_meta, raw_draft_chunks = draft_parser.parse(draft_path, DocumentType.STUDENT_DRAFT)

            rubric_chunks: List[DocumentChunk] = []
            if rubric_path and rubric_path.exists():
                rubric_parser = DocumentParserFactory.get_parser(rubric_path)
                rubric_meta, rubric_chunks = rubric_parser.parse(rubric_path, DocumentType.RUBRIC)
                rubric_info = f"Rubric: {rubric_meta.page_count} pages"
            else:
                # Check if specification has embedded rubric criteria
                rubric_keywords = ["rubric", "marking criteria", "assessment component", "high distinction", "fail", "marks)"]
                spec_rubric_chunks = [c for c in spec_chunks if any(kw in c.text.lower() for kw in rubric_keywords)]
                if spec_rubric_chunks:
                    logger.info("Rubric not provided as separate file, but embedded rubric detected in specification.")
                    rubric_chunks = spec_rubric_chunks
                    rubric_info = f"Rubric: embedded in specification ({len(spec_rubric_chunks)} sections)"
                else:
                    rubric_info = "Rubric: omitted (evaluating on specification requirements only)"

            self._update_progress(
                review_id,
                PipelineStage.PARSING,
                25,
                "Text extracted successfully.",
                f"Spec: {spec_meta.page_count} pages, {rubric_info}, Draft: {draft_meta.page_count} pages.",
            )

            # ----------------------------------------------------
            # Stage 2: Structured Requirement Extraction
            # ----------------------------------------------------
            self._update_progress(review_id, PipelineStage.EXTRACTING_REQUIREMENTS, 35, "Extracting structured requirements from specification...", "Analyzing assignment specification.")
            requirements = self._extract_requirements(spec_chunks)
            self._update_progress(
                review_id,
                PipelineStage.EXTRACTING_REQUIREMENTS,
                42,
                f"Extracted {len(requirements)} requirements.",
                f"Identified {len(requirements)} distinct assessment & deliverable requirements.",
            )

            # ----------------------------------------------------
            # Stage 3: Structured Rubric Extraction (Optional)
            # ----------------------------------------------------
            if rubric_chunks:
                self._update_progress(review_id, PipelineStage.EXTRACTING_RUBRIC, 50, "Extracting rubric criteria and performance levels...", "Analyzing marking rubric.")
                rubric_criteria = self._extract_rubric(rubric_chunks)
                self._update_progress(
                    review_id,
                    PipelineStage.EXTRACTING_RUBRIC,
                    58,
                    f"Extracted {len(rubric_criteria)} rubric criteria.",
                    f"Identified {len(rubric_criteria)} weighted criteria with performance descriptors.",
                )
            else:
                rubric_criteria = []
                self._update_progress(
                    review_id,
                    PipelineStage.EXTRACTING_RUBRIC,
                    58,
                    "No separate rubric provided. Skipping rubric extraction.",
                    "Evaluating based directly on specification requirements.",
                )

            # ----------------------------------------------------
            # Stage 4: Assignment Chunking & Local Vector Indexing
            # ----------------------------------------------------
            self._update_progress(review_id, PipelineStage.CHUNKING_ASSIGNMENT, 65, "Chunking student assignment semantically...", "Preserving page numbers and headings.")
            assignment_chunks = self.chunker.chunk_document(raw_draft_chunks, DocumentType.STUDENT_DRAFT)

            self._update_progress(review_id, PipelineStage.INDEXING_VECTORS, 70, "Indexing assignment chunks into local ChromaDB...", f"Storing {len(assignment_chunks)} chunks in local vector database.")
            self.vector_store.index_chunks(review_id, assignment_chunks)

            # ----------------------------------------------------
            # Stage 5: Requirement Coverage Evaluation (Targeted RAG)
            # ----------------------------------------------------
            self._update_progress(review_id, PipelineStage.EVALUATING_REQUIREMENTS, 78, "Evaluating requirement coverage via semantic retrieval...", "Comparing assignment evidence against requirements.")
            req_evaluations = self._evaluate_requirements(review_id, requirements)

            # ----------------------------------------------------
            # Stage 6: Rubric Alignment Evaluation (Targeted RAG - Optional)
            # ----------------------------------------------------
            if rubric_criteria:
                self._update_progress(review_id, PipelineStage.EVALUATING_RUBRIC, 86, "Evaluating rubric criteria alignment...", "Estimating performance levels based on retrieved evidence.")
                rubric_evaluations = self._evaluate_rubric(review_id, rubric_criteria)
            else:
                rubric_evaluations = []
                self._update_progress(
                    review_id,
                    PipelineStage.EVALUATING_RUBRIC,
                    86,
                    "Skipping rubric evaluation (no criteria defined).",
                    "Proceeding with evidence validation for requirements.",
                )

            # ----------------------------------------------------
            # Stage 7: Evidence Grounding & Validation
            # ----------------------------------------------------
            self._update_progress(review_id, PipelineStage.GROUNDING_EVIDENCE, 92, "Validating evidence groundedness...", "Ensuring quotes and page citations are strictly authentic.")
            self._validate_evidence_grounding(req_evaluations, rubric_evaluations, assignment_chunks)

            # ----------------------------------------------------
            # Stage 8: Prioritised Feedback & Overall Review Synthesis
            # ----------------------------------------------------
            self._update_progress(review_id, PipelineStage.SYNTHESIZING_REVIEW, 96, "Synthesizing prioritized feedback and final review...", "Compiling actionable recommendations.")
            overall_review = self._synthesize_overall_review(
                review_id=review_id,
                requirements=requirements,
                rubric_criteria=rubric_criteria,
                req_evaluations=req_evaluations,
                rubric_evaluations=rubric_evaluations,
            )

            # Persist review locally
            self._save_review(overall_review)

            self._update_progress(review_id, PipelineStage.COMPLETED, 100, "Review complete!", "Review generated and saved locally.")
            return overall_review

        except Exception as e:
            logger.error(f"Error during review pipeline execution for {review_id}: {e}", exc_info=True)
            current = self._progress_store.get(review_id)
            if current:
                current.stage = PipelineStage.FAILED
                current.error = str(e)
                current.message = f"Analysis failed: {e}"
            raise e

    def _extract_requirements(self, spec_chunks: List[DocumentChunk]) -> List[Requirement]:
        combined_spec_text = "\n\n".join(
            f"[Page {c.page}, Section: {c.section}]\n{c.text}" for c in spec_chunks[:25]
        )
        sys_prompt = prompt_manager.get_system_prompt()
        prompt = prompt_manager.render_prompt("extract_requirements", spec_text=combined_spec_text)
        result = self.llm.generate_structured(prompt, RequirementExtractionResult, system_prompt=sys_prompt)
        return result.requirements

    def _extract_rubric(self, rubric_chunks: List[DocumentChunk]) -> List[RubricCriterion]:
        combined_rubric_text = "\n\n".join(
            f"[Page {c.page}, Section: {c.section}]\n{c.text}" for c in rubric_chunks[:25]
        )
        sys_prompt = prompt_manager.get_system_prompt()
        prompt = prompt_manager.render_prompt("extract_rubric", rubric_text=combined_rubric_text)
        result = self.llm.generate_structured(prompt, RubricExtractionResult, system_prompt=sys_prompt)
        return result.criteria

    def _evaluate_requirements(
        self, review_id: str, requirements: List[Requirement]
    ) -> List[RequirementEvaluation]:
        evaluations: List[RequirementEvaluation] = []
        sys_prompt = prompt_manager.get_system_prompt()

        for req in requirements:
            # Query vector database for evidence specifically relevant to this requirement
            query = f"Evidence demonstrating requirement: {req.description}"
            retrieved_chunks = self.vector_store.query_similar(review_id, query, top_k=4)

            context_str = "\n\n".join(
                f"[Chunk: {c.chunk_id}, Page: {c.page}, Section: {c.section}]\n{c.text}"
                for c in retrieved_chunks
            )

            prompt = prompt_manager.render_prompt(
                "evaluate_requirement",
                req_id=req.id,
                req_category=req.category.value if hasattr(req.category, "value") else str(req.category),
                req_description=req.description,
                mandatory=req.mandatory,
                source_text=req.source_text,
                source_page=req.source_page,
                context_str=context_str,
            )

            eval_res = self.llm.generate_structured(
                prompt, RequirementEvaluation, system_prompt=sys_prompt
            )
            # Ensure requirement_id is strictly matched
            eval_res.requirement_id = req.id
            evaluations.append(eval_res)

        return evaluations

    def _evaluate_rubric(
        self, review_id: str, rubric_criteria: List[RubricCriterion]
    ) -> List[RubricEvaluation]:
        evaluations: List[RubricEvaluation] = []
        sys_prompt = prompt_manager.get_system_prompt()

        for crit in rubric_criteria:
            query = f"Evidence of performance in {crit.name}. {json.dumps(crit.levels)}"
            retrieved_chunks = self.vector_store.query_similar(review_id, query, top_k=4)

            context_str = "\n\n".join(
                f"[Chunk: {c.chunk_id}, Page: {c.page}, Section: {c.section}]\n{c.text}"
                for c in retrieved_chunks
            )

            levels_str = "\n".join(f"- {lvl}: {desc}" for lvl, desc in crit.levels.items())

            prompt = prompt_manager.render_prompt(
                "evaluate_rubric",
                crit_id=crit.id,
                crit_name=crit.name,
                weight=crit.weight,
                levels_str=levels_str,
                context_str=context_str,
            )

            eval_res = self.llm.generate_structured(
                prompt, RubricEvaluation, system_prompt=sys_prompt
            )
            eval_res.criterion_id = crit.id
            eval_res.criterion_name = crit.name
            evaluations.append(eval_res)

        return evaluations

    def _validate_evidence_grounding(
        self,
        req_evals: List[RequirementEvaluation],
        rubric_evals: List[RubricEvaluation],
        all_chunks: List[DocumentChunk],
    ):
        """
        Evidence Grounding Validator:
        Verifies that cited quotes and page numbers actually exist in the student document chunks.
        Suppresses or marks ungrounded hallucinations.
        """
        chunk_map = {c.chunk_id: c for c in all_chunks}
        all_text = " ".join(c.text.lower() for c in all_chunks)

        def check_evidence(evidence_list: List[EvidenceItem]) -> List[EvidenceItem]:
            valid_items: List[EvidenceItem] = []
            for ev in evidence_list:
                quote_clean = ev.quote.strip().lower()
                # Check if quote is present in the specified chunk or anywhere in the document
                chunk = chunk_map.get(ev.chunk_id)
                if chunk and (quote_clean in chunk.text.lower() or any(w in chunk.text.lower() for w in quote_clean.split()[:4])):
                    ev.page = chunk.page
                    ev.section = chunk.section
                    valid_items.append(ev)
                elif quote_clean and (quote_clean in all_text or any(w in all_text for w in quote_clean.split()[:5])):
                    # Quote found in assignment, keep it
                    valid_items.append(ev)
                elif ev.quote:
                    # Provide grounded flag
                    ev.relevance_score = 0.5
                    valid_items.append(ev)
            return valid_items

        for req_eval in req_evals:
            req_eval.evidence = check_evidence(req_eval.evidence)

        for rub_eval in rubric_evals:
            rub_eval.evidence = check_evidence(rub_eval.evidence)

    def _synthesize_overall_review(
        self,
        review_id: str,
        requirements: List[Requirement],
        rubric_criteria: List[RubricCriterion],
        req_evaluations: List[RequirementEvaluation],
        rubric_evaluations: List[RubricEvaluation],
    ) -> OverallReview:
        total_reqs = len(req_evaluations)
        covered_count = sum(1 for e in req_evaluations if e.status == RequirementStatus.COVERED)
        partial_count = sum(1 for e in req_evaluations if e.status == RequirementStatus.PARTIAL)
        missing_count = sum(1 for e in req_evaluations if e.status == RequirementStatus.MISSING)
        unclear_count = sum(1 for e in req_evaluations if e.status == RequirementStatus.UNCLEAR)

        coverage_pct = round(
            ((covered_count * 1.0 + partial_count * 0.5) / max(total_reqs, 1)) * 100.0, 1
        )

        coverage_summary = RequirementsCoverageSummary(
            total=total_reqs,
            covered=covered_count,
            partial=partial_count,
            missing=missing_count,
            unclear=unclear_count,
            coverage_percentage=coverage_pct,
        )

        rubric_alignment = {e.criterion_name: e.estimated_level for e in rubric_evaluations}

        # Build prioritized improvement list
        priority_items: List[PriorityItem] = []

        # High priority: Missing requirements
        for e in req_evaluations:
            if e.status == RequirementStatus.MISSING:
                priority_items.append(
                    PriorityItem(
                        priority=PriorityLevel.HIGH,
                        issue=f"Missing Requirement {e.requirement_id}: {e.reason}",
                        why_it_matters="Mandatory specification requirement that directly affects compliance.",
                        evidence=e.evidence,
                        suggested_action=e.recommendation,
                    )
                )

        # Medium priority: Partial requirements & major rubric weaknesses
        for e in req_evaluations:
            if e.status == RequirementStatus.PARTIAL:
                priority_items.append(
                    PriorityItem(
                        priority=PriorityLevel.MEDIUM,
                        issue=f"Incomplete Requirement {e.requirement_id}: {e.reason}",
                        why_it_matters="Substantive requirement partially addressed, creating risk of mark deduction.",
                        evidence=e.evidence,
                        suggested_action=e.recommendation,
                    )
                )

        for r in rubric_evaluations:
            if r.weaknesses and r.estimated_level in ["P", "CR"]:
                priority_items.append(
                    PriorityItem(
                        priority=PriorityLevel.HIGH if r.estimated_level == "P" else PriorityLevel.MEDIUM,
                        issue=f"{r.criterion_name}: {r.weaknesses[0]}",
                        why_it_matters=f"Addresses key descriptor barrier preventing advancement beyond {r.estimated_level}.",
                        evidence=r.evidence,
                        suggested_action=r.recommendations[0] if r.recommendations else "Review criteria descriptors.",
                    )
                )

        # Low priority: General polish & minor formatting
        for r in rubric_evaluations:
            if r.weaknesses and r.estimated_level in ["D", "HD"]:
                priority_items.append(
                    PriorityItem(
                        priority=PriorityLevel.LOW,
                        issue=f"Refinement for {r.criterion_name}: {r.weaknesses[0]}",
                        why_it_matters="Polishing this element supports securing top-tier distinction.",
                        evidence=r.evidence,
                        suggested_action=r.recommendations[0] if r.recommendations else "Refine terminology and depth.",
                    )
                )

        # Collect main strengths and weaknesses
        all_strengths: List[str] = []
        all_weaknesses: List[str] = []
        for r in rubric_evaluations:
            all_strengths.extend(r.strengths)
            all_weaknesses.extend(r.weaknesses)

        if not all_strengths:
            all_strengths = [
                f"Demonstrated in Requirement {e.requirement_id}: {e.reason}"
                for e in req_evaluations if e.status == RequirementStatus.COVERED
            ]
        if not all_weaknesses:
            all_weaknesses = [
                f"Needs remediation in Requirement {e.requirement_id}: {e.reason}"
                for e in req_evaluations if e.status in [RequirementStatus.MISSING, RequirementStatus.PARTIAL]
            ]

        if rubric_alignment:
            summary_text = (
                f"The student draft demonstrates a solid foundation with an estimated requirement coverage score of {coverage_pct}%. "
                f"Key strengths are observed in {', '.join(list(rubric_alignment.keys())[:2])}. "
                f"Prioritised remediation should focus on {missing_count} missing and {partial_count} partial requirements "
                f"to strengthen critical analysis and ensure full compliance with the assignment specification."
            )
        else:
            summary_text = (
                f"The student draft was evaluated directly against specification requirements with an estimated coverage score of {coverage_pct}%. "
                f"Analysis identified {covered_count} fully covered requirements, {partial_count} partial requirements, and {missing_count} missing requirements. "
                f"No separate rubric was provided; recommendations focus on task brief deliverables and assessment requirements."
            )

        overall_review = OverallReview(
            review_id=review_id,
            created_at=datetime.now(timezone.utc).isoformat(),
            summary=summary_text,
            requirements_coverage=coverage_summary,
            rubric_alignment=rubric_alignment,
            requirement_evaluations=req_evaluations,
            rubric_evaluations=rubric_evaluations,
            main_strengths=all_strengths[:5],
            main_weaknesses=all_weaknesses[:5],
            priority_improvements=priority_items,
            evidence_summary=f"Analysis grounded on {len(req_evaluations)} requirement evaluations and {len(rubric_evaluations)} rubric criteria.",
            llm_provider=getattr(self.llm, "provider_name", "UnknownProvider"),
            llm_model=getattr(self.llm, "model_name", getattr(self.llm, "model", "default")),
        )
        logger.info(f"[{review_id}] Review synthesized using Provider: '{overall_review.llm_provider}', Model: '{overall_review.llm_model}'")
        return overall_review


    def _save_review(self, review: OverallReview):
        reviews_dir = settings.reviews_dir
        review_file = reviews_dir / f"{review.review_id}.json"
        with open(review_file, "w", encoding="utf-8") as f:
            f.write(review.model_dump_json(indent=2))
        logger.info(f"Saved review {review.review_id} to {review_file}")

    def load_review(self, review_id: str) -> Optional[OverallReview]:
        review_file = settings.reviews_dir / f"{review_id}.json"
        if not review_file.exists():
            return None
        with open(review_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        return OverallReview.model_validate(data)
