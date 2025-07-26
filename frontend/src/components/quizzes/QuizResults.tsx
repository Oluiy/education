// src/components/quizzes/QuizResults.tsx
'use client'

import { useState } from 'react'
import { motion } from 'framer-motion'
import { Quiz, Question, QuizAttempt, Answer } from '../../api/quizzes'
import { useApi } from '../../hooks/useApi'
import {
  TrophyIcon,
  CheckCircleIcon,
  XCircleIcon,
  ClockIcon,
  CalendarIcon,
  UserIcon,
  ChartBarIcon,
  AcademicCapIcon,
  ArrowDownTrayIcon
} from '@heroicons/react/24/outline'

interface QuizResultsProps {
  quiz: Quiz
  submission?: QuizAttempt
  attempts?: QuizAttempt[]
  showAllAttempts?: boolean
  isTeacherView?: boolean
}

export function QuizResults({ 
  quiz, 
  submission, 
  attempts = [], 
  showAllAttempts = false,
  isTeacherView = false 
}: QuizResultsProps) {
  const [selectedAttempt, setSelectedAttempt] = useState<QuizAttempt | null>(null)
  const [showDetails, setShowDetails] = useState(false)

  // const { useApi } = require('../../hooks/useApi')
  // const exportMutation = useApi().exportQuizResults(quiz.id)

  const latestAttempt = attempts.length > 0 ? attempts[attempts.length - 1] : null
  const bestAttempt = attempts.reduce((best, current) => 
    current.score > (best?.score || 0) ? current : best, null as QuizAttempt | null
  )

  const currentSubmission = submission || latestAttempt
  const isPassed = currentSubmission && currentSubmission.score >= quiz.passingScore
  
  const getScoreColor = (score: number) => {
    if (score >= quiz.passingScore) return 'text-green-600'
    if (score >= quiz.passingScore * 0.7) return 'text-yellow-600'
    return 'text-red-600'
  }

  const getGradeLetter = (score: number) => {
    if (score >= 97) return 'A+'
    if (score >= 93) return 'A'
    if (score >= 90) return 'A-'
    if (score >= 87) return 'B+'
    if (score >= 83) return 'B'
    if (score >= 80) return 'B-'
    if (score >= 77) return 'C+'
    if (score >= 73) return 'C'
    if (score >= 70) return 'C-'
    if (score >= 67) return 'D+'
    if (score >= 60) return 'D'
    return 'F'
  }

  const formatDuration = (seconds: number) => {
    const hours = Math.floor(seconds / 3600)
    const minutes = Math.floor((seconds % 3600) / 60)
    const remainingSeconds = seconds % 60

    if (hours > 0) {
      return `${hours}h ${minutes}m ${remainingSeconds}s`
    } else if (minutes > 0) {
      return `${minutes}m ${remainingSeconds}s`
    } else {
      return `${remainingSeconds}s`
    }
  }

  const handleExportResults = async () => {
    try {
      // Export functionality to be implemented
      console.log('Export functionality not implemented yet')
    } catch (error) {
      console.error('Failed to export results:', error)
    }
  }

  if (!currentSubmission) {
    return (
      <div className="max-w-2xl mx-auto text-center py-12">
        <AcademicCapIcon className="w-16 h-16 mx-auto text-gray-300 mb-4" />
        <h2 className="text-2xl font-bold text-gray-900 mb-2">No Results Available</h2>
        <p className="text-gray-600">No quiz attempts found for this quiz.</p>
      </div>
    )
  }

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      {/* Overall Results */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="bg-white rounded-xl shadow-lg p-8"
      >
        <div className="text-center mb-8">
          <div className={`inline-flex items-center justify-center w-20 h-20 rounded-full mb-4 ${
            isPassed ? 'bg-green-100' : 'bg-red-100'
          }`}>
            {isPassed ? (
              <TrophyIcon className="w-10 h-10 text-green-600" />
            ) : (
              <XCircleIcon className="w-10 h-10 text-red-600" />
            )}
          </div>
          
          <h1 className="text-3xl font-bold text-gray-900 mb-2">{quiz.title}</h1>
          
          <div className="flex items-center justify-center space-x-4 text-lg">
            <span className={`font-bold ${getScoreColor(currentSubmission.score)}`}>
              {currentSubmission.score}%
            </span>
            <span className="text-gray-300">•</span>
            <span className={`font-bold ${getScoreColor(currentSubmission.score)}`}>
              {getGradeLetter(currentSubmission.score)}
            </span>
            <span className="text-gray-300">•</span>
            <span className={isPassed ? 'text-green-600' : 'text-red-600'}>
              {isPassed ? 'PASSED' : 'FAILED'}
            </span>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <div className="text-center p-4 bg-gray-50 rounded-lg">
            <div className="text-2xl font-bold text-gray-900">{currentSubmission.correctAnswers}</div>
            <div className="text-sm text-gray-600">Correct Answers</div>
            <div className="text-xs text-gray-500">out of {quiz.questions.length}</div>
          </div>
          
          <div className="text-center p-4 bg-gray-50 rounded-lg">
            <div className="text-2xl font-bold text-gray-900">
              {currentSubmission.totalPoints || quiz.questions.reduce((sum, q) => sum + q.points, 0)}
            </div>
            <div className="text-sm text-gray-600">Points Earned</div>
            <div className="text-xs text-gray-500">
              out of {quiz.questions.reduce((sum, q) => sum + q.points, 0)}
            </div>
          </div>
          
          <div className="text-center p-4 bg-gray-50 rounded-lg">
            <div className="text-2xl font-bold text-gray-900">
              {currentSubmission.timeSpent ? formatDuration(currentSubmission.timeSpent) : 'N/A'}
            </div>
            <div className="text-sm text-gray-600">Time Spent</div>
            {quiz.timeLimit && (
              <div className="text-xs text-gray-500">
                limit: {quiz.timeLimit} min
              </div>
            )}
          </div>
        </div>

        <div className="flex items-center justify-center space-x-6 text-sm text-gray-600">
          <div className="flex items-center space-x-2">
            <CalendarIcon className="w-4 h-4" />
            <span>Submitted: {currentSubmission.submittedAt ? new Date(currentSubmission.submittedAt).toLocaleString() : 'Not submitted'}</span>
          </div>
          {currentSubmission.gradedAt && (
            <div className="flex items-center space-x-2">
              <CheckCircleIcon className="w-4 h-4" />
              <span>Graded: {new Date(currentSubmission.gradedAt).toLocaleString()}</span>
            </div>
          )}
        </div>
      </motion.div>

      {/* Attempt History */}
      {showAllAttempts && attempts.length > 1 && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="bg-white rounded-xl shadow-lg p-6"
        >
          <h2 className="text-xl font-semibold text-gray-900 mb-4">Attempt History</h2>
          
          <div className="space-y-3">
            {attempts.map((attempt, index) => (
              <div
                key={attempt.id}
                className={`p-4 rounded-lg border transition-colors cursor-pointer ${
                  selectedAttempt?.id === attempt.id
                    ? 'border-blue-500 bg-blue-50'
                    : 'border-gray-200 hover:bg-gray-50'
                }`}
                onClick={() => setSelectedAttempt(selectedAttempt?.id === attempt.id ? null : attempt)}
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-4">
                    <span className="font-medium text-gray-900">
                      Attempt {index + 1}
                    </span>
                    {attempt === bestAttempt && (
                      <span className="px-2 py-1 bg-yellow-100 text-yellow-800 text-xs rounded-full">
                        Best Score
                      </span>
                    )}
                    {attempt === latestAttempt && (
                      <span className="px-2 py-1 bg-blue-100 text-blue-800 text-xs rounded-full">
                        Latest
                      </span>
                    )}
                  </div>
                  
                  <div className="flex items-center space-x-4 text-sm">
                    <span className={`font-medium ${getScoreColor(attempt.score)}`}>
                      {attempt.score}%
                    </span>
                    <span className="text-gray-500">
                      {attempt.submittedAt ? new Date(attempt.submittedAt).toLocaleDateString() : 'Not submitted'}
                    </span>
                  </div>
                </div>

                {selectedAttempt?.id === attempt.id && (
                  <motion.div
                    initial={{ opacity: 0, height: 0 }}
                    animate={{ opacity: 1, height: 'auto' }}
                    exit={{ opacity: 0, height: 0 }}
                    className="mt-4 pt-4 border-t border-gray-200"
                  >
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                      <div>
                        <span className="text-gray-600">Score:</span>
                        <span className={`ml-2 font-medium ${getScoreColor(attempt.score)}`}>
                          {attempt.score}%
                        </span>
                      </div>
                      <div>
                        <span className="text-gray-600">Correct:</span>
                        <span className="ml-2 font-medium text-gray-900">
                          {attempt.correctAnswers}/{quiz.questions.length}
                        </span>
                      </div>
                      <div>
                        <span className="text-gray-600">Time:</span>
                        <span className="ml-2 font-medium text-gray-900">
                          {attempt.timeSpent ? formatDuration(attempt.timeSpent) : 'N/A'}
                        </span>
                      </div>
                      <div>
                        <span className="text-gray-600">Status:</span>
                        <span className={`ml-2 font-medium ${
                          attempt.score >= quiz.passingScore ? 'text-green-600' : 'text-red-600'
                        }`}>
                          {attempt.score >= quiz.passingScore ? 'Passed' : 'Failed'}
                        </span>
                      </div>
                    </div>
                  </motion.div>
                )}
              </div>
            ))}
          </div>
        </motion.div>
      )}

      {/* Question Breakdown */}
      {quiz.showResults && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="bg-white rounded-xl shadow-lg p-6"
        >
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-xl font-semibold text-gray-900">Question Breakdown</h2>
            <button
              onClick={() => setShowDetails(!showDetails)}
              className="text-blue-600 hover:text-blue-700 text-sm font-medium"
            >
              {showDetails ? 'Hide Details' : 'Show Details'}
            </button>
          </div>

          <div className="space-y-4">
            {quiz.questions.map((question, index) => {
              const userAnswer = currentSubmission.answers.find(a => a.questionId === question.id)?.answer
              const isCorrect = userAnswer === question.correctAnswer
              
              return (
                <div
                  key={question.id}
                  className={`p-4 rounded-lg border ${
                    isCorrect ? 'border-green-200 bg-green-50' : 'border-red-200 bg-red-50'
                  }`}
                >
                  <div className="flex items-start justify-between mb-2">
                    <div className="flex items-center space-x-3">
                      <div className={`w-6 h-6 rounded-full flex items-center justify-center ${
                        isCorrect ? 'bg-green-600' : 'bg-red-600'
                      }`}>
                        {isCorrect ? (
                          <CheckCircleIcon className="w-4 h-4 text-white" />
                        ) : (
                          <XCircleIcon className="w-4 h-4 text-white" />
                        )}
                      </div>
                      <span className="font-medium text-gray-900">
                        Question {index + 1}
                      </span>
                      <span className="text-sm text-gray-600">
                        ({question.points} point{question.points !== 1 ? 's' : ''})
                      </span>
                    </div>
                    
                    <span className={`text-sm font-medium ${
                      isCorrect ? 'text-green-600' : 'text-red-600'
                    }`}>
                      {isCorrect ? 'Correct' : 'Incorrect'}
                    </span>
                  </div>

                  {showDetails && (
                    <motion.div
                      initial={{ opacity: 0, height: 0 }}
                      animate={{ opacity: 1, height: 'auto' }}
                      className="mt-4 space-y-3"
                    >
                      <div>
                        <p className="text-gray-900 font-medium mb-2">{question.question}</p>
                      </div>

                      {question.type === 'multiple-choice' && (
                        <div className="space-y-2">
                          {question.options?.map((option, optIndex) => (
                            option && (
                              <div
                                key={optIndex}
                                className={`p-2 rounded border text-sm ${
                                  option === question.correctAnswer
                                    ? 'border-green-500 bg-green-100 text-green-800'
                                    : option === userAnswer
                                    ? 'border-red-500 bg-red-100 text-red-800'
                                    : 'border-gray-200 bg-white text-gray-700'
                                }`}
                              >
                                {option}
                                {option === question.correctAnswer && (
                                  <span className="ml-2 text-green-600">✓ Correct</span>
                                )}
                                {option === userAnswer && option !== question.correctAnswer && (
                                  <span className="ml-2 text-red-600">✗ Your answer</span>
                                )}
                              </div>
                            )
                          ))}
                        </div>
                      )}

                      {(question.type === 'true-false' || 
                        question.type === 'short-answer' || 
                        question.type === 'essay') && (
                        <div className="space-y-2">
                          <div>
                            <span className="text-sm font-medium text-gray-700">Your Answer: </span>
                            <span className={`text-sm ${isCorrect ? 'text-green-600' : 'text-red-600'}`}>
                              {userAnswer || 'No answer provided'}
                            </span>
                          </div>
                          
                          <div>
                            <span className="text-sm font-medium text-gray-700">Correct Answer: </span>
                            <span className="text-sm text-green-600">{question.correctAnswer}</span>
                          </div>
                        </div>
                      )}

                      {question.explanation && (
                        <div className="p-3 bg-blue-50 border border-blue-200 rounded">
                          <p className="text-sm text-blue-800">
                            <strong>Explanation:</strong> {question.explanation}
                          </p>
                        </div>
                      )}
                    </motion.div>
                  )}
                </div>
              )
            })}
          </div>
        </motion.div>
      )}

      {/* Actions */}
      {isTeacherView && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
          className="bg-white rounded-xl shadow-lg p-6"
        >
          <h2 className="text-xl font-semibold text-gray-900 mb-4">Teacher Actions</h2>
          
          <div className="flex items-center space-x-4">
            <button
              onClick={handleExportResults}
              disabled={false}
              className="flex items-center space-x-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
            >
              <ArrowDownTrayIcon className="w-4 h-4" />
              <span>
                Export Results
              </span>
            </button>

            <button className="flex items-center space-x-2 px-4 py-2 text-gray-700 border border-gray-300 rounded-lg hover:bg-gray-50">
              <ChartBarIcon className="w-4 h-4" />
              <span>View Analytics</span>
            </button>
          </div>
        </motion.div>
      )}
    </div>
  )
}
