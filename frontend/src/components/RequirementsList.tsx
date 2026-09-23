import React, { useState } from 'react'
import { Filter, ArrowUpRight } from 'lucide-react'
import type { RequirementEvaluation, RequirementStatus, EvidenceItem } from '../types'

interface RequirementsListProps {
  evaluations: RequirementEvaluation[]
  onSelectEvidence: (ev: EvidenceItem) => void
}

export const RequirementsList: React.FC<RequirementsListProps> = ({
  evaluations,
  onSelectEvidence,
}) => {
  const [filter, setFilter] = useState<RequirementStatus | 'ALL'>('ALL')

  const filtered = evaluations.filter((e) => filter === 'ALL' || e.status === filter)

  const getStatusBadge = (status: RequirementStatus) => {
    switch (status) {
      case 'COVERED':
        return (
          <span className="px-2.5 py-0.5 rounded-full text-[11px] font-mono border border-neutral-700 bg-neutral-900 text-neutral-200">
            MET
          </span>
        )
      case 'PARTIAL':
        return (
          <span className="px-2.5 py-0.5 rounded-full text-[11px] font-mono border border-neutral-800 bg-black text-neutral-400">
            PARTIAL
          </span>
        )
      case 'MISSING':
        return (
          <span className="px-2.5 py-0.5 rounded-full text-[11px] font-mono border border-neutral-600 bg-white text-black font-semibold">
            MISSING
          </span>
        )
      case 'UNCLEAR':
        return (
          <span className="px-2.5 py-0.5 rounded-full text-[11px] font-mono border border-neutral-800 text-neutral-500">
            UNCLEAR
          </span>
        )
    }
  }

  return (
    <div className="space-y-6">
      
      {/* Filter Bar */}
      <div className="flex flex-wrap items-center justify-between gap-3 pb-3 border-b border-neutral-800">
        <div className="flex items-center gap-2 text-xs font-mono text-neutral-400">
          <Filter className="w-3.5 h-3.5" />
          <span>FILTER REQUIREMENTS</span>
        </div>

        <div className="flex flex-wrap gap-1 p-1 bg-neutral-950 border border-neutral-800 rounded-xl">
          {(['ALL', 'COVERED', 'PARTIAL', 'MISSING', 'UNCLEAR'] as const).map((st) => (
            <button
              key={st}
              onClick={() => setFilter(st)}
              className={`px-3 py-1 rounded-lg text-xs font-mono transition-all ${
                filter === st
                  ? 'bg-neutral-800 text-white font-semibold'
                  : 'text-neutral-400 hover:text-white'
              }`}
            >
              {st}
              {st !== 'ALL' && (
                <span className="ml-1 opacity-60">
                  ({evaluations.filter((e) => e.status === st).length})
                </span>
              )}
            </button>
          ))}
        </div>
      </div>

      {/* Cards List */}
      <div className="space-y-3">
        {filtered.length === 0 ? (
          <div className="text-center py-12 border border-neutral-800 rounded-2xl bg-neutral-950 text-neutral-500 text-xs font-mono">
            No requirements match this status filter.
          </div>
        ) : (
          filtered.map((item) => (
            <div
              key={item.requirement_id}
              className="border border-neutral-800 bg-neutral-950 rounded-2xl p-6 space-y-4 hover:border-neutral-700 transition-colors"
            >
              {/* Header */}
              <div className="flex flex-wrap items-center justify-between gap-3">
                <div className="flex items-center gap-3">
                  <span className="font-mono text-xs font-semibold text-white px-2 py-0.5 rounded bg-neutral-900 border border-neutral-800">
                    {item.requirement_id}
                  </span>
                  <span className="text-[11px] font-mono text-neutral-500">
                    {(item.confidence * 100).toFixed(0)}% Confidence
                  </span>
                </div>
                {getStatusBadge(item.status)}
              </div>

              {/* Reason */}
              <div className="space-y-1">
                <span className="text-[11px] font-mono uppercase tracking-wider text-neutral-500">
                  Grounded Assessment
                </span>
                <p className="text-xs sm:text-sm text-neutral-200 leading-relaxed font-sans">
                  {item.reason}
                </p>
              </div>

              {/* Citations */}
              {item.evidence && item.evidence.length > 0 && (
                <div className="space-y-2 pt-1">
                  <span className="text-[11px] font-mono uppercase tracking-wider text-neutral-500">
                    Retrieved Student Evidence ({item.evidence.length})
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

              {/* Actionable Suggestion */}
              {item.recommendation && (
                <div className="border border-neutral-800 bg-black rounded-xl p-4 text-xs space-y-1">
                  <span className="font-mono uppercase text-[10px] tracking-wider text-neutral-400">
                    Specific Remediation
                  </span>
                  <p className="text-neutral-300 leading-relaxed">
                    {item.recommendation}
                  </p>
                </div>
              )}

            </div>
          ))
        )}
      </div>

    </div>
  )
}
