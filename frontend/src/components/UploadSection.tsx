import React, { useState, useRef } from 'react'
import {
  FileText,
  AlertCircle,
  Play,
  Lock,
  Compass,
  ArrowRight
} from 'lucide-react'

interface UploadSectionProps {
  onStartReview: (spec: File, rubric: File | null, draft: File) => void
  onStartSample: () => void
  onOpenHowItWorks: () => void
  isLoading: boolean
}

export const UploadSection: React.FC<UploadSectionProps> = ({
  onStartReview,
  onStartSample,
  onOpenHowItWorks,
  isLoading,
}) => {
  const [specFile, setSpecFile] = useState<File | null>(null)
  const [rubricFile, setRubricFile] = useState<File | null>(null)
  const [draftFile, setDraftFile] = useState<File | null>(null)
  const [error, setError] = useState<string | null>(null)

  const specRef = useRef<HTMLInputElement>(null)
  const rubricRef = useRef<HTMLInputElement>(null)
  const draftRef = useRef<HTMLInputElement>(null)

  const handleStart = (e: React.FormEvent) => {
    e.preventDefault()
    if (!specFile || !draftFile) {
      setError('Please provide at least the Assignment Specification and your Student Draft.')
      return
    }
    setError(null)
    onStartReview(specFile, rubricFile, draftFile)
  }

  const renderFileInput = (
    stepNumber: string,
    label: string,
    sublabel: string,
    file: File | null,
    setFile: (f: File | null) => void,
    inputRef: React.RefObject<HTMLInputElement | null>,
    isOptional: boolean = false
  ) => {
    return (
      <div
        onClick={() => inputRef.current?.click()}
        className={`group relative rounded-2xl p-6 text-left cursor-pointer transition-all duration-200 border ${
          file
            ? 'border-neutral-400 bg-neutral-900/80 shadow-md'
            : 'border-neutral-800 bg-neutral-950/60 hover:border-neutral-700 hover:bg-neutral-900/40'
        }`}
      >
        <input
          type="file"
          ref={inputRef}
          className="hidden"
          accept=".pdf,.docx,.txt"
          onChange={(e) => {
            if (e.target.files && e.target.files[0]) {
              setFile(e.target.files[0])
              setError(null)
            }
          }}
        />

        <div className="flex items-center justify-between mb-4">
          <span className="text-[11px] font-mono tracking-wider text-neutral-500 uppercase">
            Step {stepNumber} {isOptional && '• Optional'}
          </span>
          {file ? (
            <span className="w-5 h-5 rounded-full bg-white text-black flex items-center justify-center text-xs">
              ✓
            </span>
          ) : (
            <span className="text-neutral-600 text-xs group-hover:text-neutral-400 transition-colors">
              +
            </span>
          )}
        </div>

        {file ? (
          <div className="space-y-1">
            <p className="text-sm font-semibold text-white truncate max-w-[220px]">{file.name}</p>
            <p className="text-xs text-neutral-400 font-mono">{(file.size / 1024).toFixed(1)} KB</p>
            <div className="pt-2">
              <span className="text-[10px] font-mono text-neutral-400 uppercase tracking-wider underline underline-offset-4">
                Click to replace
              </span>
            </div>
          </div>
        ) : (
          <div className="space-y-1.5">
            <h3 className="text-sm font-semibold text-neutral-200 group-hover:text-white transition-colors">
              {label}
            </h3>
            <p className="text-xs text-neutral-500 leading-relaxed group-hover:text-neutral-400 transition-colors">
              {sublabel}
            </p>
            <div className="pt-3 flex items-center gap-1.5 text-[10px] font-mono text-neutral-600">
              <span>PDF • DOCX • TXT</span>
            </div>
          </div>
        )}
      </div>
    )
  }

  return (
    <div className="max-w-4xl mx-auto space-y-10 py-6">
      
      {/* Hero Header */}
      <div className="text-center space-y-4 max-w-2xl mx-auto">
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full border border-neutral-800 bg-neutral-900/60 text-neutral-300 text-xs font-mono">
          <span>LOCAL-FIRST RAG SYSTEM</span>
        </div>

        <h1 className="text-3xl sm:text-5xl font-semibold tracking-tight text-white">
          AI Assignment Reviewer
        </h1>

        <p className="text-neutral-400 text-sm sm:text-base leading-relaxed">
          A minimalist, evidence-grounded academic assessment engine. Upload your assignment specification,
          optional marking rubric, and draft submission to verify compliance before submission.
        </p>

        {/* Learn How It Works Button */}
        <div className="pt-1">
          <button
            type="button"
            onClick={onOpenHowItWorks}
            className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full border border-neutral-800 hover:border-neutral-600 bg-neutral-950 text-xs text-neutral-300 hover:text-white transition-all group"
          >
            <Compass className="w-3.5 h-3.5 text-neutral-400 group-hover:text-white transition-colors" />
            <span>How does the AI process this? (View Architecture & Logic)</span>
            <ArrowRight className="w-3 h-3 text-neutral-500 group-hover:translate-x-0.5 transition-transform" />
          </button>
        </div>
      </div>

      {/* Error alert */}
      {error && (
        <div className="bg-neutral-950 border border-neutral-700 rounded-xl p-3.5 text-neutral-200 text-xs flex items-center gap-2.5">
          <AlertCircle className="w-4 h-4 shrink-0 text-white" />
          <span>{error}</span>
        </div>
      )}

      {/* Upload Cards Grid */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {renderFileInput(
          '01',
          'Assignment Spec',
          'Task brief, question prompts, or syllabus requirements',
          specFile,
          setSpecFile,
          specRef
        )}
        {renderFileInput(
          '02',
          'Marking Rubric',
          'Criteria table or grading descriptors (leave empty if in spec)',
          rubricFile,
          setRubricFile,
          rubricRef,
          true
        )}
        {renderFileInput(
          '03',
          'Student Draft',
          'Your assignment draft submission to evaluate',
          draftFile,
          setDraftFile,
          draftRef
        )}
      </div>

      {/* Action Buttons */}
      <div className="flex flex-col sm:flex-row items-center justify-center gap-3 pt-2">
        <button
          onClick={handleStart}
          disabled={isLoading || !specFile || !draftFile}
          className="w-full sm:w-auto px-8 py-3 bg-white text-black font-semibold text-xs tracking-wide rounded-full hover:bg-neutral-200 disabled:opacity-30 disabled:cursor-not-allowed transition-all flex items-center justify-center gap-2 shadow-sm"
        >
          <Play className="w-3.5 h-3.5 fill-current" />
          <span>Compile Assignment Review</span>
        </button>

        <button
          type="button"
          onClick={onStartSample}
          disabled={isLoading}
          className="w-full sm:w-auto px-6 py-3 bg-neutral-900 border border-neutral-800 hover:border-neutral-700 text-neutral-300 hover:text-white text-xs font-medium rounded-full transition-all flex items-center justify-center gap-2"
        >
          <FileText className="w-3.5 h-3.5 text-neutral-400" />
          <span>Try Demo Sample Assignment</span>
        </button>
      </div>

      {/* Trust & Privacy Notice */}
      <div className="border-t border-neutral-900 pt-6 text-center text-xs text-neutral-500 flex flex-col sm:flex-row items-center justify-center gap-4 font-mono">
        <span className="flex items-center gap-1.5">
          <Lock className="w-3.5 h-3.5 text-neutral-400" />
          All documents stored locally in data/
        </span>
        <span className="hidden sm:inline text-neutral-800">•</span>
        <span>Deterministic Evidence Grounding</span>
        <span className="hidden sm:inline text-neutral-800">•</span>
        <span>Zero Third-Party Cloud Persistence</span>
      </div>

    </div>
  )
}
