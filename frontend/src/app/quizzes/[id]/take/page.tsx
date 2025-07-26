// src/app/quizzes/[id]/take/page.tsx
'use client'

import { useParams, useRouter } from 'next/navigation'
import { useApi } from '../../../../hooks/useApi'
import { useAuth } from '../../../../contexts/AuthContext'
import { QuizTaker } from '../../../../components/quizzes/QuizTaker'
import { LoadingSpinner } from '../../../../components/ui/LoadingSpinner'
import { ErrorBoundary } from '../../../../components/ui/ErrorBoundary'
import { useEffect } from 'react'

export default function TakeQuizPage() {
  const params = useParams()
  const router = useRouter()
  const { user } = useAuth()
  const quizId = params.id as string

  const { 
    useQuiz, 
    useUserQuizAttempts 
  } = useApi()

  const { data: quiz, isLoading: quizLoading, error: quizError } = useQuiz(quizId ?? '')
  const { data: userAttempts } = useUserQuizAttempts(user?.id ?? '', quizId ?? '')

  // Check permissions
  useEffect(() => {
    if (quiz && user) {
      if (user.role !== 'student') {
        router.push(`/quizzes/${quizId}`)
        return
      }

      if (!quiz.isPublished) {
        router.push(`/quizzes/${quizId}`)
        return
      }

      if (userAttempts && userAttempts.length >= quiz.attempts) {
        router.push(`/quizzes/${quizId}`)
        return
      }
    }
  }, [quiz, user, userAttempts, quizId, router])

  if (quizLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <LoadingSpinner size="lg" />
      </div>
    )
  }

  if (quizError || !quiz) {
    return (
      <ErrorBoundary>
        <div className="text-center py-12">
          <p className="text-red-600">Quiz not found or not available</p>
        </div>
      </ErrorBoundary>
    )
  }

  const handleComplete = (submission: any) => {
    router.push(`/quizzes/${quizId}/results?submission=${submission.id}`)
  }

  const handleExit = () => {
    router.push(`/quizzes/${quizId}`)
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <QuizTaker
        quiz={quiz}
        onComplete={handleComplete}
        onExit={handleExit}
      />
    </div>
  )
}
