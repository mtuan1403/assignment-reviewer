from typing import Type, TypeVar, Optional, List
import re
from pydantic import BaseModel

from backend.app.core.logging import get_logger
from backend.app.services.llm.base import BaseLLMProvider
from backend.app.models.domain import (
    RequirementCategory,
    RequirementStatus,
    PriorityLevel,
)
from backend.app.models.schemas import (
    Requirement,
    RequirementExtractionResult,
    RubricCriterion,
    RubricExtractionResult,
    RequirementEvaluation,
    RubricEvaluation,
    EvidenceItem,
    PriorityItem,
    OverallReview,
    RequirementsCoverageSummary,
)

logger = get_logger(__name__)
T = TypeVar("T", bound=BaseModel)


class MockProvider(BaseLLMProvider):
    """
    Deterministic, fully offline LLM provider.
    Inspects incoming document text and generates grounded, realistic responses
    for COMP8240 / VADER and general portfolio evaluations.
    """

    def generate_text(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        return "Mock evaluation response."

    def generate_structured(
        self,
        prompt: str,
        response_model: Type[T],
        system_prompt: Optional[str] = None,
    ) -> T:
        name = response_model.__name__

        if name == "RequirementExtractionResult":
            return self._mock_extract_requirements(prompt)
        elif name == "RubricExtractionResult":
            return self._mock_extract_rubric(prompt)
        elif name == "RequirementEvaluation":
            return self._mock_evaluate_requirement(prompt)
        elif name == "RubricEvaluation":
            return self._mock_evaluate_rubric(prompt)
        elif name == "OverallReview":
            return self._mock_synthesize_review(prompt)
        else:
            return response_model.model_validate({})

    def _mock_extract_requirements(self, prompt: str) -> RequirementExtractionResult:
        is_comp8240 = "comp8240" in prompt.lower() or "vader" in prompt.lower() or "acl" in prompt.lower() or "overleaf" in prompt.lower()

        if is_comp8240:
            requirements = [
                Requirement(
                    id="R1",
                    description="Describe what the paper is about and what it aims to achieve for a general computer science audience, explaining core concepts with examples.",
                    category=RequirementCategory.EXPLICIT,
                    mandatory=True,
                    source_text="You should describe what the paper is about and what it aims to achieve. This description should be aimed at a general computer science reader.",
                    source_page=2,
                ),
                Requirement(
                    id="R2",
                    description="Explain evaluation methodology and metrics with references and a worked example, describe original datasets, and outline an LLM-as-a-judge evaluation.",
                    category=RequirementCategory.ASSESSMENT,
                    mandatory=True,
                    source_text="You will need to explain these [methodologies and metrics]; this explanation should include a worked example. As part of this, you should also describe the datasets used in the paper... introducing a new kind of evaluation, using an LLM as a judge.",
                    source_page=3,
                ),
                Requirement(
                    id="R3",
                    description="Justify choice of paper by indicators of quality (venue, citations, adoption), verify code accessibility, and execute the software noting successful run.",
                    category=RequirementCategory.EXPLICIT,
                    mandatory=True,
                    source_text="In addition to justifying the choice of work by some indicator of quality, you'll also need to convince us of the feasibility of the project... you should at least download and execute the relevant software, and note that you have done this successfully.",
                    source_page=3,
                ),
                Requirement(
                    id="R4",
                    description="Describe new data for the method: discuss several (e.g., five) existing candidate datasets assessing feasibility, and outline newly constructed data.",
                    category=RequirementCategory.DELIVERABLE,
                    mandatory=True,
                    source_text="There should be two types of new data: 1. Existing datasets that the method hasn't yet been applied to. You should discuss several (e.g., five) possibilities... 2. New datasets that you create.",
                    source_page=3,
                ),
                Requirement(
                    id="R5",
                    description="Follow formatting requirements: use ACL LaTeX template, compile to PDF, typical length 5-6 pages, and reference using ACL style.",
                    category=RequirementCategory.FORMATTING,
                    mandatory=False,
                    source_text="Length: A typical length would be 5-6 pages. Material: You will be expected to produce your report using latex... Style: You should use the ACL template available in Overleaf.",
                    source_page=1,
                ),
            ]
            return RequirementExtractionResult(requirements=requirements)

        # Default fallback (CS-504)
        requirements = [
            Requirement(
                id="R1",
                description="Formulate an enterprise cloud migration strategy evaluating at least two architectural options.",
                category=RequirementCategory.EXPLICIT,
                mandatory=True,
                source_text="Students must evaluate at least two architectural migration strategies for the enterprise workload.",
                source_page=1,
            ),
            Requirement(
                id="R2",
                description="Conduct a comprehensive comparative trade-off analysis of cost, latency, and reliability.",
                category=RequirementCategory.ASSESSMENT,
                mandatory=True,
                source_text="Include a comparative trade-off matrix analyzing capital expenditure, latency constraints, and fault tolerance.",
                source_page=2,
            ),
            Requirement(
                id="R3",
                description="Incorporate an Ethical AI and data governance framework addressing privacy and model bias.",
                category=RequirementCategory.EXPLICIT,
                mandatory=True,
                source_text="The proposal must establish clear ethical data governance principles, addressing data sovereignty, model bias, and user privacy.",
                source_page=2,
            ),
            Requirement(
                id="R4",
                description="Deliver a phased 12-month migration roadmap with clear risk mitigation milestones.",
                category=RequirementCategory.DELIVERABLE,
                mandatory=True,
                source_text="Provide a realistic 12-month implementation timeline with staged risk mitigations.",
                source_page=3,
            ),
            Requirement(
                id="R5",
                description="Format document in IEEE style within 2,500 words (+/- 10%) with peer-reviewed references.",
                category=RequirementCategory.FORMATTING,
                mandatory=False,
                source_text="The submission should follow IEEE double-column format and be between 2,250 and 2,750 words.",
                source_page=3,
            ),
        ]
        return RequirementExtractionResult(requirements=requirements)

    def _mock_extract_rubric(self, prompt: str) -> RubricExtractionResult:
        is_comp8240 = "comp8240" in prompt.lower() or "chosen paper" in prompt.lower() or "quality of description" in prompt.lower()

        if is_comp8240:
            criteria = [
                RubricCriterion(
                    id="C1",
                    name="Quality of description of chosen paper",
                    weight=20.0,
                    levels={
                        "HD": "Report very clearly describes purpose and relevant details of chosen paper with no significant errors.",
                        "D": "Report does a good job of describing purpose and relevant details of chosen paper, possibly with an error or two.",
                        "CR": "Report is mostly accurate in describing purpose and relevant details of chosen paper.",
                        "P": "Report conveys the general gist of the chosen paper.",
                        "Fail": "Report does not successfully convey even the general gist of the chosen paper.",
                    },
                    source_page=5,
                ),
                RubricCriterion(
                    id="C2",
                    name="Justification of chosen paper",
                    weight=20.0,
                    levels={
                        "HD": "Chosen paper is justified by several criteria, well explained.",
                        "D": "Chosen paper is justified by several criteria, moderately well explained.",
                        "CR": "Chosen paper is justified by more than one criterion, with some explanation.",
                        "P": "Chosen paper is justified in some (relevant) way.",
                        "Fail": "Chosen paper has little or no justification.",
                    },
                    source_page=5,
                ),
                RubricCriterion(
                    id="C3",
                    name="Quality of explanation of evaluation aspects of chosen paper, including datasets used in that paper",
                    weight=20.0,
                    levels={
                        "HD": "Report explains all of the most important evaluation aspects of the chosen paper clearly, and describes all of the datasets used.",
                        "D": "Report explains most of the most important evaluation aspects of the chosen paper clearly, and describes most of the datasets used.",
                        "CR": "Report explains some evaluation aspects of the chosen paper with some degree of clarity, and gives a reasonable description of the datasets used.",
                        "P": "Report gives an overall sense of the evaluation and datasets of the chosen paper.",
                        "Fail": "Report misses much of the explanation of evaluation and datasets used.",
                    },
                    source_page=5,
                ),
                RubricCriterion(
                    id="C4",
                    name="Quality of description of new data",
                    weight=20.0,
                    levels={
                        "HD": "Report explains very clearly and in some detail the specific new existing datasets to be used as well as the idea for newly constructed data.",
                        "D": "Report explains the specific new existing datasets to be used, in less detail than expected for the HD level, as well as the idea for newly constructed data.",
                        "CR": "Report gives some idea for specific new existing datasets to be used as well as the idea for newly constructed data.",
                        "P": "Report makes some suggestions for new existing datasets to be used, with less specificity than at the Cr level, as well as the idea for newly constructed data.",
                        "Fail": "Report is missing most or all details on new datasets.",
                    },
                    source_page=5,
                ),
                RubricCriterion(
                    id="C5",
                    name="Quality of presentation",
                    weight=20.0,
                    levels={
                        "HD": "Writing style is excellent and clearly conveys the required content, and the report conforms to the specified format.",
                        "D": "Writing style is very good and mostly conveys the required content, and the report mostly conforms to the specified format.",
                        "CR": "Writing style is decent and satisfactorily conveys the required content, and the report generally conforms to the specified format.",
                        "P": "Writing style is satisfactory and goes some way to conveying the required content, and the report makes a reasonable attempt to conform to the specified format.",
                        "Fail": "Writing style is unclear and/or the report fails to conform to the specified format in major ways.",
                    },
                    source_page=5,
                ),
            ]
            return RubricExtractionResult(criteria=criteria)

        # Default fallback
        criteria = [
            RubricCriterion(
                id="C1",
                name="Architectural & Technical Analysis",
                weight=30.0,
                levels={
                    "HD": "Exemplary, highly rigorous comparative analysis of migration patterns with in-depth quantitative metrics.",
                    "D": "Strong technical analysis evaluating multiple options with clear rationale and minor gaps in quantitative modeling.",
                    "CR": "Competent overview of cloud architectures but limited depth in evaluating trade-offs.",
                    "P": "Superficial description of technologies without substantive architectural justification.",
                },
                source_page=1,
            ),
            RubricCriterion(
                id="C2",
                name="Ethical AI & Data Governance",
                weight=25.0,
                levels={
                    "HD": "Thorough integration of international ethical AI standards, proactive bias auditing, and sovereign data controls.",
                    "D": "Sound ethical analysis identifying key compliance requirements with actionable mitigation strategies.",
                    "CR": "General awareness of data privacy and ethical principles without detailed implementation safeguards.",
                    "P": "Rudimentary mention of privacy regulations with negligible ethical analysis.",
                },
                source_page=2,
            ),
            RubricCriterion(
                id="C3",
                name="Strategic Implementation & Risk Mitigation",
                weight=25.0,
                levels={
                    "HD": "Sophisticated, realistic phased roadmap with proactive rollback triggers and comprehensive risk governance.",
                    "D": "Clear, practical implementation timeline with well-identified risk categories.",
                    "CR": "Basic project timeline with generic risks and conventional mitigations.",
                    "P": "Unrealistic or vague timeline lacking concrete milestone definitions.",
                },
                source_page=2,
            ),
            RubricCriterion(
                id="C4",
                name="Academic Rigour & Professional Communication",
                weight=20.0,
                levels={
                    "HD": "Impeccable academic prose, coherent synthesis, and flawless citation of authoritative sources.",
                    "D": "Well-structured, professional report with consistent academic referencing and minor formatting flaws.",
                    "CR": "Readable report with adequate referencing but inconsistent terminology or flow.",
                    "P": "Disorganized structure, informal tone, or frequent citation inaccuracies.",
                },
                source_page=3,
            ),
        ]
        return RubricExtractionResult(criteria=criteria)

    def _mock_evaluate_requirement(self, prompt: str) -> RequirementEvaluation:
        req_id_match = re.search(r"\b(R\d+)\b", prompt)
        req_id = req_id_match.group(1) if req_id_match else "R1"

        # Extract chunks from prompt
        chunks_in_prompt = re.findall(
            r"\[Chunk:\s*([\w_]+),\s*Page:\s*(\d+),\s*Section:\s*([^\]]+)\]\s*\n(.*?)(?=\n\[Chunk:|\Z)",
            prompt,
            re.DOTALL,
        )

        evidence_items: List[EvidenceItem] = []
        for c_id, page, section, text in chunks_in_prompt[:2]:
            clean_text = text.strip()
            first_sentence = clean_text.split(". ")[0] if clean_text else "Student draft excerpt"
            evidence_items.append(
                EvidenceItem(
                    page=int(page),
                    section=section.strip(),
                    chunk_id=c_id.strip(),
                    quote=first_sentence[:130],
                    relevance_score=0.95,
                )
            )

        is_comp8240_spec = "comp8240" in prompt.lower() or "chosen paper" in prompt.lower()
        
        # Check student chunks in prompt to see if student actually submitted a VADER paper proposal
        # (rather than an unrelated document like an internship guide, resume, or syllabus)
        student_text_in_prompt = " ".join(t.lower() for _, _, _, t in chunks_in_prompt)
        has_vader_content = any(k in student_text_in_prompt for k in ["vader", "sentiment", "lexical", "heuristics", "pang", "gold standard", "icwsm"])

        if is_comp8240_spec and not has_vader_content:

            # Student submitted an unrelated document against the COMP8240 spec!
            return RequirementEvaluation(
                requirement_id=req_id,
                status=RequirementStatus.MISSING,
                confidence=0.95,
                reason=f"The uploaded student document does not contain evidence addressing Requirement {req_id}. The content appears to be unrelated to the paper proposal task.",
                evidence=evidence_items[:1] if evidence_items else [],
                recommendation="Ensure you upload your actual draft assignment that corresponds to this specification.",
            )

        if is_comp8240_spec and has_vader_content:
            if req_id == "R1":
                return RequirementEvaluation(
                    requirement_id="R1",
                    status=RequirementStatus.COVERED,
                    confidence=0.96,
                    reason="The student provides an exemplary description of the VADER paper for a general CS reader, defining sentiment analysis via Pang and Lee (2008), detailing VADER's 7,500 lexical features and five linguistic heuristics, and providing concrete grounded examples (e.g., 'AMAZING', 'not good', 'good, but boring').",
                    evidence=evidence_items,
                    recommendation="The description is exceptionally thorough and clear; ensure consistency in referencing between in-text citations and the bibliography.",
                )

            elif req_id == "R2":
                return RequirementEvaluation(
                    requirement_id="R2",
                    status=RequirementStatus.COVERED,
                    confidence=0.96,
                    reason="Comprehensive explanation of evaluation aspects: details the human-annotated gold standard quality control, Pearson correlation with positive affine invariance explanation, classification metrics with mathematical formulas, an explicit worked example on the NYT corpus (F1 ≈ 0.57), descriptions of all 4 original datasets, and an LLM-as-a-judge proposal.",
                    evidence=evidence_items,
                    recommendation="The worked example and mathematical rigor are outstanding. In future work, specify which specific LLM model (e.g. GPT-4o, Claude 3.5 Sonnet) will serve as the judge.",
                )
            elif req_id == "R3":
                return RequirementEvaluation(
                    requirement_id="R3",
                    status=RequirementStatus.COVERED,
                    confidence=0.97,
                    reason="The justification is substantiated across multiple dimensions: CORE A conference ranking for ICWSM, 10,100 Google Scholar citations, 5.1k GitHub stars, PyPI package availability, and NLTK integration. Crucially, the student installed and verified vaderSentiment v3.3.2 on Python 3.13.9 with test code and terminal output figures.",
                    evidence=evidence_items,
                    recommendation="Verification of software execution with code and terminal screenshots directly fulfills the feasibility requirement.",
                )
            elif req_id == "R4":
                return RequirementEvaluation(
                    requirement_id="R4",
                    status=RequirementStatus.COVERED,
                    confidence=0.96,
                    reason="The proposal details exactly five existing candidate datasets (EmoBank, SST, CMU-MOSEI, FiQA 2018, SemEval-2007 Task 14) with critical appraisal of domain characteristics and VADER compatibility. Furthermore, it outlines newly constructed social media data (TikTok, Reddit, X) with ethical compliance (PRAW, public data only) and an 18-25 annotator protocol.",
                    evidence=evidence_items,
                    recommendation="The critique of why CMU-MOSEI lacks punctuation and FiQA has aspect-level mismatch demonstrates critical evaluation. Ensure the final human annotation study obtains formal ethics approval if required.",
                )
            else: # R5
                return RequirementEvaluation(
                    requirement_id="R5",
                    status=RequirementStatus.PARTIAL,
                    confidence=0.88,
                    reason="The report is expertly written in two-column ACL LaTeX style with flawless scholarly citations. However, the proposal spans 8 pages (including references and figures), exceeding the typical length specified in the unit guide: 'A typical length would be 5-6 pages.'",
                    evidence=evidence_items,
                    recommendation="Consider condensing introductory explanations or placing software execution screenshots in an appendix/compact format to bring the core paper closer to the recommended 5-6 page guideline.",
                )

        # Default fallback
        if req_id == "R1":
            return RequirementEvaluation(
                requirement_id="R1",
                status=RequirementStatus.COVERED,
                confidence=0.92,
                reason="The student provides an in-depth evaluation comparing containerized Kubernetes deployment versus serverless architecture for the core services.",
                evidence=evidence_items,
                recommendation="Maintain the detailed comparison; consider providing an explicit benchmark table of expected latency under peak load.",
            )
        elif req_id == "R2":
            return RequirementEvaluation(
                requirement_id="R2",
                status=RequirementStatus.PARTIAL,
                confidence=0.86,
                reason="While both architectural options are described, the draft does not present an explicit side-by-side trade-off matrix or quantify cost differentials.",
                evidence=evidence_items,
                recommendation="Synthesize the comparative narrative into a formal comparative matrix detailing OpEx vs CapEx, fault tolerance, and cold-start latency.",
            )
        elif req_id == "R3":
            return RequirementEvaluation(
                requirement_id="R3",
                status=RequirementStatus.COVERED,
                confidence=0.89,
                reason="The submission includes a dedicated section on ethical governance addressing data sovereignty, GDPR compliance, and bias mitigation in automated scoring.",
                evidence=evidence_items,
                recommendation="Expand on continuous model monitoring mechanisms post-deployment to ensure fairness across demographic subgroups.",
            )
        elif req_id == "R4":
            return RequirementEvaluation(
                requirement_id="R4",
                status=RequirementStatus.PARTIAL,
                confidence=0.81,
                reason="A 4-phase rollout is proposed, but the timeline spans 8 months rather than the required 12-month operational stabilization and decommissioning phase.",
                evidence=evidence_items,
                recommendation="Extend the implementation roadmap to include legacy system decommissioning and long-term disaster recovery rehearsals across months 9 to 12.",
            )
        else:
            return RequirementEvaluation(
                requirement_id=req_id,
                status=RequirementStatus.COVERED,
                confidence=0.88,
                reason="The document adheres to formatting guidelines and proper academic structure.",
                evidence=evidence_items,
                recommendation="Verify all IEEE in-text citations correspond to active peer-reviewed sources.",
            )

    def _mock_evaluate_rubric(self, prompt: str) -> RubricEvaluation:
        crit_id_match = re.search(r"\b(C\d+)\b", prompt)
        crit_id = crit_id_match.group(1) if crit_id_match else "C1"

        is_comp8240 = "comp8240" in prompt.lower() or "chosen paper" in prompt.lower() or "vader" in prompt.lower() or "quality of description" in prompt.lower()

        chunks_in_prompt = re.findall(
            r"\[Chunk:\s*([\w_]+),\s*Page:\s*(\d+),\s*Section:\s*([^\]]+)\]\s*\n(.*?)(?=\n\[Chunk:|\Z)",
            prompt,
            re.DOTALL,
        )

        evidence_items: List[EvidenceItem] = []
        for c_id, page, section, text in chunks_in_prompt[:2]:
            clean_text = text.strip()
            first_sentence = clean_text.split(". ")[0] if clean_text else "Student draft excerpt"
            evidence_items.append(
                EvidenceItem(
                    page=int(page),
                    section=section.strip(),
                    chunk_id=c_id.strip(),
                    quote=first_sentence[:130],
                    relevance_score=0.94,
                )
            )

        is_comp8240 = "comp8240" in prompt.lower() or "chosen paper" in prompt.lower() or "vader" in prompt.lower() or "quality of description" in prompt.lower()

        student_text_in_prompt = " ".join(t.lower() for _, _, _, t in chunks_in_prompt)
        has_vader_content = any(k in student_text_in_prompt for k in ["vader", "sentiment", "lexical", "heuristics", "pang", "gold standard", "icwsm"])

        if is_comp8240 and not has_vader_content:
            return RubricEvaluation(
                criterion_id=crit_id,
                criterion_name=crit_id,
                estimated_level="Fail",
                confidence=0.95,
                strengths=[],
                weaknesses=[
                    "The submitted document contains no observable evidence addressing the required paper evaluation.",
                    "Content is completely unrelated to the assessment specification."
                ],
                evidence=evidence_items[:1] if evidence_items else [],
                recommendations=[
                    "Submit the correct assignment draft corresponding to this rubric."
                ],
            )

        if is_comp8240:
            if crit_id == "C1":

                return RubricEvaluation(
                    criterion_id="C1",
                    criterion_name="Quality of description of chosen paper",
                    estimated_level="HD",
                    confidence=0.95,
                    strengths=[
                        "Lucid, accessible explanation of sentiment analysis principles aimed at a general computer science audience.",
                        "Comprehensive analysis of VADER's rule-based heuristics and empirical development methodology.",
                        "Detailed comparative analysis of VADER's performance across four distinct text domains.",
                    ],
                    weaknesses=[
                        "None of significance. The conceptual foundation and linguistic mechanisms are described with exceptional clarity.",
                    ],
                    evidence=evidence_items,
                    recommendations=[
                        "Maintain this high level of clarity into the final project report.",
                    ],
                )
            elif crit_id == "C2":
                return RubricEvaluation(
                    criterion_id="C2",
                    criterion_name="Justification of chosen paper",
                    estimated_level="HD",
                    confidence=0.96,
                    strengths=[
                        "Multi-faceted justification covering venue prestige (ICWSM CORE A rank), academic citations (10.1k Google Scholar), and industry adoption (5.1k GitHub stars).",
                        "Practical demonstration of software availability through PyPI and NLTK.",
                        "Direct verification of code execution with Python 3.13 on macOS, verified heuristics, and terminal screenshots.",
                    ],
                    weaknesses=[
                        "None. The justification convincingly establishes both academic merit and practical project feasibility.",
                    ],
                    evidence=evidence_items,
                    recommendations=[
                        "Ensure the specific hardware/compute requirements for reproducing the full experimental pipeline are outlined in the next milestone.",
                    ],
                )
            elif crit_id == "C3":
                return RubricEvaluation(
                    criterion_id="C3",
                    criterion_name="Quality of explanation of evaluation aspects of chosen paper, including datasets used in that paper",
                    estimated_level="HD",
                    confidence=0.95,
                    strengths=[
                        "Rigorous mathematical explanations of Pearson correlation, precision, recall, and harmonic F1 score.",
                        "Includes an explicit, step-by-step worked example on the NYT opinion editorial corpus (F1 ≈ 0.57).",
                        "Exhaustive coverage of all four original evaluation datasets (Twitter, Movie Reviews, Product Reviews, NYT).",
                        "Thoughtful introduction of the LLM-as-a-judge evaluation methodology.",
                    ],
                    weaknesses=[
                        "Prompt design and prompt engineering details for the LLM judge are left broad (noted as acceptable at this proposal stage in the spec).",
                    ],
                    evidence=evidence_items,
                    recommendations=[
                        "As the project progresses into Week 7, specify the exact system prompt, evaluation rubric, and temperature parameters for the LLM judge.",
                    ],
                )
            elif crit_id == "C4":
                return RubricEvaluation(
                    criterion_id="C4",
                    criterion_name="Quality of description of new data",
                    estimated_level="HD",
                    confidence=0.94,
                    strengths=[
                        "Exemplary analysis of five distinct existing datasets (EmoBank, SST, CMU-MOSEI, FiQA, SemEval-2007).",
                        "Critical insight into domain limitations (e.g. speech transcripts lacking punctuation, aspect vs sentence sentiment).",
                        "Well-planned contemporary social media dataset targeting Gen Z slang on TikTok, Reddit, and X.",
                        "Explicit commitment to ethical compliance (PRAW, public data only, no private/deleted content) and formal annotation protocol.",
                    ],
                    weaknesses=[
                        "Inter-annotator agreement metrics (e.g. Cohen's Kappa or Krippendorff's alpha) could be explicitly mentioned for the 18-25 annotators.",
                    ],
                    evidence=evidence_items,
                    recommendations=[
                        "Plan to compute and report inter-rater reliability (such as Cohen's Kappa or Pearson r) between the human annotators.",
                    ],
                )
            else: # C5
                return RubricEvaluation(
                    criterion_id="C5",
                    criterion_name="Quality of presentation",
                    estimated_level="D",
                    confidence=0.88,
                    strengths=[
                        "Excellent, scholarly writing style adhering strictly to academic prose standards.",
                        "Professional ACL two-column LaTeX typesetting with clear sectioning and high readability.",
                        "Comprehensive and properly formatted ACL bibliography with full citation metadata.",
                        "Transparent and ethical disclosure of GenAI tool assistance in the Acknowledgments.",
                    ],
                    weaknesses=[
                        "At 8 pages total, the proposal exceeds the unit specification's typical length of 5-6 pages.",
                    ],
                    evidence=evidence_items,
                    recommendations=[
                        "Review whether figures or dataset descriptions can be slightly condensed to align more closely with the typical 5-6 page guideline.",
                    ],
                )

        # Default fallback
        if crit_id == "C1":
            return RubricEvaluation(
                criterion_id="C1",
                criterion_name="Architectural & Technical Analysis",
                estimated_level="D",
                confidence=0.85,
                strengths=[
                    "Clear architectural diagrams and sound comparative framework.",
                    "Solid understanding of multi-region redundancy and database replication.",
                ],
                weaknesses=[
                    "Cost analysis is largely qualitative without an itemized monthly breakdown.",
                    "Does not fully evaluate edge networking caching trade-offs.",
                ],
                evidence=evidence_items,
                recommendations=[
                    "Include a cost model using AWS/GCP pricing calculators to substantiate ROI claims.",
                ],
            )
        elif crit_id == "C2":
            return RubricEvaluation(
                criterion_id="C2",
                criterion_name="Ethical AI & Data Governance",
                estimated_level="HD",
                confidence=0.88,
                strengths=[
                    "Exceptional treatment of data sovereignty and cross-border transfer laws.",
                    "Proactive bias testing framework proposed for fine-tuned models.",
                ],
                weaknesses=[
                    "Incident response plan for ethical violations could be more specific.",
                ],
                evidence=evidence_items,
                recommendations=[
                    "Specify escalation protocols when automated bias detectors flag threshold breaches.",
                ],
            )
        elif crit_id == "C3":
            return RubricEvaluation(
                criterion_id="C3",
                criterion_name="Strategic Implementation & Risk Mitigation",
                estimated_level="CR",
                confidence=0.82,
                strengths=[
                    "Realistic staging of workload migrations into waves.",
                    "Identifies critical staff reskilling requirements.",
                ],
                weaknesses=[
                    "Risk mitigation strategies are reactive rather than preventive.",
                    "Contingency plan in case of cutover failure lacks rollback steps.",
                ],
                evidence=evidence_items,
                recommendations=[
                    "Detail automated rollback triggers during cutover windows to mitigate downtime.",
                ],
            )
        else:
            return RubricEvaluation(
                criterion_id="C4",
                criterion_name="Academic Rigour & Professional Communication",
                estimated_level="D",
                confidence=0.90,
                strengths=[
                    "Professional layout with crisp, informative subheadings.",
                    "Consistent use of IEEE citations.",
                ],
                weaknesses=[
                    "Minor grammatical colloquialisms in Section 3.",
                ],
                evidence=evidence_items,
                recommendations=[
                    "Proofread Section 3 to replace conversational phrases with formal academic phrasing.",
                ],
            )

    def _mock_synthesize_review(self, prompt: str) -> OverallReview:
        return OverallReview(
            review_id="mock_review_01",
            created_at="2026-09-22T12:00:00Z",
            summary="Exceptional project proposal demonstrating high scholarly rigor, comprehensive evaluation design, and practical reproducibility verification.",
            requirements_coverage=RequirementsCoverageSummary(
                total=5, covered=4, partial=1, missing=0, unclear=0, coverage_percentage=90.0
            ),
            rubric_alignment={
                "Quality of description of chosen paper": "HD",
                "Justification of chosen paper": "HD",
                "Quality of explanation of evaluation aspects of chosen paper, including datasets used in that paper": "HD",
                "Quality of description of new data": "HD",
                "Quality of presentation": "D",
            },
            requirement_evaluations=[],
            rubric_evaluations=[],
            main_strengths=[
                "Exceptional depth and clarity in explaining VADER's rule-based mechanisms with grounded linguistic examples.",
                "Rigorous mathematical explanations of evaluation metrics accompanied by an authentic worked example on the NYT corpus.",
                "Convincing multi-criteria justification and direct experimental verification of code execution on Python 3.13.",
                "Critical appraisal of five existing datasets and well-designed ethical protocol for contemporary Gen Z social media data.",
            ],
            main_weaknesses=[
                "Document length is 8 pages, exceeding the recommended typical length of 5-6 pages.",
                "Inter-rater reliability metrics (e.g. Cohen's Kappa) should be formally specified for the newly proposed human annotations.",
            ],
            priority_improvements=[
                PriorityItem(
                    priority=PriorityLevel.MEDIUM,
                    issue="Page length exceeds typical specification (8 pages vs typical 5-6 pages)",
                    why_it_matters="While the extra depth provides comprehensive detail, exceeding recommended length guidelines may be flagged by some markers.",
                    evidence=[],
                    suggested_action="Consider tightening paragraphs in Section 1 or placing software execution figures in a more compact format.",
                ),
                PriorityItem(
                    priority=PriorityLevel.LOW,
                    issue="Specify inter-rater reliability protocol for new human annotation study",
                    why_it_matters="Ensures reproducibility and statistical validity when comparing Gen Z human raters with VADER scores.",
                    evidence=[],
                    suggested_action="Mention the use of Cohen's Kappa or Pearson correlation to measure agreement between the two independent raters.",
                ),
            ],
            evidence_summary="Analysis grounded across 8 pages of student draft text and 5 pages of unit specification and rubric.",
        )
