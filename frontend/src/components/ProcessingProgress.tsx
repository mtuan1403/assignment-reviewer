import React, { useEffect, useRef, useState } from 'react'
import { Terminal, Compass } from 'lucide-react'
import type { ProgressStatus, PipelineStage } from '../types'

interface ProcessingProgressProps {
  progress: ProgressStatus
  onOpenHowItWorks?: () => void
}

interface StageStep {
  id: string
  number: string
  label: string
  description: string
  associatedStages: PipelineStage[]
}

const STAGES: StageStep[] = [
  {
    id: 'upload',
    number: '01',
    label: 'Document Ingestion & Parsing',
    description: 'PyMuPDF parses PDF heading hierarchy, bold font scales, and layout trees into structured page streams.',
    associatedStages: ['uploading', 'parsing', 'extracting_requirements', 'extracting_rubric', 'chunking_assignment', 'indexing_vectors', 'evaluating_requirements', 'evaluating_rubric', 'grounding_evidence', 'synthesizing_review', 'completed'],
  },
  {
    id: 'extract_reqs',
    number: '02',
    label: 'Requirement Extraction',
    description: 'Deconstructs assignment brief into strict schema items (mandatory deliverables, word counts, formatting, comparisons).',
    associatedStages: ['extracting_requirements', 'extracting_rubric', 'chunking_assignment', 'indexing_vectors', 'evaluating_requirements', 'evaluating_rubric', 'grounding_evidence', 'synthesizing_review', 'completed'],
  },
  {
    id: 'extract_rubric',
    number: '03',
    label: 'Rubric Criteria Structuring',
    description: 'Parses criteria scales (HD, D, CR, P) or auto-detects embedded rubric tables within the specification.',
    associatedStages: ['extracting_rubric', 'chunking_assignment', 'indexing_vectors', 'evaluating_requirements', 'evaluating_rubric', 'grounding_evidence', 'synthesizing_review', 'completed'],
  },
  {
    id: 'index_assignment',
    number: '04',
    label: 'Section-Aware Semantic Chunking & Vector DB',
    description: 'Splits assignment into section-tagged chunks, computes 384D dense embeddings, and stores in local ChromaDB.',
    associatedStages: ['chunking_assignment', 'indexing_vectors', 'evaluating_requirements', 'evaluating_rubric', 'grounding_evidence', 'synthesizing_review', 'completed'],
  },
  {
    id: 'eval_reqs',
    number: '05',
    label: 'Targeted RAG Requirement Evaluation',
    description: 'Queries ChromaDB with requirement vectors, performs Top-K semantic matching, and enforces structured evaluation JSON.',
    associatedStages: ['evaluating_requirements', 'evaluating_rubric', 'grounding_evidence', 'synthesizing_review', 'completed'],
  },
  {
    id: 'eval_rubric',
    number: '06',
    label: 'Rubric Alignment & Grounding Verification',
    description: 'Estimates performance tier alignment and verifies all cited quotes verbatim against student text chunks.',
    associatedStages: ['evaluating_rubric', 'grounding_evidence', 'synthesizing_review', 'completed'],
  },
  {
    id: 'final_review',
    number: '07',
    label: 'Review Synthesis & Action Prioritisation',
    description: 'Ranks feedback into HIGH, MEDIUM, and LOW actions to provide a structured academic revision plan.',
    associatedStages: ['synthesizing_review', 'completed'],
  },
]

