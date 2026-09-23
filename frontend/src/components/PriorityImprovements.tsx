import React from 'react'
import { ArrowUpRight, ArrowRight } from 'lucide-react'
import type { PriorityItem, PriorityLevel, EvidenceItem } from '../types'

interface PriorityImprovementsProps {
  items: PriorityItem[]
  onSelectEvidence: (ev: EvidenceItem) => void
}

export const PriorityImprovements: React.FC<PriorityImprovementsProps> = ({
  items,
  onSelectEvidence,
}) => {
  const getPriorityBadge = (priority: PriorityLevel) => {
    switch (priority) {
      case 'HIGH':
        return (
          <span className="px-2.5 py-0.5 rounded-full text-[10px] font-mono border border-neutral-600 bg-white text-black font-semibold">
            HIGH PRIORITY
          </span>
        )
      case 'MEDIUM':
        return (
          <span className="px-2.5 py-0.5 rounded-full text-[10px] font-mono border border-neutral-700 bg-neutral-900 text-neutral-200">
            MEDIUM
          </span>
        )
      case 'LOW':
        return (
          <span className="px-2.5 py-0.5 rounded-full text-[10px] font-mono border border-neutral-800 text-neutral-500">
            LOW
          </span>
        )
    }
  }

  const highItems = items.filter((it) => it.priority === 'HIGH')
  const medItems = items.filter((it) => it.priority === 'MEDIUM')
  const lowItems = items.filter((it) => it.priority === 'LOW')

  return (
    <div className="space-y-6">
      
      <div className="border border-neutral-800 bg-neutral-950 rounded-2xl p-4 sm:p-5 text-xs text-neutral-400 leading-relaxed">
        <span className="font-semibold text-white">Revision Ordering: </span>
        Address HIGH priority compliance gaps first to secure baseline passing and specification mandates,
        followed by MEDIUM depth improvements and LOW stylistic polish.
      </div>

      <div className="space-y-3">
        {items.length === 0 ? (
          <div className="text-center py-12 border border-neutral-800 rounded-2xl bg-neutral-950 text-neutral-500 text-xs font-mono">
            No priority improvements flagged. All specifications comprehensively met.
          </div>
        ) : (
          [...highItems, ...medItems, ...lowItems].map((item, idx) => (
            <div
              key={idx}
              className="border border-neutral-800 bg-neutral-950 rounded-2xl p-6 space-y-4 hover:border-neutral-700 transition-colors"
            >
              {/* Header */}
              <div className="flex items-center justify-between gap-3">
                <span className="text-[11px] font-mono text-neutral-500">
                  ACTION #{String(idx + 1).padStart(2, '0')}
                </span>
                {getPriorityBadge(item.priority)}
              </div>

              {/* Issue */}
              <h4 className="text-sm sm:text-base font-semibold text-white leading-snug">
                {item.issue}
              </h4>

              {/* Why it Matters */}
              <div className="text-xs text-neutral-300 border border-neutral-900 bg-black rounded-xl p-3.5 leading-relaxed">
                <span className="font-semibold text-white">Academic Rationale: </span>
                {item.why_it_matters}
              </div>

              {/* Citations */}
              {item.evidence && item.evidence.length > 0 && (
                <div className="flex flex-wrap items-center gap-2 pt-1">
                  <span className="text-[11px] font-mono uppercase tracking-wider text-neutral-500">
                    Draft Evidence:
                  </span>
                  {item.evidence.map((ev, i) => (
                    <button
                      key={i}
                      onClick={() => onSelectEvidence(ev)}
                      className="group inline-flex items-center gap-1.5 text-xs font-mono text-neutral-300 hover:text-white border border-neutral-800 hover:border-neutral-600 bg-black px-2.5 py-1 rounded-lg transition-colors"
                    >
                      <span>p.{ev.page} ({ev.chunk_id})</span>
                      <ArrowUpRight className="w-3 h-3 text-neutral-600 group-hover:text-white" />
                    </button>
                  ))}
                </div>
              )}

              {/* Suggested Action */}
              <div className="border border-neutral-800 bg-black rounded-xl p-4 flex items-start gap-3">
                <ArrowRight className="w-4 h-4 text-white shrink-0 mt-0.5" />
                <div className="text-xs text-neutral-200 leading-relaxed">
                  <span className="font-semibold text-white">Recommended Action: </span>
                  {item.suggested_action}
                </div>
              </div>

            </div>
          ))
        )}
      </div>

    </div>
  )
}
