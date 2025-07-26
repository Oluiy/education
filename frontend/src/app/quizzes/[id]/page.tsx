// src/app/quizzes/[id]/page.tsx
'use client'

import { useState } from 'react'
import { useParams, useRouter } from 'next/navigation'
import { motion } from 'framer-motion'
import { useApi } from '../../../hooks/useApi'
import { useAuth } from '../../../contexts/AuthContext'
import { QuizCard } from '../../../components/quizzes/QuizCard'
import { LoadingSpinner } from '../../../components/ui/LoadingSpinner'
import { ErrorBoundary } from '../../../components/ui/ErrorBoundary'
import Link from 'next/link'
import {
  PlayIcon,
  PencilIcon,
  TrophyIcon,
  ClockIcon,
  UserGroupIcon,
  ChartBarIcon,
  ArrowLeftIcon
} from '@heroicons/react/24/outline'

export default function QuizDetailPage() {
  const params = useParams()
  const router = useRouter()
  const { user } = useAuth()
  const quizId = params.id as string

  const { 
    useQuiz, 
    useQuizAttempts, 
    useQuizStats,
    useUserQuizAttempts 
  } = useApi()

  const { data: quiz, isLoading: quizLoading, error: quizError } = useQuiz(quizId ?? '')
  const { data: quizStats } = useQuizStats(quizId ?? '')
  const { data: userAttempts } = useUserQuizAttempts(user?.id ?? '', quizId ?? '')

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
          <p className="text-red-600">Quiz not found</p>
          <Link href="/quizzes" className="text-blue-600 hover:text-blue-700 mt-4 inline-block">
            ← Back to Quizzes
          </Link>
        </div>
      </ErrorBoundary>
    )
  }

  const userBestScore = (userAttempts ?? []).length > 0 
    ? Math.max(...(userAttempts ?? []).map(a => a.score)) 
    : undefined
  
  const canTakeQuiz = user?.role === 'student' && 
    quiz.isPublished && 
    ((userAttempts ?? []).length) < quiz.attempts

  const hasPassedQuiz = userBestScore !== undefined && userBestScore >= quiz.passingScore

  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* Navigation */}
      <div className="mb-6">
        <Link 
          href="/quizzes"
          className="flex items-center space-x-2 text-gray-600 hover:text-gray-800"
        >
          <ArrowLeftIcon className="w-4 h-4" />
          <span>Back to Quizzes</span>
        </Link>
      </div>

      {/* Quiz Header */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="bg-white rounded-xl shadow-lg p-8 mb-8"
      >
        <div className="flex items-start justify-between mb-6">
          <div className="flex-1">
            <div className="flex items-center space-x-3 mb-2">
              <h1 className="text-3xl font-bold text-gray-900">{quiz.title}</h1>
              {!quiz.isPublished && (
                <span className="px-3 py-1 bg-yellow-100 text-yellow-800 text-sm rounded-full">
                  Draft
                </span>
              )}
            </div>
            <p className="text-gray-600 text-lg mb-6">{quiz.description}</p>
          </div>

          {/* Action Buttons */}
          <div className="flex items-center space-x-3">
            {user?.role === 'teacher' && (
              <Link href={`/quizzes/${quiz.id}/edit`}>
                <button className="flex items-center space-x-2 px-4 py-2 text-blue-600 border border-blue-200 rounded-lg hover:bg-blue-50">
                  <PencilIcon className="w-4 h-4" />
                  <span>Edit</span>
                </button>
              </Link>
            )}

            {canTakeQuiz && (
              <Link href={`/quizzes/${quiz.id}/take`}>
                <button className="flex items-center space-x-2 px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700">
                  <PlayIcon className="w-4 h-4" />
                  <span>
                    {userAttempts?.length === 0 ? 'Take Quiz' : 'Retake Quiz'}
                  </span>
                </button>
              </Link>
            )}

            {user?.role === 'teacher' && (
              <Link href={`/quizzes/${quiz.id}/results`}>
                <button className="flex items-center space-x-2 px-4 py-2 text-green-600 border border-green-200 rounded-lg hover:bg-green-50">
                  <TrophyIcon className="w-4 h-4" />
                  <span>View Results</span>
                </button>
              </Link>
            )}
          </div>
        </div>

        {/* Quiz Stats */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
          <div className="text-center p-4 bg-gray-50 rounded-lg">
            <div className="text-2xl font-bold text-gray-900">{quiz.questions.length}</div>
            <div className="text-sm text-gray-600">Questions</div>
          </div>
          
          <div className="text-center p-4 bg-gray-50 rounded-lg">
            <div className="text-2xl font-bold text-gray-900">
              {quiz.timeLimit ? `${quiz.timeLimit} min` : 'No limit'}
            </div>
            <div className="text-sm text-gray-600">Time Limit</div>
          </div>
          
          <div className="text-center p-4 bg-gray-50 rounded-lg">
            <div className="text-2xl font-bold text-gray-900">{quiz.passingScore}%</div>
            <div className="text-sm text-gray-600">To Pass</div>
          </div>
          
          <div className="text-center p-4 bg-gray-50 rounded-lg">
            <div className="text-2xl font-bold text-gray-900">{quiz.attempts}</div>
            <div className="text-sm text-gray-600">Attempts</div>
          </div>
        </div>
      </motion.div>

      {/* User Progress (Students) */}
      {user?.role === 'student' && userAttempts && userAttempts.length > 0 && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="bg-white rounded-xl shadow-lg p-6 mb-8"
        >
          <h2 className="text-xl font-semibold text-gray-900 mb-4">Your Progress</h2>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
            <div className="text-center p-4 bg-blue-50 rounded-lg">
              <div className="text-2xl font-bold text-blue-600">{userAttempts.length}</div>
              <div className="text-sm text-blue-800">Attempts Made</div>
              <div className="text-xs text-blue-600">out of {quiz.attempts}</div>
            </div>
            
            <div className="text-center p-4 bg-green-50 rounded-lg">
              <div className={`text-2xl font-bold ${userBestScore! >= quiz.passingScore ? 'text-green-600' : 'text-red-600'}`}>
                {userBestScore}%
              </div>
              <div className="text-sm text-gray-600">Best Score</div>
              <div className={`text-xs ${userBestScore! >= quiz.passingScore ? 'text-green-600' : 'text-red-600'}`}>
                {userBestScore! >= quiz.passingScore ? 'Passed' : 'Not passed'}
              </div>
            </div>
            
            <div className="text-center p-4 bg-purple-50 rounded-lg">
              <div className="text-2xl font-bold text-purple-600">
                {userAttempts[userAttempts.length - 1]?.timeSpent || 0}s
              </div>
              <div className="text-sm text-purple-800">Last Attempt Time</div>
            </div>
          </div>

          {/* Attempt History */}
          <div className="space-y-3">
            <h3 className="font-medium text-gray-900">Attempt History</h3>
            {userAttempts.map((attempt, index) => (
              <div key={attempt.id} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                <div className="flex items-center space-x-4">
                  <span className="text-sm font-medium text-gray-900">
                    Attempt {index + 1}
                  </span>
                  <span className={`text-sm font-medium ${
                    attempt.score >= quiz.passingScore ? 'text-green-600' : 'text-red-600'
                  }`}>
                    {attempt.score}%
                  </span>
                </div>
                
                <div className="flex items-center space-x-4 text-sm text-gray-600">
                  <span>{new Date(attempt.submittedAt ?? attempt.completedAt ?? attempt.startedAt).toLocaleDateString()}</span>
                  <Link 
                    href={`/quizzes/${quiz.id}/results?attempt=${attempt.id}`}
                    className="text-blue-600 hover:text-blue-700"
                  >
                    View Details
                  </Link>
                </div>
              </div>
            ))}
          </div>

          {/* Next Attempt */}
          {canTakeQuiz && (
            <div className="mt-6 p-4 bg-blue-50 border border-blue-200 rounded-lg">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-blue-800 font-medium">Ready for another attempt?</p>
                  <p className="text-blue-600 text-sm">
                    You have {quiz.attempts - userAttempts.length} attempt{quiz.attempts - userAttempts.length !== 1 ? 's' : ''} remaining
                  </p>
                </div>
                <Link href={`/quizzes/${quiz.id}/take`}>
                  <button className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700">
                    Take Quiz
                  </button>
                </Link>
              </div>
            </div>
          )}

          {!canTakeQuiz && !hasPassedQuiz && (
            <div className="mt-6 p-4 bg-red-50 border border-red-200 rounded-lg">
              <p className="text-red-800 font-medium">No more attempts available</p>
              <p className="text-red-600 text-sm">
                You have used all {quiz.attempts} attempts for this quiz.
              </p>
            </div>
          )}
        </motion.div>
      )}

      {/* Quiz Overview (Teachers) */}
      {user?.role === 'teacher' && quizStats && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="bg-white rounded-xl shadow-lg p-6 mb-8"
        >
          <h2 className="text-xl font-semibold text-gray-900 mb-4">Quiz Statistics</h2>
          
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
            <div className="text-center p-4 bg-blue-50 rounded-lg">
              <div className="flex items-center justify-center mb-2">
                <UserGroupIcon className="w-6 h-6 text-blue-600" />
              </div>
              <div className="text-2xl font-bold text-blue-600">{quizStats.totalAttempts}</div>
              <div className="text-sm text-blue-800">Total Attempts</div>
            </div>
            
            <div className="text-center p-4 bg-green-50 rounded-lg">
              <div className="flex items-center justify-center mb-2">
                <TrophyIcon className="w-6 h-6 text-green-600" />
              </div>
              <div className="text-2xl font-bold text-green-600">{quizStats.passRate}%</div>
              <div className="text-sm text-green-800">Pass Rate</div>
            </div>
            
            <div className="text-center p-4 bg-yellow-50 rounded-lg">
              <div className="flex items-center justify-center mb-2">
                <ChartBarIcon className="w-6 h-6 text-yellow-600" />
              </div>
              <div className="text-2xl font-bold text-yellow-600">{quizStats.averageScore}%</div>
              <div className="text-sm text-yellow-800">Average Score</div>
            </div>
            
            <div className="text-center p-4 bg-purple-50 rounded-lg">
              <div className="flex items-center justify-center mb-2">
                <ClockIcon className="w-6 h-6 text-purple-600" />
              </div>
              <div className="text-2xl font-bold text-purple-600">{quizStats.averageTime}m</div>
              <div className="text-sm text-purple-800">Avg. Time</div>
            </div>
          </div>
        </motion.div>
      )}

      {/* Question Preview */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2 }}
        className="bg-white rounded-xl shadow-lg p-6"
      >
        <h2 className="text-xl font-semibold text-gray-900 mb-6">Question Overview</h2>
        
        <div className="space-y-4">
          {quiz.questions.slice(0, 3).map((question, index) => (
            <div key={question.id} className="p-4 border border-gray-200 rounded-lg">
              <div className="flex items-start justify-between mb-2">
                <h3 className="font-medium text-gray-900">Question {index + 1}</h3>
                <span className="text-sm text-gray-500 capitalize">
                  {question.type.replace('-', ' ')} • {question.points} pts
                </span>
              </div>
              <p className="text-gray-700 line-clamp-2">{question.question}</p>
            </div>
          ))}
          
          {quiz.questions.length > 3 && (
            <div className="text-center py-4">
              <p className="text-gray-500">
                And {quiz.questions.length - 3} more question{quiz.questions.length - 3 !== 1 ? 's' : ''}...
              </p>
            </div>
          )}
        </div>
      </motion.div>
    </div>
  )
}
