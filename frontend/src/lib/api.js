// frontend/src/lib/api.js
// Helper functions for calling our FastAPI backend.
// Automatically attaches the Supabase JWT token for auth.

import { supabase } from './supabase'

const BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api'

async function authHeaders() {
  const { data: { session } } = await supabase.auth.getSession()
  if (!session) throw new Error('Not authenticated')
  return {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${session.access_token}`,
  }
}

async function get(path, params = {}) {
  const headers = await authHeaders()
  const url = new URL(BASE_URL + path, window.location.origin)
  Object.entries(params).forEach(([k, v]) => v !== undefined && url.searchParams.set(k, v))
  const res = await fetch(url.toString(), { headers })
  if (!res.ok) throw new Error(await res.text())
  return res.json()
}

async function post(path, body = {}) {
  const headers = await authHeaders()
  const res = await fetch(BASE_URL + path, {
    method: 'POST',
    headers,
    body: JSON.stringify(body),
  })
  if (!res.ok) throw new Error(await res.text())
  return res.json()
}

async function del(path) {
  const headers = await authHeaders()
  const res = await fetch(BASE_URL + path, { method: 'DELETE', headers })
  if (!res.ok) throw new Error(await res.text())
  return res.json()
}

// ── Exported API functions ────────────────────────────────────────────────────

export const api = {
  // Subjects & categories
  getSubjects: () => get('/questions/subjects'),

  // Questions
  getQuestions: (params) => get('/questions/', params),

  // Quiz sessions
  createSession: (body) => post('/quiz/sessions', body),
  submitAnswer: (sessionId, body) => post(`/quiz/sessions/${sessionId}/answers`, body),
  completeSession: (sessionId, body) => post(`/quiz/sessions/${sessionId}/complete`, body),

  // Answer reveal (used in Review Mode)
  getAnswer: (questionId) => get(`/questions/${questionId}/answer`),

  // Review state
  getReviewState: (subject_id) => get('/questions/review-state', { subject_id }),
  updateReviewState: (question_id, status) => post('/questions/review-state', { question_id, status }),
  resetReviewState: (subject_id, category_id) => post('/questions/review-state/reset', { subject_id, category_id }),

  // History
  getHistory: (params) => get('/history/', params),
  getSessionDetail: (sessionId) => get(`/history/${sessionId}`),
  clearHistory: () => del('/history/'),
}
