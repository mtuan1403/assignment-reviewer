import type { OverallReview, ProgressStatus, DocumentChunk } from '../types'

const API_BASE = '/api'

export async function checkHealth() {
  const res = await fetch(`${API_BASE}/health`)
  if (!res.ok) throw new Error('Health check failed')
  return res.json()
}

export async function startReview(
  specFile: File,
  rubricFile: File | null,
  draftFile: File
): Promise<{ review_id: string; message: string }> {
  const formData = new FormData()
  formData.append('spec_file', specFile)
  if (rubricFile) {
    formData.append('rubric_file', rubricFile)
  }
  formData.append('draft_file', draftFile)

  const res = await fetch(`${API_BASE}/reviews/start`, {
    method: 'POST',
    body: formData,
  })

  if (!res.ok) {
    const err = await res.json().catch(() => ({}))
    throw new Error(err.detail || err.message || 'Failed to start review')
  }

  return res.json()
}

export async function startSampleReview(): Promise<{ review_id: string; message: string }> {
  const res = await fetch(`${API_BASE}/reviews/sample`, {
    method: 'POST',
  })

  if (!res.ok) {
    const err = await res.json().catch(() => ({}))
    throw new Error(err.detail || err.message || 'Failed to start sample review')
  }

  return res.json()
}

export async function getReviewProgress(reviewId: string): Promise<ProgressStatus> {
  const res = await fetch(`${API_BASE}/reviews/${reviewId}/progress`)
  if (!res.ok) {
    throw new Error(`Failed to fetch progress for review ${reviewId}`)
  }
  return res.json()
}

export async function getReview(reviewId: string): Promise<OverallReview> {
  const res = await fetch(`${API_BASE}/reviews/${reviewId}`)
  if (!res.ok) {
    const err = await res.json().catch(() => ({}))
    throw new Error(err.detail || 'Review is still processing or not found')
  }
  return res.json()
}

export async function getReviewChunks(
  reviewId: string
): Promise<{ review_id: string; total_chunks: number; chunks: DocumentChunk[] }> {
  const res = await fetch(`${API_BASE}/reviews/${reviewId}/chunks`)
  if (!res.ok) throw new Error('Failed to fetch chunks')
  return res.json()
}
