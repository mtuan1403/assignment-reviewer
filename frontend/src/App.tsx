import { useState, useEffect } from 'react'
import {
  startReview,
  startSampleReview,
  getReviewProgress,
  getReview,
} from './api/client'
import type { OverallReview, ProgressStatus } from './types'
import { UploadSection } from './components/UploadSection'
import { ProcessingProgress } from './components/ProcessingProgress'
import { Dashboard } from './components/Dashboard'
import { EducationalModal } from './components/EducationalModal'
import { Compass, RotateCcw, Lock } from 'lucide-react'

type ScreenState = 'upload' | 'processing' | 'dashboard'

export function App() {
  const [screen, setScreen] = useState<ScreenState>('upload')
  const [currentReviewId, setCurrentReviewId] = useState<string | null>(null)
  const [progress, setProgress] = useState<ProgressStatus>({
    review_id: '',
    stage: 'idle',
    percent: 0,
    message: 'Idle',
    logs: [],
  })
  const [review, setReview] = useState<OverallReview | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [isLoading, setIsLoading] = useState(false)
  const [isHowItWorksOpen, setIsHowItWorksOpen] = useState(false)
  const [systemModel, setSystemModel] = useState<string>('gemini-1.5-flash')

  // Fetch configured model info on mount
  useEffect(() => {
    fetch('/api/health')
      .then((r) => r.json())
      .then((d) => {
        if (d.llm_model) {
          setSystemModel(`${d.llm_provider || 'gemini'}: ${d.llm_model}`)
        }
      })
      .catch(() => {})
  }, [])

  // Polling loop when in processing state
  useEffect(() => {
    if (screen !== 'processing' || !currentReviewId) return


    let isSubscribed = true
    const interval = setInterval(async () => {
      try {
        const prog = await getReviewProgress(currentReviewId)
        if (!isSubscribed) return
        setProgress(prog)

        if (prog.stage === 'completed') {
          clearInterval(interval)
          // Fetch completed review
          const fullReview = await getReview(currentReviewId)
          if (!isSubscribed) return
          setReview(fullReview)
          setScreen('dashboard')
        } else if (prog.stage === 'failed') {
          clearInterval(interval)
          setError(prog.error || 'Review processing failed.')
          setScreen('upload')
        }
      } catch (err: any) {
        console.error('Error polling progress:', err)
      }
    }, 1200)

    return () => {
      isSubscribed = false
      clearInterval(interval)
    }
  }, [screen, currentReviewId])

  const handleStartReview = async (spec: File, rubric: File | null, draft: File) => {
    setIsLoading(true)
    setError(null)
    try {
      const res = await startReview(spec, rubric, draft)
      setCurrentReviewId(res.review_id)
      const rubricLog = rubric
        ? 'Uploaded specification, rubric, and assignment.'
        : 'Uploaded specification and assignment (rubric omitted).'
      setProgress({
        review_id: res.review_id,
        stage: 'uploading',
        percent: 5,
        message: 'Parsing and structuring document trees...',
        logs: [rubricLog],
      })
      setScreen('processing')
    } catch (err: any) {
      setError(err.message || 'Failed to start review')
    } finally {
      setIsLoading(false)
    }
  }

  const handleStartSample = async () => {
    setIsLoading(true)
    setError(null)
    try {
      const res = await startSampleReview()
      setCurrentReviewId(res.review_id)
      setProgress({
        review_id: res.review_id,
        stage: 'uploading',
        percent: 5,
        message: 'Loaded sample assignment documents.',
        logs: ['Loaded CS-504 enterprise cloud migration sample specification, rubric, and student draft.'],
      })
      setScreen('processing')
    } catch (err: any) {
      setError(err.message || 'Failed to start sample review')
    } finally {
      setIsLoading(false)
    }
  }

  const handleReset = () => {
    setScreen('upload')
    setCurrentReviewId(null)
    setReview(null)
    setError(null)
  }

  return (
    <div className="min-h-screen bg-black text-neutral-100 flex flex-col antialiased selection:bg-white selection:text-black">
      
      {/* Top Header / Navigation */}
      <header className="border-b border-neutral-900 bg-black/80 backdrop-blur-md sticky top-0 z-40">
        <div className="max-w-5xl mx-auto px-4 sm:px-6 h-14 flex items-center justify-between">
          
          <div
            onClick={handleReset}
            className="flex items-center gap-2.5 cursor-pointer select-none"
          >
            <div className="w-6 h-6 rounded-md bg-white text-black flex items-center justify-center font-bold text-xs tracking-tighter">
              AI
            </div>
            <div className="flex items-baseline gap-2">
              <span className="text-sm font-semibold text-white tracking-tight">
                Assignment Reviewer
              </span>
              <span className="text-[10px] font-mono text-neutral-500 uppercase">
                Local RAG
              </span>
            </div>
          </div>

          <div className="flex items-center gap-2.5">
            {/* Active Model Indicator */}
            <div className="hidden sm:flex items-center gap-1.5 px-2.5 py-1 rounded-full border border-neutral-800 bg-neutral-950 text-[11px] font-mono text-neutral-400">
              <span className="w-1.5 h-1.5 rounded-full bg-white animate-pulse" />
              <span>{systemModel}</span>
            </div>

            {/* How It Works Trigger */}
            <button
              onClick={() => setIsHowItWorksOpen(true)}
              className="px-3 py-1.5 rounded-full border border-neutral-800 hover:border-neutral-600 bg-neutral-950 text-xs text-neutral-300 hover:text-white transition-all flex items-center gap-1.5"
            >
              <Compass className="w-3.5 h-3.5 text-neutral-400" />
              <span>How It Works</span>
            </button>


            {screen === 'dashboard' && (
              <button
                onClick={handleReset}
                className="px-3 py-1.5 rounded-full bg-white text-black text-xs font-semibold hover:bg-neutral-200 transition-colors flex items-center gap-1.5"
              >
                <RotateCcw className="w-3.5 h-3.5" />
                <span>New</span>
              </button>
            )}
          </div>

        </div>
      </header>

      {/* Main Container */}
      <main className="flex-1 max-w-5xl w-full mx-auto px-4 sm:px-6 py-8">
        {error && (
          <div className="max-w-3xl mx-auto mb-6 p-4 bg-neutral-950 border border-neutral-700 rounded-xl text-neutral-200 text-xs flex items-center justify-between gap-3">
            <span>{error}</span>
            <button
              onClick={() => setError(null)}
              className="text-[11px] font-mono text-neutral-400 hover:text-white underline"
            >
              Dismiss
            </button>
          </div>
        )}

        {screen === 'upload' && (
          <UploadSection
            onStartReview={handleStartReview}
            onStartSample={handleStartSample}
            onOpenHowItWorks={() => setIsHowItWorksOpen(true)}
            isLoading={isLoading}
          />
        )}

        {screen === 'processing' && (
          <ProcessingProgress
            progress={progress}
            onOpenHowItWorks={() => setIsHowItWorksOpen(true)}
          />
        )}

        {screen === 'dashboard' && review && (
          <Dashboard
            review={review}
            onReset={handleReset}
            onOpenHowItWorks={() => setIsHowItWorksOpen(true)}
          />
        )}
      </main>

      {/* Footer */}
      <footer className="border-t border-neutral-900 bg-black py-6 text-center text-xs text-neutral-600 font-mono">
        <div className="max-w-5xl mx-auto px-4 flex flex-col sm:flex-row items-center justify-between gap-2">
          <div className="flex items-center gap-1.5 text-neutral-500">
            <Lock className="w-3.5 h-3.5" />
            <span>Local Execution • ChromaDB • Python FastAPI</span>
          </div>
          <div>
            <span>Strict Evidence Grounding & Schema Validation</span>
          </div>
        </div>
      </footer>

      {/* Educational Walkthrough Modal */}
      <EducationalModal
        isOpen={isHowItWorksOpen}
        onClose={() => setIsHowItWorksOpen(false)}
      />

    </div>
  )
}

export default App
