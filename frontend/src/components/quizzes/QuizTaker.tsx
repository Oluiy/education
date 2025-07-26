// src/components/quizzes/QuizTaker.tsx
'use client'

import { useState, useEffect, useCallback } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { useForm } from 'react-hook-form'
import { Quiz, Question, QuizAttempt, Answer } from '../../api/quizzes'
import { useApi } from '../../hooks/useApi'
import { useToast } from '../../contexts/ToastContext'
import {
  ClockIcon,
  CheckCircleIcon,
  XCircleIcon,
  ArrowLeftIcon,
  ArrowRightIcon,
  FlagIcon,
  PlayIcon,
  StopIcon,
  ExclamationTriangleIcon
} from '@heroicons/react/24/outline'

interface QuizTakerProps {
  quiz: Quiz
  attempt?: QuizAttempt
  onComplete?: (submission: QuizAttempt) => void
  onExit?: () => void
}

interface QuizAnswers {
  [questionId: string]: string
}

export function QuizTaker({ quiz, attempt, onComplete, onExit }: QuizTakerProps) {
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0)
  const [timeRemaining, setTimeRemaining] = useState<number | null>(
    quiz.timeLimit ? quiz.timeLimit * 60 : null
  )
  const [isStarted, setIsStarted] = useState(false)
  const [isSubmitted, setIsSubmitted] = useState(false)
  const [flaggedQuestions, setFlaggedQuestions] = useState<Set<number>>(new Set())
  const [showConfirmSubmit, setShowConfirmSubmit] = useState(false)

  const { submitQuiz } = useApi()
  const { success, error, warning } = useToast()

  const form = useForm<QuizAnswers>({
    defaultValues: attempt ? 
      attempt.answers.reduce((acc, answer) => {
        acc[answer.questionId] = Array.isArray(answer.answer) ? answer.answer.join(',') : answer.answer.toString()
        return acc
      }, {} as QuizAnswers) : {}
  })

  const questions = quiz.randomizeQuestions && !attempt 
    ? [...quiz.questions].sort(() => Math.random() - 0.5)
    : quiz.questions

  const currentQuestion = questions[currentQuestionIndex]
  const answeredCount = Object.keys(form.watch()).filter(key => 
    form.watch()[key] && form.watch()[key].trim() !== ''
  ).length

  // Timer effect
  useEffect(() => {
    if (!isStarted || !timeRemaining || timeRemaining <= 0) return

    const timer = setInterval(() => {
      setTimeRemaining(prev => {
        if (prev && prev <= 1) {
          handleAutoSubmit()
          return 0
        }
        return prev ? prev - 1 : null
      })
    }, 1000)

    return () => clearInterval(timer)
  }, [isStarted, timeRemaining])

  const handleAutoSubmit = useCallback(async () => {
    if (isSubmitted) return
    
    warning('Time is up! Quiz will be submitted automatically.')
    await handleSubmit(form.getValues())
  }, [isSubmitted])

  const handleStart = () => {
    setIsStarted(true)
    success('Quiz started! Good luck!')
  }

  const handleSubmit = async (answers: QuizAnswers) => {
    if (isSubmitted) return

    try {
      setIsSubmitted(true)
      
      const answersArray = Object.entries(answers).map(([questionId, answer]) => ({
        questionId,
        answer,
        isCorrect: false,
        points: 0
      }))

      const submission = await submitQuiz.mutateAsync({
        quizId: quiz.id,
        answers: answersArray
      })

      success('Quiz submitted successfully!')
      onComplete?.(submission as QuizAttempt)
    } catch (err) {
      setIsSubmitted(false)
      error(
        `Failed to submit quiz: ${err instanceof Error ? err.message : 'Unknown error'}`
      )
    }
  }

  const handleNext = () => {
    if (currentQuestionIndex < questions.length - 1) {
      setCurrentQuestionIndex(currentQuestionIndex + 1)
    }
  }

  const handlePrevious = () => {
    if (currentQuestionIndex > 0) {
      setCurrentQuestionIndex(currentQuestionIndex - 1)
    }
  }

  const toggleFlag = () => {
    const newFlagged = new Set(flaggedQuestions)
    if (newFlagged.has(currentQuestionIndex)) {
      newFlagged.delete(currentQuestionIndex)
    } else {
      newFlagged.add(currentQuestionIndex)
    }
    setFlaggedQuestions(newFlagged)
  }

  const formatTime = (seconds: number) => {
    const minutes = Math.floor(seconds / 60)
    const remainingSeconds = seconds % 60
    return `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`
  }

  const getProgressColor = () => {
    if (!timeRemaining || !quiz.timeLimit) return 'bg-blue-600'
    const percentRemaining = timeRemaining / (quiz.timeLimit * 60)
    if (percentRemaining > 0.5) return 'bg-green-600'
    if (percentRemaining > 0.25) return 'bg-yellow-600'
    return 'bg-red-600'
  }

  if (!isStarted) {
    return (
      <div className="max-w-2xl mx-auto">
        <div className="bg-white rounded-xl shadow-lg p-8 text-center">
          <div className="mb-6">
            <PlayIcon className="w-16 h-16 mx-auto text-blue-600 mb-4" />
            <h1 className="text-3xl font-bold text-gray-900 mb-2">{quiz.title}</h1>
            <p className="text-gray-600">{quiz.description}</p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-8">
            <div className="p-4 bg-gray-50 rounded-lg">
              <div className="text-2xl font-bold text-gray-900">{questions.length}</div>
              <div className="text-sm text-gray-600">Questions</div>
            </div>
            
            {quiz.timeLimit && (
              <div className="p-4 bg-gray-50 rounded-lg">
                <div className="text-2xl font-bold text-gray-900">{quiz.timeLimit}</div>
                <div className="text-sm text-gray-600">Minutes</div>
              </div>
            )}
            
            <div className="p-4 bg-gray-50 rounded-lg">
              <div className="text-2xl font-bold text-gray-900">{quiz.passingScore}%</div>
              <div className="text-sm text-gray-600">To Pass</div>
            </div>
            
            <div className="p-4 bg-gray-50 rounded-lg">
              <div className="text-2xl font-bold text-gray-900">{quiz.attempts}</div>
              <div className="text-sm text-gray-600">Attempts</div>
            </div>
          </div>

          <div className="text-sm text-gray-600 mb-6 space-y-2">
            <p>• Read each question carefully before answering</p>
            <p>• You can navigate between questions using the navigation buttons</p>
            <p>• Flag questions you want to review later</p>
            {quiz.timeLimit && <p>• The quiz will auto-submit when time runs out</p>}
            {!quiz.showResults && <p>• Results will be available after instructor review</p>}
          </div>

          <div className="flex items-center justify-center space-x-4">
            <button
              onClick={onExit}
              className="px-6 py-2 text-gray-700 border border-gray-300 rounded-lg hover:bg-gray-50"
            >
              Cancel
            </button>
            
            <button
              onClick={handleStart}
              className="flex items-center space-x-2 px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
            >
              <PlayIcon className="w-4 h-4" />
              <span>Start Quiz</span>
            </button>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="max-w-4xl mx-auto">
      {/* Header */}
      <div className="bg-white rounded-xl shadow-lg p-6 mb-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">{quiz.title}</h1>
            <p className="text-gray-600">
              Question {currentQuestionIndex + 1} of {questions.length} • 
              {answeredCount} answered • 
              {flaggedQuestions.size} flagged
            </p>
          </div>

          <div className="flex items-center space-x-4">
            {timeRemaining !== null && (
              <div className="flex items-center space-x-2">
                <ClockIcon className="w-5 h-5 text-gray-500" />
                <span className={`font-mono text-lg ${
                  timeRemaining < 300 ? 'text-red-600 font-bold' : 'text-gray-900'
                }`}>
                  {formatTime(timeRemaining)}
                </span>
              </div>
            )}

            <button
              onClick={onExit}
              className="flex items-center space-x-2 px-4 py-2 text-gray-700 border border-gray-300 rounded-lg hover:bg-gray-50"
            >
              <ArrowLeftIcon className="w-4 h-4" />
              <span>Exit</span>
            </button>
          </div>
        </div>

        {/* Progress Bar */}
        <div className="mt-4">
          <div className="flex justify-between text-sm text-gray-600 mb-2">
            <span>Progress</span>
            <span>{Math.round((answeredCount / questions.length) * 100)}% Complete</span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div 
              className={`h-2 rounded-full transition-all duration-300 ${getProgressColor()}`}
              style={{ width: `${(answeredCount / questions.length) * 100}%` }}
            />
          </div>
        </div>
      </div>

      {/* Question */}
      <div className="bg-white rounded-xl shadow-lg p-8 mb-6">
        <div className="flex items-start justify-between mb-6">
          <div className="flex-1">
            <div className="flex items-center space-x-3 mb-4">
              <span className="px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-sm font-medium">
                Question {currentQuestionIndex + 1}
              </span>
              <span className="text-sm text-gray-500">
                {currentQuestion.points} point{currentQuestion.points !== 1 ? 's' : ''}
              </span>
            </div>
            
            <h2 className="text-xl font-medium text-gray-900 mb-6">
              {currentQuestion.question}
            </h2>
          </div>

          <button
            onClick={toggleFlag}
            className={`flex items-center space-x-1 px-3 py-1 rounded-lg border transition-colors ${
              flaggedQuestions.has(currentQuestionIndex)
                ? 'border-yellow-500 bg-yellow-50 text-yellow-700'
                : 'border-gray-300 text-gray-600 hover:bg-gray-50'
            }`}
          >
            <FlagIcon className="w-4 h-4" />
            <span className="text-sm">
              {flaggedQuestions.has(currentQuestionIndex) ? 'Flagged' : 'Flag'}
            </span>
          </button>
        </div>

        {/* Question Content */}
        <div className="space-y-4">
          {currentQuestion.type === 'multiple-choice' && (
            <div className="space-y-3">
              {currentQuestion.options?.map((option, index) => (
                option && (
                  <label
                    key={index}
                    className="flex items-start space-x-3 p-4 rounded-lg border border-gray-200 hover:bg-gray-50 cursor-pointer transition-colors"
                  >
                    <input
                      type="radio"
                      {...form.register(`${currentQuestion.id}`)}
                      value={option}
                      className="mt-1 text-blue-600 focus:ring-blue-500"
                    />
                    <span className="text-gray-700">{option}</span>
                  </label>
                )
              ))}
            </div>
          )}

          {currentQuestion.type === 'true-false' && (
            <div className="space-y-3">
              <label className="flex items-center space-x-3 p-4 rounded-lg border border-gray-200 hover:bg-gray-50 cursor-pointer transition-colors">
                <input
                  type="radio"
                  {...form.register(`${currentQuestion.id}`)}
                  value="true"
                  className="text-blue-600 focus:ring-blue-500"
                />
                <span className="text-gray-700">True</span>
              </label>
              
              <label className="flex items-center space-x-3 p-4 rounded-lg border border-gray-200 hover:bg-gray-50 cursor-pointer transition-colors">
                <input
                  type="radio"
                  {...form.register(`${currentQuestion.id}`)}
                  value="false"
                  className="text-blue-600 focus:ring-blue-500"
                />
                <span className="text-gray-700">False</span>
              </label>
            </div>
          )}

          {currentQuestion.type === 'short-answer' && (
            <div>
              <textarea
                {...form.register(`${currentQuestion.id}`)}
                rows={3}
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="Enter your answer here..."
              />
            </div>
          )}

          {currentQuestion.type === 'essay' && (
            <div>
              <textarea
                {...form.register(`${currentQuestion.id}`)}
                rows={8}
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="Write your essay response here..."
              />
            </div>
          )}
        </div>
      </div>

      {/* Navigation */}
      <div className="bg-white rounded-xl shadow-lg p-6">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <button
              onClick={handlePrevious}
              disabled={currentQuestionIndex === 0}
              className="flex items-center space-x-2 px-4 py-2 text-gray-700 border border-gray-300 rounded-lg hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <ArrowLeftIcon className="w-4 h-4" />
              <span>Previous</span>
            </button>

            <button
              onClick={handleNext}
              disabled={currentQuestionIndex === questions.length - 1}
              className="flex items-center space-x-2 px-4 py-2 text-gray-700 border border-gray-300 rounded-lg hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <span>Next</span>
              <ArrowRightIcon className="w-4 h-4" />
            </button>
          </div>

          {/* Question Navigation */}
          <div className="flex items-center space-x-2">
            <span className="text-sm text-gray-600 mr-2">Jump to:</span>
            <div className="flex items-center space-x-1 max-w-md overflow-x-auto">
              {questions.map((_, index) => {
                const questionId = questions[index].id
                const isAnswered = form.watch()[questionId] && form.watch()[questionId].trim() !== ''
                const isCurrent = index === currentQuestionIndex
                const isFlagged = flaggedQuestions.has(index)

                return (
                  <button
                    key={index}
                    onClick={() => setCurrentQuestionIndex(index)}
                    className={`w-8 h-8 rounded-lg text-sm font-medium border-2 transition-colors relative ${
                      isCurrent
                        ? 'border-blue-600 bg-blue-600 text-white'
                        : isAnswered
                        ? 'border-green-600 bg-green-600 text-white'
                        : 'border-gray-300 text-gray-600 hover:bg-gray-50'
                    }`}
                  >
                    {index + 1}
                    {isFlagged && (
                      <div className="absolute -top-1 -right-1 w-3 h-3 bg-yellow-500 rounded-full" />
                    )}
                  </button>
                )
              })}
            </div>
          </div>

          <button
            onClick={() => setShowConfirmSubmit(true)}
            disabled={isSubmitted || submitQuiz.isPending}
            className="flex items-center space-x-2 px-6 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <StopIcon className="w-4 h-4" />
            <span>
              {submitQuiz.isPending ? 'Submitting...' : 'Submit Quiz'}
            </span>
          </button>
        </div>
      </div>

      {/* Submit Confirmation Modal */}
      <AnimatePresence>
        {showConfirmSubmit && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50"
          >
            <motion.div
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.95 }}
              className="bg-white rounded-xl p-6 max-w-md w-full mx-4"
            >
              <h3 className="text-lg font-medium text-gray-900 mb-4">Submit Quiz?</h3>
              
              <div className="mb-6 space-y-2 text-sm text-gray-600">
                <div className="flex justify-between">
                  <span>Questions answered:</span>
                  <span className="font-medium">{answeredCount} of {questions.length}</span>
                </div>
                <div className="flex justify-between">
                  <span>Questions flagged:</span>
                  <span className="font-medium">{flaggedQuestions.size}</span>
                </div>
                {timeRemaining && (
                  <div className="flex justify-between">
                    <span>Time remaining:</span>
                    <span className="font-medium">{formatTime(timeRemaining)}</span>
                  </div>
                )}
              </div>

              {answeredCount < questions.length && (
                <div className="mb-4 p-3 bg-yellow-50 border border-yellow-200 rounded-lg">
                  <div className="flex items-center space-x-2">
                    <ExclamationTriangleIcon className="w-5 h-5 text-yellow-600" />
                    <span className="text-sm text-yellow-800">
                      You have {questions.length - answeredCount} unanswered question{questions.length - answeredCount !== 1 ? 's' : ''}.
                    </span>
                  </div>
                </div>
              )}

              <p className="text-gray-600 mb-6">
                Once submitted, you cannot change your answers. Are you sure you want to submit?
              </p>

              <div className="flex items-center justify-end space-x-3">
                <button
                  onClick={() => setShowConfirmSubmit(false)}
                  className="px-4 py-2 text-gray-700 border border-gray-300 rounded-lg hover:bg-gray-50"
                >
                  Cancel
                </button>
                
                <button
                  onClick={() => {
                    setShowConfirmSubmit(false)
                    handleSubmit(form.getValues())
                  }}
                  className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700"
                >
                  Submit Quiz
                </button>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}
