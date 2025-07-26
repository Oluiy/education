// src/components/quizzes/QuizCard.tsx
'use client'

import { motion } from 'framer-motion'
import Link from 'next/link'
import { Quiz } from '../../api/quizzes'
import { useAuth } from '../../contexts/AuthContext'
import {
  ClockIcon,
  QuestionMarkCircleIcon,
  TrophyIcon,
  PlayIcon,
  PencilIcon,
  DocumentTextIcon
} from '@heroicons/react/24/outline'

interface QuizCardProps {
  quiz: Quiz
  showEditButton?: boolean
  showTakeButton?: boolean
  userAttempts?: number
  bestScore?: number
}

export function QuizCard({ 
  quiz, 
  showEditButton = false, 
  showTakeButton = true,
  userAttempts = 0,
  bestScore 
}: QuizCardProps) {
  const { user } = useAuth()

  const difficultyColor = {
    1: 'bg-green-100 text-green-800',
    2: 'bg-yellow-100 text-yellow-800',
    3: 'bg-red-100 text-red-800'
  }

  const getDifficultyLevel = (questions: any[]) => {
    const avgPoints = questions.reduce((acc, q) => acc + q.points, 0) / questions.length
    if (avgPoints <= 2) return 1
    if (avgPoints <= 4) return 2
    return 3
  }

  const difficulty = getDifficultyLevel(quiz.questions)
  const hasAttemptsLeft = userAttempts < quiz.attempts

  return (
    <motion.div
      whileHover={{ y: -4 }}
      transition={{ duration: 0.2 }}
      className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden hover:shadow-lg transition-shadow"
    >
      <div className="p-6">
        <div className="flex items-start justify-between mb-4">
          <div className="flex-1">
            <div className="flex items-center space-x-2 mb-2">
              <h3 className="text-lg font-semibold text-gray-900 line-clamp-2">{quiz.title}</h3>
              {!quiz.isPublished && (
                <span className="px-2 py-1 bg-yellow-100 text-yellow-800 text-xs rounded-full">
                  Draft
                </span>
              )}
            </div>
            <p className="text-gray-600 text-sm line-clamp-2 mb-4">{quiz.description}</p>
          </div>
          
          <div className="flex-shrink-0 ml-4">
            <span className={`px-2 py-1 rounded-full text-xs font-medium ${difficultyColor[difficulty]}`}>
              {difficulty === 1 ? 'Easy' : difficulty === 2 ? 'Medium' : 'Hard'}
            </span>
          </div>
        </div>

        <div className="grid grid-cols-2 gap-4 mb-4">
          <div className="flex items-center space-x-2 text-sm text-gray-500">
            <QuestionMarkCircleIcon className="w-4 h-4" />
            <span>{quiz.questions.length} questions</span>
          </div>
          <div className="flex items-center space-x-2 text-sm text-gray-500">
            <ClockIcon className="w-4 h-4" />
            <span>{quiz.timeLimit ? `${quiz.timeLimit} min` : 'No limit'}</span>
          </div>
          <div className="flex items-center space-x-2 text-sm text-gray-500">
            <TrophyIcon className="w-4 h-4" />
            <span>{quiz.passingScore}% to pass</span>
          </div>
          <div className="flex items-center space-x-2 text-sm text-gray-500">
            <DocumentTextIcon className="w-4 h-4" />
            <span>{quiz.attempts} attempts</span>
          </div>
        </div>

        {/* User Progress */}
        {bestScore !== undefined && (
          <div className="mb-4 p-3 bg-gray-50 rounded-lg">
            <div className="flex justify-between items-center mb-2">
              <span className="text-sm font-medium text-gray-700">Your Best Score</span>
              <span className={`text-sm font-bold ${bestScore >= quiz.passingScore ? 'text-green-600' : 'text-red-600'}`}>
                {bestScore}%
              </span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-2">
              <div 
                className={`h-2 rounded-full transition-all duration-300 ${
                  bestScore >= quiz.passingScore ? 'bg-green-600' : 'bg-red-600'
                }`}
                style={{ width: `${bestScore}%` }}
              />
            </div>
            <div className="flex justify-between items-center mt-2 text-xs text-gray-500">
              <span>Attempts: {userAttempts}/{quiz.attempts}</span>
              <span>{bestScore >= quiz.passingScore ? 'Passed' : 'Not passed'}</span>
            </div>
          </div>
        )}

        {/* Action Buttons */}
        <div className="flex items-center justify-between">
          <div className="text-sm text-gray-500">
            {quiz.courseId && (
              <span>Course: {quiz.courseId}</span>
            )}
          </div>

          <div className="flex items-center space-x-2">
            {showEditButton && user?.role === 'teacher' && (
              <Link href={`/quizzes/${quiz.id}/edit`}>
                <button className="flex items-center space-x-1 px-3 py-1 text-sm text-blue-600 hover:text-blue-700 border border-blue-200 rounded-lg hover:bg-blue-50 transition-colors">
                  <PencilIcon className="w-4 h-4" />
                  <span>Edit</span>
                </button>
              </Link>
            )}

            {showTakeButton && user?.role === 'student' && quiz.isPublished && (
              <Link href={`/quizzes/${quiz.id}/take`}>
                <button 
                  disabled={!hasAttemptsLeft}
                  className="flex items-center space-x-1 px-4 py-2 text-sm font-medium text-white bg-primary-600 hover:bg-primary-700 rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  <PlayIcon className="w-4 h-4" />
                  <span>
                    {userAttempts === 0 ? 'Take Quiz' : hasAttemptsLeft ? 'Retake' : 'No attempts left'}
                  </span>
                </button>
              </Link>
            )}

            {user?.role === 'teacher' && (
              <Link href={`/quizzes/${quiz.id}/results`}>
                <button className="flex items-center space-x-1 px-3 py-1 text-sm text-green-600 hover:text-green-700 border border-green-200 rounded-lg hover:bg-green-50 transition-colors">
                  <TrophyIcon className="w-4 h-4" />
                  <span>Results</span>
                </button>
              </Link>
            )}
          </div>
        </div>
      </div>
    </motion.div>
  )
}
