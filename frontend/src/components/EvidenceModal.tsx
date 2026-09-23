import React from 'react'
import { X, Check } from 'lucide-react'
import type { EvidenceItem } from '../types'

interface EvidenceModalProps {
  evidence: EvidenceItem | null
  onClose: () => void
}

export const EvidenceModal: React.FC<EvidenceModalProps> = ({ evidence, onClose }) => {
  if (!evidence) return null

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-md animate-in fade-in duration-200">
      <div className="bg-black border border-neutral-800 rounded-2xl max-w-lg w-full p-6 shadow-2xl space-y-5 relative text-neutral-100">
        
        {/* Close Button */}
        <button
          onClick={onClose}
          className="absolute top-5 right-5 text-neutral-400 hover:text-white p-1 rounded-lg hover:bg-neutral-900 transition-colors"
        >
          <X className="w-4 h-4" />
        </button>

        {/* Modal Header */}
        <div className="space-y-1">
          <span className="text-[10px] font-mono uppercase tracking-wider text-neutral-500">
            Vector Retrieval Provenance
          </span>
          <h3 className="text-base font-semibold text-white">
            Grounded Student Evidence
          </h3>
          <p className="text-xs text-neutral-400">
            Verbatim excerpt retrieved from your submitted document
          </p>
        </div>

        {/* Metadata Badges */}
        <div className="flex flex-wrap gap-2 text-xs font-mono">
          <span className="px-2.5 py-1 rounded-md border border-neutral-800 bg-neutral-950 text-neutral-300">
            Page {evidence.page}
          </span>
          <span className="px-2.5 py-1 rounded-md border border-neutral-800 bg-neutral-950 text-neutral-300">
            {evidence.section}
          </span>
          <span className="px-2.5 py-1 rounded-md border border-neutral-800 bg-neutral-950 text-neutral-400">
            {evidence.chunk_id}
          </span>
        </div>

        {/* Quote Block */}
        <div className="border border-neutral-800 bg-neutral-950 rounded-xl p-4 space-y-2">
          <div className="text-[10px] font-mono uppercase tracking-wider text-neutral-400 flex items-center gap-1.5">
            <Check className="w-3 h-3 text-white" />
            <span>Verified Citation Quote</span>
          </div>
          <blockquote className="text-xs sm:text-sm text-neutral-200 italic leading-relaxed border-l-2 border-white pl-3.5">
            "{evidence.quote}"
          </blockquote>
        </div>

        <p className="text-[11px] text-neutral-500 leading-relaxed font-mono">
          Verified via case-insensitive exact and fuzzy substring matching against the indexed vector chunk.
        </p>

        {/* Dismiss Button */}
        <div className="pt-2 flex justify-end">
          <button
            onClick={onClose}
            className="px-4 py-2 bg-white text-black hover:bg-neutral-200 text-xs font-semibold rounded-full transition-colors"
          >
            Done
          </button>
        </div>

      </div>
    </div>
  )
}
