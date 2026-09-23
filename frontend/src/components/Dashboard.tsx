import React, { useState } from 'react'
import {
  RotateCcw,
  Compass,
  ShieldAlert
} from 'lucide-react'
import type { OverallReview, EvidenceItem } from '../types'
import { RequirementsList } from './RequirementsList'
import { RubricAnalysis } from './RubricAnalysis'
import { PriorityImprovements } from './PriorityImprovements'
import { EvidenceInspector } from './EvidenceInspector'
import { EvidenceModal } from './EvidenceModal'

interface DashboardProps {
  review: OverallReview
  onReset: () => void
  onOpenHowItWorks: () => void
}

export const Dashboard: React.FC<DashboardProps> = ({ review, onReset, onOpenHowItWorks }) => {
  const [activeTab, setActiveTab] = useState<
    'overview' | 'requirements' | 'rubric' | 'priorities' | 'evidence'
  >('overview')
  const [selectedEvidence, setSelectedEvidence] = useState<EvidenceItem | null>(null)

  const { requirements_coverage } = review

  return (
    <div className="max-w-5xl mx-auto space-y-8 py-4 text-neutral-100">
      
      {/* Top Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-6 border-b border-neutral-800">
        <div className="space-y-1">
          <div className="flex items-center gap-2">
            <span className="text-[11px] font-mono uppercase tracking-wider text-neutral-500">
              Analysis Complete • ID: {review.review_id.slice(0, 8)}
            </span>
            <span className="px-2 py-0.5 rounded-full text-[10px] font-mono border border-neutral-700 bg-neutral-900 text-neutral-200">
              {review.llm_model ? `Model: ${review.llm_model}` : review.llm_provider || 'Local Model'}
            </span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-semibold tracking-tight text-white">
            Assignment Review
          </h1>
        </div>


        <div className="flex items-center gap-2.5">
          <button
            onClick={onOpenHowItWorks}
            className="px-3.5 py-2 rounded-full border border-neutral-800 bg-neutral-900 hover:border-neutral-700 hover:text-white text-xs font-medium text-neutral-300 transition-colors flex items-center gap-1.5"
          >
            <Compass className="w-3.5 h-3.5" />
            <span>How AI Evaluated This</span>
          </button>

          <button
            onClick={onReset}
            className="px-3.5 py-2 rounded-full bg-white text-black hover:bg-neutral-200 text-xs font-semibold transition-colors flex items-center gap-1.5"
          >
            <RotateCcw className="w-3.5 h-3.5" />
            <span>New Review</span>
          </button>
        </div>
      </div>

      {/* University Disclaimer Banner */}
      <div className="border border-neutral-800 bg-neutral-950 rounded-2xl p-4 sm:p-5 flex items-start gap-3">
        <ShieldAlert className="w-4 h-4 text-neutral-400 shrink-0 mt-0.5" />
        <div className="text-xs text-neutral-400 leading-relaxed">
          <span className="font-semibold text-neutral-200">Formative Academic Advisory: </span>
          {review.limitations_disclaimer}
        </div>
      </div>

      {/* Navigation Tabs - Modern Segmented Control */}
      <div className="flex flex-wrap gap-1 p-1 bg-neutral-950 border border-neutral-800 rounded-xl">
        <button
          onClick={() => setActiveTab('overview')}
          className={`px-4 py-2 rounded-lg text-xs font-medium transition-all ${
            activeTab === 'overview'
              ? 'bg-neutral-800 text-white font-semibold shadow-xs'
              : 'text-neutral-400 hover:text-white'
          }`}
        >
          Overview
        </button>

        <button
          onClick={() => setActiveTab('requirements')}
          className={`px-4 py-2 rounded-lg text-xs font-medium transition-all ${
            activeTab === 'requirements'
              ? 'bg-neutral-800 text-white font-semibold shadow-xs'
              : 'text-neutral-400 hover:text-white'
          }`}
        >
          Requirements ({review.requirement_evaluations.length})
        </button>

        <button
          onClick={() => setActiveTab('rubric')}
          className={`px-4 py-2 rounded-lg text-xs font-medium transition-all ${
            activeTab === 'rubric'
              ? 'bg-neutral-800 text-white font-semibold shadow-xs'
              : 'text-neutral-400 hover:text-white'
          }`}
        >
          Rubric Alignment ({review.rubric_evaluations.length})
        </button>

        <button
          onClick={() => setActiveTab('priorities')}
          className={`px-4 py-2 rounded-lg text-xs font-medium transition-all ${
            activeTab === 'priorities'
              ? 'bg-neutral-800 text-white font-semibold shadow-xs'
              : 'text-neutral-400 hover:text-white'
          }`}
        >
          Priority Actions ({review.priority_improvements.length})
        </button>

        <button
          onClick={() => setActiveTab('evidence')}
          className={`px-4 py-2 rounded-lg text-xs font-medium transition-all ${
            activeTab === 'evidence'
              ? 'bg-neutral-800 text-white font-semibold shadow-xs'
              : 'text-neutral-400 hover:text-white'
          }`}
        >
          Vector Evidence
        </button>
      </div>

      {/* TAB CONTENT: Overview */}
      {activeTab === 'overview' && (
        <div className="space-y-6">
          
          {/* Executive Summary Card */}
          <div className="border border-neutral-800 bg-neutral-950 rounded-2xl p-6 sm:p-7 space-y-3">
            <span className="text-[11px] font-mono uppercase tracking-wider text-neutral-500">
              Executive Evaluation Summary
            </span>
            <p className="text-sm sm:text-base text-neutral-200 leading-relaxed font-sans">
              {review.summary}
            </p>
          </div>

          {/* Stats KPI Cards */}
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
            <div className="border border-neutral-800 bg-neutral-950 rounded-2xl p-5 space-y-1">
              <span className="text-[11px] font-mono uppercase text-neutral-500">Coverage</span>
              <div className="text-3xl font-semibold text-white tracking-tight">
                {requirements_coverage.coverage_percentage}%
              </div>
              <p className="text-[11px] text-neutral-400">
                {requirements_coverage.covered} of {requirements_coverage.total} met
              </p>
            </div>

            <div className="border border-neutral-800 bg-neutral-950 rounded-2xl p-5 space-y-1">
              <span className="text-[11px] font-mono uppercase text-neutral-500">Partial</span>
              <div className="text-3xl font-semibold text-white tracking-tight">
                {requirements_coverage.partial}
              </div>
              <p className="text-[11px] text-neutral-400">Need elaboration</p>
            </div>

            <div className="border border-neutral-800 bg-neutral-950 rounded-2xl p-5 space-y-1">
              <span className="text-[11px] font-mono uppercase text-neutral-500">Missing</span>
              <div className="text-3xl font-semibold text-white tracking-tight">
                {requirements_coverage.missing}
              </div>
              <p className="text-[11px] text-neutral-400">Critical gaps</p>
            </div>

            <div className="border border-neutral-800 bg-neutral-950 rounded-2xl p-5 space-y-1">
              <span className="text-[11px] font-mono uppercase text-neutral-500">Actions</span>
              <div className="text-3xl font-semibold text-white tracking-tight">
                {review.priority_improvements.length}
              </div>
              <p className="text-[11px] text-neutral-400">Ranked suggestions</p>
            </div>
          </div>

          {/* Rubric Alignment Overview Grid */}
          {review.rubric_evaluations.length > 0 ? (
            <div className="border border-neutral-800 bg-neutral-950 rounded-2xl p-6 space-y-4">
              <div className="flex items-center justify-between pb-2 border-b border-neutral-900">
                <span className="text-[11px] font-mono uppercase tracking-wider text-neutral-400">
                  Rubric Performance Alignment
                </span>
                <span className="text-[11px] font-mono text-neutral-500">
                  {review.rubric_evaluations.length} Criteria Evaluated
                </span>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-3">
                {review.rubric_evaluations.map((item) => (
                  <div
                    key={item.criterion_id}
                    className="border border-neutral-800 bg-black rounded-xl p-4 space-y-2 hover:border-neutral-700 transition-colors"
                  >
                    <div className="flex items-center justify-between text-[11px] font-mono text-neutral-500">
                      <span>{item.criterion_id}</span>
                      <span>{(item.confidence * 100).toFixed(0)}% conf</span>
                    </div>
                    <h4 className="text-xs font-semibold text-neutral-200 line-clamp-1">
                      {item.criterion_name}
                    </h4>
                    <div className="pt-2">
                      <span className="text-xl font-bold font-mono tracking-tight text-white">
                        {item.estimated_level}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          ) : (
            <div className="border border-neutral-800 bg-neutral-950 rounded-2xl p-5 text-neutral-400 text-xs">
              <span className="font-semibold text-white">Marking Criteria Notice: </span>
              Rubric upload was omitted. Analysis was executed directly against assignment brief requirements.
            </div>
          )}

          {/* Strengths & Weaknesses */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="border border-neutral-800 bg-neutral-950 rounded-2xl p-6 space-y-3">
              <span className="text-[11px] font-mono uppercase tracking-wider text-neutral-400">
                Verified Substantive Strengths
              </span>
              <ul className="space-y-2.5 text-xs text-neutral-300">
                {review.main_strengths.map((s, i) => (
                  <li key={i} className="flex items-start gap-2.5">
                    <span className="text-white font-bold">✓</span>
                    <span className="leading-relaxed">{s}</span>
                  </li>
                ))}
              </ul>
            </div>

            <div className="border border-neutral-800 bg-neutral-950 rounded-2xl p-6 space-y-3">
              <span className="text-[11px] font-mono uppercase tracking-wider text-neutral-400">
                Identified Compliance Deficits
              </span>
              <ul className="space-y-2.5 text-xs text-neutral-300">
                {review.main_weaknesses.map((w, i) => (
                  <li key={i} className="flex items-start gap-2.5">
                    <span className="text-neutral-500 font-bold">•</span>
                    <span className="leading-relaxed">{w}</span>
                  </li>
                ))}
              </ul>
            </div>
          </div>

        </div>
      )}

      {/* TAB CONTENT: Requirements */}
      {activeTab === 'requirements' && (
        <RequirementsList
          evaluations={review.requirement_evaluations}
          onSelectEvidence={(ev) => setSelectedEvidence(ev)}
        />
      )}

      {/* TAB CONTENT: Rubric */}
      {activeTab === 'rubric' && (
        review.rubric_evaluations.length > 0 ? (
          <RubricAnalysis
            evaluations={review.rubric_evaluations}
            onSelectEvidence={(ev) => setSelectedEvidence(ev)}
          />
        ) : (
          <div className="text-center py-16 border border-neutral-800 rounded-2xl bg-neutral-950 text-neutral-400 space-y-2">
            <h4 className="text-sm font-semibold text-white">No Rubric Provided</h4>
            <p className="text-xs text-neutral-400 max-w-sm mx-auto">
              Evaluation was performed directly on the task specification deliverables.
            </p>
          </div>
        )
      )}

      {/* TAB CONTENT: Priorities */}
      {activeTab === 'priorities' && (
        <PriorityImprovements
          items={review.priority_improvements}
          onSelectEvidence={(ev) => setSelectedEvidence(ev)}
        />
      )}

      {/* TAB CONTENT: Evidence */}
      {activeTab === 'evidence' && <EvidenceInspector reviewId={review.review_id} />}

      {/* Evidence Modal */}
      <EvidenceModal
        evidence={selectedEvidence}
        onClose={() => setSelectedEvidence(null)}
      />

    </div>
  )
}
