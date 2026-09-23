export type RequirementCategory =
  | 'explicit'
  | 'optional_suggestion'
  | 'formatting'
  | 'assessment'
  | 'deliverable'

export type RequirementStatus = 'COVERED' | 'PARTIAL' | 'MISSING' | 'UNCLEAR'

export type PriorityLevel = 'HIGH' | 'MEDIUM' | 'LOW'

export type PipelineStage =
  | 'idle'
  | 'uploading'
  | 'parsing'
  | 'extracting_requirements'
  | 'extracting_rubric'
  | 'chunking_assignment'
  | 'indexing_vectors'
  | 'evaluating_requirements'
  | 'evaluating_rubric'
  | 'grounding_evidence'
  | 'synthesizing_review'
  | 'completed'
  | 'failed'

export interface EvidenceItem {
  page: number
  section: string
  chunk_id: string
  quote: string
  relevance_score: number
}

export interface Requirement {
  id: string
  description: string
  category: RequirementCategory
  mandatory: boolean
  source_text: string
  source_page: number
}

export interface RubricCriterion {
  id: string
  name: string
  weight?: number
  levels: Record<string, string>
  source_page: number
}

export interface RequirementEvaluation {
  requirement_id: string
  status: RequirementStatus
  confidence: number
  reason: string
  evidence: EvidenceItem[]
  recommendation: string
}

export interface RubricEvaluation {
  criterion_id: string
  criterion_name: string
  estimated_level: string
  confidence: number
  strengths: string[]
  weaknesses: string[]
  evidence: EvidenceItem[]
  recommendations: string[]
}

export interface PriorityItem {
  priority: PriorityLevel
  issue: string
  why_it_matters: string
  evidence: EvidenceItem[]
  suggested_action: string
}

export interface RequirementsCoverageSummary {
  total: number
  covered: number
  partial: number
  missing: number
  unclear: number
  coverage_percentage: number
}

export interface OverallReview {
  review_id: string
  created_at: string
  summary: string
  requirements_coverage: RequirementsCoverageSummary
  rubric_alignment: Record<string, string>
  requirement_evaluations: RequirementEvaluation[]
  rubric_evaluations: RubricEvaluation[]
  main_strengths: string[]
  main_weaknesses: string[]
  priority_improvements: PriorityItem[]
  evidence_summary: string
  llm_provider?: string
  llm_model?: string
  limitations_disclaimer: string
}

export interface ProgressStatus {
  review_id: string
  stage: PipelineStage
  percent: number
  message: string
  logs: string[]
  error?: string
}

export interface DocumentChunk {
  chunk_id: string
  document_type: string
  page: number
  section: string
  text: string
  token_count: number
}