export const ProcessingProgress: React.FC<ProcessingProgressProps> = ({
  progress,
  onOpenHowItWorks,
}) => {
  const terminalRef = useRef<HTMLDivElement>(null)
  const [showLogs, setShowLogs] = useState(true)

  useEffect(() => {
    if (terminalRef.current) {
      terminalRef.current.scrollTop = terminalRef.current.scrollHeight
    }
  }, [progress.logs])

  const getStepStatus = (index: number) => {
    const stageOrder: Record<PipelineStage, number> = {
      idle: 0,
      uploading: 0,
      parsing: 0,
      extracting_requirements: 1,
      extracting_rubric: 2,
      chunking_assignment: 3,
      indexing_vectors: 3,
      evaluating_requirements: 4,
      evaluating_rubric: 5,
      grounding_evidence: 5,
      synthesizing_review: 6,
      completed: 7,
      failed: -1,
    }

    const currentActiveIdx = stageOrder[progress.stage] ?? 0

    if (progress.stage === 'failed') return 'failed'
    if (currentActiveIdx > index) return 'completed'
    if (currentActiveIdx === index) return 'in_progress'
    return 'pending'
  }

  return (
    <div className="max-w-3xl mx-auto space-y-6 py-6">
      
      {/* Header & Progress Card */}
      <div className="bg-neutral-950 border border-neutral-800 rounded-2xl p-6 sm:p-8 space-y-6">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div className="space-y-1">
            <span className="text-[11px] font-mono uppercase tracking-wider text-neutral-500">
              Pipeline Execution in Progress
            </span>
            <h2 className="text-xl sm:text-2xl font-semibold text-white tracking-tight">
              Compiling Assignment Review
            </h2>
            <p className="text-xs text-neutral-400">
              {progress.message}
            </p>
          </div>

          <div className="flex items-center gap-3">
            {onOpenHowItWorks && (
              <button
                type="button"
                onClick={onOpenHowItWorks}
                className="px-3 py-1.5 rounded-full border border-neutral-800 hover:border-neutral-600 bg-black text-xs text-neutral-300 hover:text-white transition-all flex items-center gap-1.5"
              >
                <Compass className="w-3.5 h-3.5" />
                <span>Explain Logic</span>
              </button>
            )}
            <span className="text-2xl sm:text-3xl font-mono font-medium text-white">
              {progress.percent}%
            </span>
          </div>
        </div>

        {/* Minimalist Monochrome Progress Bar */}
        <div className="w-full bg-neutral-900 rounded-full h-1 overflow-hidden">
          <div
            className="bg-white h-1 rounded-full transition-all duration-300 ease-out"
            style={{ width: `${Math.max(progress.percent, 3)}%` }}
          />
        </div>
      </div>

      {/* Stage Checklist with Detailed Educational Descriptions */}
      <div className="bg-neutral-950 border border-neutral-800 rounded-2xl p-6 space-y-3">
        <div className="flex items-center justify-between pb-3 border-b border-neutral-900">
          <h3 className="text-xs font-mono uppercase tracking-wider text-neutral-400">
            Pipeline Execution Stages & RAG Rationale
          </h3>
          <span className="text-[11px] font-mono text-neutral-500">
            Automated Academic Workflow
          </span>
        </div>

        <div className="space-y-2 pt-2">
          {STAGES.map((step, idx) => {
            const status = getStepStatus(idx)
            return (
              <div
                key={step.id}
                className={`p-4 rounded-xl border transition-all ${
                  status === 'completed'
                    ? 'bg-neutral-900/40 border-neutral-800 text-neutral-300'
                    : status === 'in_progress'
                    ? 'bg-neutral-900 border-neutral-700 text-white'
                    : 'bg-black/30 border-neutral-900 text-neutral-600'
                }`}
              >
                <div className="flex items-start justify-between gap-3">
                  <div className="flex items-start gap-3">
                    <span className="font-mono text-xs pt-0.5 text-neutral-400 shrink-0">
                      {step.number}
                    </span>
                    <div className="space-y-1">
                      <div className="flex items-center gap-2">
                        <span className="text-xs font-semibold">{step.label}</span>
                        {status === 'in_progress' && (
                          <span className="w-1.5 h-1.5 rounded-full bg-white animate-pulse" />
                        )}
                      </div>
                      <p className="text-[11px] text-neutral-400 leading-relaxed font-sans max-w-xl">
                        {step.description}
                      </p>
                    </div>
                  </div>

                  <span className="text-[10px] font-mono px-2 py-0.5 rounded border border-neutral-800 uppercase tracking-wider shrink-0">
                    {status === 'completed' && 'Done'}
                    {status === 'in_progress' && 'Running'}
                    {status === 'pending' && 'Queued'}
                    {status === 'failed' && 'Error'}
                  </span>
                </div>
              </div>
            )
          })}
        </div>
      </div>

      {/* Diagnostic Terminal Stream */}
      <div className="bg-black border border-neutral-800 rounded-2xl p-4 space-y-3">
        <div className="flex items-center justify-between text-xs font-mono text-neutral-400 pb-2 border-b border-neutral-900">
          <div className="flex items-center gap-2">
            <Terminal className="w-3.5 h-3.5 text-neutral-400" />
            <span>Diagnostic Event Stream</span>
          </div>
          <button
            type="button"
            onClick={() => setShowLogs(!showLogs)}
            className="text-[10px] text-neutral-500 hover:text-neutral-300 underline underline-offset-2"
          >
            {showLogs ? 'Collapse' : 'Expand'}
          </button>
        </div>

        {showLogs && (
          <div
            ref={terminalRef}
            className="h-36 overflow-y-auto font-mono text-xs text-neutral-400 space-y-1 pr-2 leading-relaxed"
          >
            {progress.logs.length === 0 ? (
              <span className="text-neutral-600 italic">Initializing local pipeline...</span>
            ) : (
              progress.logs.map((log, i) => (
                <div key={i} className="truncate">
                  <span className="text-neutral-600">› </span>
                  <span className="text-neutral-300">{log}</span>
                </div>
              ))
            )}
          </div>
        )}
      </div>

    </div>
  )
}
