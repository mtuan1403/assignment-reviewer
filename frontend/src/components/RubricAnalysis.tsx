import React from 'react'
import { ArrowUpRight, HelpCircle } from 'lucide-react'
import type { RubricEvaluation, EvidenceItem } from '../types'

interface RubricAnalysisProps {
  evaluations: RubricEvaluation[]
  onSelectEvidence: (ev: EvidenceItem) => void
}

export const RubricAnalysis: React.FC<RubricAnalysisProps> = ({
  evaluations,
  onSelectEvidence,
}) => {
  return (
    <div className="space-y-6">
      
      {/* Educational Notice */}
      <div className="border border-neutral-800 bg-neutral-950 rounded-2xl p-4 sm:p-5 flex items-start gap-3">
        <HelpCircle className="w-4 h-4 text-neutral-400 shrink-0 mt-0.5" />
        <div className="text-xs text-neutral-400 leading-relaxed">
          <span className="font-semibold text-neutral-200">Rubric Calibration: </span>
          The performance descriptors reflect semantic vector alignment against the official marking criteria.
          Assessors mark holistically; treat these diagnostic grades as actionable levers to move to the next tier.
        </div>
      </div>

      {/* Rubric Cards */}
      <div className="space-y-4">
        {evaluations.map((item) => (
          <div
            key={item.criterion_id}
            className="border border-neutral-800 bg-neutral-950 rounded-2xl p-6 space-y-5 hover:border-neutral-700 transition-colors"
          >
            {/* Header */}
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-4 border-b border-neutral-900">
              <div className="space-y-1">
                <div className="flex items-center gap-2">
                  <span className="text-xs font-mono font-bold text-neutral-400 px-2 py-0.5 rounded bg-neutral-900 border border-neutral-800">
                    {item.criterion_id}
                  </span>
                  <h3 className="text-sm sm:text-base font-semibold text-white">
                    {item.criterion_name}
                  </h3>
                </div>
                <p className="text-[11px] font-mono text-neutral-500">
                  {(item.confidence * 100).toFixed(0)}% Retrieval Confidence
                </p>
              </div>

              <div>
                <span className="px-3.5 py-1 rounded-full border border-neutral-700 bg-neutral-900 text-white font-mono text-xs font-bold tracking-wider">
                  Level: {item.estimated_level}
                </span>
              </div>
            </div>

            {/* Strengths & Weaknesses Grid */}
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div className="border border-neutral-900 bg-black rounded-xl p-4 space-y-2">
                <span className="text-[11px] font-mono uppercase tracking-wider text-neutral-400">
                  Demonstrated Competencies
                </span>
                <ul className="space-y-1.5 text-xs text-neutral-300">
                  {item.strengths.map((str, idx) => (
                    <li key={idx} className="flex items-start gap-2">
                      <span className="text-neutral-400 font-bold">✓</span>
                      <span className="leading-relaxed">{str}</span>
                    </li>
                  ))}
                </ul>
              </div>

              <div className="border border-neutral-900 bg-black rounded-xl p-4 space-y-2">
                <span className="text-[11px] font-mono uppercase tracking-wider text-neutral-400">
                  Identified Gaps
                </span>
                <ul className="space-y-1.5 text-xs text-neutral-300">
                  {item.weaknesses.map((wk, idx) => (
                    <li key={idx} className="flex items-start gap-2">
                      <span className="text-neutral-500 font-bold">•</span>
                      <span className="leading-relaxed">{wk}</span>
                    </li>
                  ))}
                </ul>
              </div>
            </div>

            {/* Citations */}
            {item.evidence && item.evidence.length > 0 && (
              <div className="space-y-2 pt-1">
                <span className="text-[11px] font-mono uppercase tracking-wider text-neutral-500">
                  Supporting Draft Citations
                </span>
                <div className="flex flex-wrap gap-2">
                  {item.evidence.map((ev, i) => (
                    <button
                      key={i}
                      onClick={() => onSelectEvidence(ev)}
                      className="group text-left max-w-full inline-flex items-center gap-2 px-3 py-1.5 rounded-lg border border-neutral-800 bg-black hover:border-neutral-600 transition-all text-xs"
                    >
                      <span className="font-mono text-neutral-400 shrink-0 text-[11px]">
                        p.{ev.page} ({ev.section})
                      </span>
                      <span className="text-neutral-300 truncate max-w-xs group-hover:text-white">
                        "{ev.quote}"
                      </span>
                      <ArrowUpRight className="w-3 h-3 text-neutral-600 group-hover:text-white shrink-0" />
                    </button>
                  ))}
                </div>
              </div>
            )}

            {/* Recommendations */}
            {item.recommendations && item.recommendations.length > 0 && (
              <div className="border border-neutral-800 bg-black rounded-xl p-4 text-xs space-y-1.5">
                <span className="font-mono uppercase text-[10px] tracking-wider text-neutral-400">
                  Path to Next Grade Band
                </span>
                <ul className="list-disc pl-4 space-y-1 text-neutral-300 leading-relaxed">
                  {item.recommendations.map((rec, i) => (
                    <li key={i}>{rec}</li>
                  ))}
                </ul>
              </div>
            )}

          </div>
        ))}
      </div>

    </div>
  )
}
