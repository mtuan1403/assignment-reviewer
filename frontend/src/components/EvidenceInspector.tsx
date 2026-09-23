import React, { useState, useEffect } from 'react'
import { Search, Loader2 } from 'lucide-react'
import type { DocumentChunk } from '../types'
import { getReviewChunks } from '../api/client'

interface EvidenceInspectorProps {
  reviewId: string
}

export const EvidenceInspector: React.FC<EvidenceInspectorProps> = ({ reviewId }) => {
  const [chunks, setChunks] = useState<DocumentChunk[]>([])
  const [loading, setLoading] = useState(true)
  const [searchTerm, setSearchTerm] = useState('')
  const [selectedSection, setSelectedSection] = useState('ALL')

  useEffect(() => {
    let isMounted = true
    getReviewChunks(reviewId)
      .then((data) => {
        if (isMounted) {
          setChunks(data.chunks || [])
          setLoading(false)
        }
      })
      .catch((err) => {
        console.error('Failed to load chunks:', err)
        if (isMounted) setLoading(false)
      })
    return () => {
      isMounted = false
    }
  }, [reviewId])

  const sections = Array.from(new Set(chunks.map((c) => c.section)))

  const filteredChunks = chunks.filter((c) => {
    const matchesSection = selectedSection === 'ALL' || c.section === selectedSection
    const matchesSearch =
      !searchTerm ||
      c.text.toLowerCase().includes(searchTerm.toLowerCase()) ||
      c.section.toLowerCase().includes(searchTerm.toLowerCase()) ||
      c.chunk_id.toLowerCase().includes(searchTerm.toLowerCase())
    return matchesSection && matchesSearch
  })

  return (
    <div className="space-y-6">
      
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 pb-4 border-b border-neutral-800">
        <div>
          <span className="text-[11px] font-mono uppercase tracking-wider text-neutral-500">
            Local ChromaDB Vector Collection
          </span>
          <h3 className="text-base sm:text-lg font-semibold text-white mt-0.5">
            Indexed Assignment Chunks ({chunks.length})
          </h3>
          <p className="text-xs text-neutral-400 mt-0.5">
            Section-aware embeddings with exact page and section provenance
          </p>
        </div>

        {/* Search & Filter */}
        <div className="flex flex-wrap items-center gap-2 w-full sm:w-auto">
          <div className="relative flex-1 sm:w-60">
            <Search className="w-3.5 h-3.5 text-neutral-500 absolute left-3 top-2.5" />
            <input
              type="text"
              placeholder="Search chunk text..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full pl-8 pr-3 py-1.5 bg-neutral-950 border border-neutral-800 rounded-lg text-xs text-white placeholder-neutral-500 focus:outline-hidden focus:border-neutral-600"
            />
          </div>

          <select
            value={selectedSection}
            onChange={(e) => setSelectedSection(e.target.value)}
            className="px-3 py-1.5 bg-neutral-950 border border-neutral-800 rounded-lg text-xs text-neutral-300 focus:outline-hidden focus:border-neutral-600 max-w-[170px] truncate"
          >
            <option value="ALL">All Sections</option>
            {sections.map((s, i) => (
              <option key={i} value={s}>
                {s}
              </option>
            ))}
          </select>
        </div>
      </div>

      {loading ? (
        <div className="flex flex-col items-center justify-center py-16 text-neutral-500 space-y-2">
          <Loader2 className="w-5 h-5 animate-spin text-neutral-400" />
          <span className="text-xs font-mono">Retrieving chunks from local SQLite ChromaDB...</span>
        </div>
      ) : filteredChunks.length === 0 ? (
        <div className="text-center py-12 border border-neutral-800 rounded-2xl bg-neutral-950 text-neutral-500 text-xs font-mono">
          No chunks match query.
        </div>
      ) : (
        <div className="space-y-3">
          {filteredChunks.map((chunk) => (
            <div
              key={chunk.chunk_id}
              className="border border-neutral-800 bg-neutral-950 rounded-2xl p-5 space-y-3 hover:border-neutral-700 transition-colors"
            >
              <div className="flex flex-wrap items-center justify-between gap-2 text-[11px] font-mono">
                <div className="flex items-center gap-2">
                  <span className="font-semibold text-white px-2 py-0.5 rounded bg-neutral-900 border border-neutral-800">
                    {chunk.chunk_id}
                  </span>
                  <span className="text-neutral-400">
                    Page {chunk.page}
                  </span>
                </div>
                <span className="text-neutral-500">
                  {chunk.token_count} words
                </span>
              </div>

              <div className="text-xs font-medium text-neutral-300 border border-neutral-900 bg-black px-3 py-1 rounded-lg">
                Section: {chunk.section}
              </div>

              <p className="text-xs sm:text-sm text-neutral-300 font-sans leading-relaxed whitespace-pre-wrap">
                {chunk.text}
              </p>
            </div>
          ))}
        </div>
      )}

    </div>
  )
}
