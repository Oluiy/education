// src/app/quizzes/[id]/results/page.tsx
'use client'

import { useParams, useSearchParams } from 'next/navigation'
import { useApi } from '../../../../hooks/useApi'
import { useAuth } from '../../../../contexts/AuthContext'
import { QuizResults } from '../../../../components/quizzes/QuizResults'
import { LoadingSpinner } from '../../../../components/ui/LoadingSpinner'
import { ErrorBoundary } from '../../../../components/ui/ErrorBoundary'

export default function QuizResultsPage() {
  const params = useParams()
  const searchParams = useSearchParams()
  const { user } = useAuth()
  
  const quizId = params.id as string
  const submissionId = searchParams.get('submission')
  const attemptId = searchParams.get('attempt')

  const { 
    useQuiz, 
    useQuizSubmission,
    useUserQuizAttempts,
    useQuizAttempts
  } = useApi()

  const { data: quiz, isLoading: quizLoading } = useQuiz(quizId ?? '')
  const { data: submission } = useQuizSubmission(submissionId ?? undefined)
  const { data: userAttempts } = useUserQuizAttempts(user?.id ?? '', quizId ?? '')
  const { data: allAttempts } = useQuizAttempts(quizId ?? '')

  const isTeacherView = user?.role === 'teacher' || user?.role === 'admin'
  const attempts = isTeacherView ? allAttempts : userAttempts

  if (quizLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <LoadingSpinner size="lg" />
      </div>
    )
  }

  if (!quiz) {
    return (
      <ErrorBoundary>
        <div className="text-center py-12">
          <p className="text-red-600">Quiz not found</p>
        </div>
      </ErrorBoundary>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <QuizResults
        quiz={quiz}
        submission={submission}
        attempts={attempts}
        showAllAttempts={user?.role === 'student'}
        isTeacherView={isTeacherView}
      />
    </div>
  )
}
