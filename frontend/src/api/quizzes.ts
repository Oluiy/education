// src/api/quizzes.ts
export interface Quiz {
  id: string
  title: string
  description: string
  courseId?: string
  createdBy: string
  timeLimit?: number
  attempts: number
  passingScore: number
  isPublished: boolean
  createdAt: string
  updatedAt: string
  questions: Question[]
  randomizeQuestions?: boolean
  showResults?: boolean
}

export interface Question {
  id: string
  type: 'multiple-choice' | 'true-false' | 'short-answer' | 'essay'
  question: string
  options?: string[]
  correctAnswer: string | string[]
  points: number
  explanation?: string
  order: number
}

export interface QuizAttempt {
  id: string
  quizId: string
  userId: string
  startedAt: string
  completedAt?: string
  submittedAt?: string
  gradedAt?: string
  timeSpent: number
  score: number
  percentage: number
  passed: boolean
  answers: Answer[]
  correctAnswers?: number
  totalPoints?: number
}

export interface Answer {
  questionId: string
  answer: string | string[]
  isCorrect: boolean
  points: number
}

export interface QuizResult {
  attempt: QuizAttempt
  quiz: Quiz
  correctAnswers: number
  totalQuestions: number
  timeSpent: number
  feedback: string
}

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

export async function getQuizzes(params?: {
  courseId?: string
  search?: string
  page?: number
  limit?: number
}): Promise<{ quizzes: Quiz[]; total: number; page: number; limit: number }> {
  const token = localStorage.getItem('auth_token')
  const searchParams = new URLSearchParams()
  
  if (params) {
    Object.entries(params).forEach(([key, value]) => {
      if (value !== undefined) searchParams.append(key, value.toString())
    })
  }

  const response = await fetch(`${API_URL}/quizzes?${searchParams}`, {
    headers: { 'Authorization': `Bearer ${token}` }
  })
  if (!response.ok) throw new Error('Failed to fetch quizzes')
  return response.json()
}

export async function getQuiz(id: string): Promise<Quiz> {
  const token = localStorage.getItem('auth_token')
  const response = await fetch(`${API_URL}/quizzes/${id}`, {
    headers: { 'Authorization': `Bearer ${token}` }
  })
  if (!response.ok) throw new Error('Failed to fetch quiz')
  return response.json()
}

export async function createQuiz(data: Partial<Quiz>): Promise<Quiz> {
  const token = localStorage.getItem('auth_token')
  const response = await fetch(`${API_URL}/quizzes`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`
    },
    body: JSON.stringify(data)
  })
  if (!response.ok) throw new Error('Failed to create quiz')
  return response.json()
}

export async function updateQuiz(id: string, data: Partial<Quiz>): Promise<Quiz> {
  const token = localStorage.getItem('auth_token')
  const response = await fetch(`${API_URL}/quizzes/${id}`, {
    method: 'PUT',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`
    },
    body: JSON.stringify(data)
  })
  if (!response.ok) throw new Error('Failed to update quiz')
  return response.json()
}

export async function deleteQuiz(id: string): Promise<void> {
  const token = localStorage.getItem('auth_token')
  const response = await fetch(`${API_URL}/quizzes/${id}`, {
    method: 'DELETE',
    headers: { 'Authorization': `Bearer ${token}` }
  })
  if (!response.ok) throw new Error('Failed to delete quiz')
}

export async function startQuizAttempt(quizId: string): Promise<QuizAttempt> {
  const token = localStorage.getItem('auth_token')
  const response = await fetch(`${API_URL}/quizzes/${quizId}/attempts`, {
    method: 'POST',
    headers: { 'Authorization': `Bearer ${token}` }
  })
  if (!response.ok) throw new Error('Failed to start quiz attempt')
  return response.json()
}

export async function submitQuizAttempt(attemptId: string, answers: Answer[]): Promise<QuizResult> {
  const token = localStorage.getItem('auth_token')
  const response = await fetch(`${API_URL}/quiz-attempts/${attemptId}/submit`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`
    },
    body: JSON.stringify({ answers })
  })
  if (!response.ok) throw new Error('Failed to submit quiz')
  return response.json()
}

export async function getQuizAttempts(quizId: string): Promise<QuizAttempt[]> {
  const token = localStorage.getItem('auth_token')
  const response = await fetch(`${API_URL}/quizzes/${quizId}/attempts`, {
    headers: { 'Authorization': `Bearer ${token}` }
  })
  if (!response.ok) throw new Error('Failed to fetch quiz attempts')
  return response.json()
}

export async function getUserQuizAttempts(userId?: string, quizId?: string): Promise<QuizAttempt[]> {
  const token = localStorage.getItem('auth_token')
  const params = new URLSearchParams()
  if (userId) params.append('userId', userId)
  if (quizId) params.append('quizId', quizId)
  
  const url = `${API_URL}/quiz-attempts${params.toString() ? `?${params.toString()}` : ''}`
  const response = await fetch(url, {
    headers: { 'Authorization': `Bearer ${token}` }
  })
  if (!response.ok) throw new Error('Failed to fetch user quiz attempts')
  return response.json()
}

// Additional API methods needed by useApi hooks
export async function publishQuiz(id: string): Promise<Quiz> {
  const token = localStorage.getItem('auth_token')
  const response = await fetch(`${API_URL}/quizzes/${id}/publish`, {
    method: 'POST',
    headers: { 'Authorization': `Bearer ${token}` }
  })
  if (!response.ok) throw new Error('Failed to publish quiz')
  return response.json()
}

export async function submitQuiz(quizId: string, answers: any[]): Promise<QuizAttempt> {
  const token = localStorage.getItem('auth_token')
  const response = await fetch(`${API_URL}/quizzes/${quizId}/submit`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`
    },
    body: JSON.stringify({ answers })
  })
  if (!response.ok) throw new Error('Failed to submit quiz')
  return response.json()
}

export async function getQuizStats(quizId: string): Promise<any> {
  const token = localStorage.getItem('auth_token')
  const response = await fetch(`${API_URL}/quizzes/${quizId}/stats`, {
    headers: { 'Authorization': `Bearer ${token}` }
  })
  if (!response.ok) throw new Error('Failed to fetch quiz stats')
  return response.json()
}

export async function getUserQuizStats(userId: string): Promise<any> {
  const token = localStorage.getItem('auth_token')
  const response = await fetch(`${API_URL}/users/${userId}/quiz-stats`, {
    headers: { 'Authorization': `Bearer ${token}` }
  })
  if (!response.ok) throw new Error('Failed to fetch user quiz stats')
  return response.json()
}

export async function exportQuizResults(quizId: string): Promise<any> {
  const token = localStorage.getItem('auth_token')
  const response = await fetch(`${API_URL}/quizzes/${quizId}/export`, {
    headers: { 'Authorization': `Bearer ${token}` }
  })
  if (!response.ok) throw new Error('Failed to export quiz results')
  return response.json()
}

export async function getQuizSubmission(submissionId: string): Promise<any> {
  const token = localStorage.getItem('auth_token')
  const response = await fetch(`${API_URL}/quiz-submissions/${submissionId}`, {
    headers: { 'Authorization': `Bearer ${token}` }
  })
  if (!response.ok) throw new Error('Failed to fetch quiz submission')
  return response.json()
}
