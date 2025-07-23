'use client'

import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { useRouter } from 'next/navigation'
import {
  ClockIcon,
  CheckCircleIcon,
  XCircleIcon,
  ArrowRightIcon,
  ArrowLeftIcon,
  FlagIcon
} from '@heroicons/react/24/outline'

interface Question {
  id: string
  question: string
  type: 'multiple_choice' | 'true_false' | 'short_answer'
  options?: string[]
  correct_answer: string
  points: number
}

interface QuizAttempt {
  id: string
  quiz_id: string
  answers: Record<string, string>
  started_at: string
  submitted_at?: string
  score?: number
  passed?: boolean
}

export default function TakeQuizPage({ params }: { params: { id: string } }) {
  const router = useRouter()
  const [quiz, setQuiz] = useState<any>(null)
  const [questions, setQuestions] = useState<Question[]>([])
  const [currentQuestion, setCurrentQuestion] = useState(0)
  const [answers, setAnswers] = useState<Record<string, string>>({})
  const [timeLeft, setTimeLeft] = useState(0)
  const [loading, setLoading] = useState(true)
  const [submitting, setSubmitting] = useState(false)
  const [flaggedQuestions, setFlaggedQuestions] = useState<Set<string>>(new Set())

  useEffect(() => {
    fetchQuiz()
  }, [params.id])

  useEffect(() => {
    if (timeLeft > 0) {
      const timer = setTimeout(() => setTimeLeft(timeLeft - 1), 1000)
      return () => clearTimeout(timer)
    } else if (timeLeft === 0 && quiz) {
      handleSubmit()
    }
  }, [timeLeft, quiz])

  const fetchQuiz = async () => {
    try {
      // Mock data for now - replace with actual API call
      const mockQuiz = {
        id: params.id,
        title: 'Calculus Fundamentals',
        description: 'Test your understanding of basic calculus concepts',
        duration: 30,
        questions_count: 5,
        pass_percentage: 70,
        attempts_allowed: 3,
        current_attempt: 1
      }

      const mockQuestions: Question[] = [
        {
          id: '1',
          question: 'What is the derivative of x²?',
          type: 'multiple_choice',
          options: ['2x', 'x²', '2x²', 'x'],
          correct_answer: '2x',
          points: 10
        },
        {
          id: '2',
          question: 'The integral of 1/x dx is ln(x) + C',
          type: 'true_false',
          options: ['True', 'False'],
          correct_answer: 'True',
          points: 10
        },
        {
          id: '3',
          question: 'What is the limit of (sin x)/x as x approaches 0?',
          type: 'short_answer',
          correct_answer: '1',
          points: 15
        },
        {
          id: '4',
          question: 'Which of the following is the correct formula for the chain rule?',
          type: 'multiple_choice',
          options: [
            '(f(g(x)))′ = f′(g(x)) · g′(x)',
            '(f(g(x)))′ = f′(x) · g′(x)',
            '(f(g(x)))′ = f(x) · g′(x)',
            '(f(g(x)))′ = f′(g(x)) · g(x)'
          ],
          correct_answer: '(f(g(x)))′ = f′(g(x)) · g′(x)',
          points: 15
        },
        {
          id: '5',
          question: 'What is the second derivative of 3x³ + 2x² - 5x + 1?',
          type: 'multiple_choice',
          options: ['18x + 4', '9x² + 4x - 5', '18x + 4x', '6x + 4'],
          correct_answer: '18x + 4',
          points: 20
        }
      ]

      setQuiz(mockQuiz)
      setQuestions(mockQuestions)
      setTimeLeft(mockQuiz.duration * 60) // Convert to seconds
      setLoading(false)
    } catch (error) {
      console.error('Error fetching quiz:', error)
      setLoading(false)
    }
  }

  const handleAnswerChange = (questionId: string, answer: string) => {
    setAnswers(prev => ({
      ...prev,
      [questionId]: answer
    }))
  }

  const toggleFlag = (questionId: string) => {
    setFlaggedQuestions(prev => {
      const newSet = new Set(prev)
      if (newSet.has(questionId)) {
        newSet.delete(questionId)
      } else {
        newSet.add(questionId)
      }
      return newSet
    })
  }

  const handleSubmit = async () => {
    setSubmitting(true)
    try {
      // TODO: Replace with actual API call
      const attempt: QuizAttempt = {
        id: Date.now().toString(),
        quiz_id: params.id,
        answers,
        started_at: new Date().toISOString(),
        submitted_at: new Date().toISOString()
      }
      
      console.log('Submitting quiz:', attempt)
      
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 2000))
      
      router.push(`/dashboard/quizzes/${params.id}/results`)
    } catch (error) {
      console.error('Error submitting quiz:', error)
    } finally {
      setSubmitting(false)
    }
  }

  const formatTime = (seconds: number) => {
    const minutes = Math.floor(seconds / 60)
    const remainingSeconds = seconds % 60
    return `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`
  }

  const getCompletionPercentage = () => {
    const answeredCount = Object.keys(answers).length
    return (answeredCount / questions.length) * 100
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="flex items-center justify-center h-64">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
          </div>
        </div>
      </div>
    )
  }

  const currentQuestionData = questions[currentQuestion]

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Main Content - Centralized */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="max-w-4xl mx-auto">
          {/* Quiz Header */}
          <div className="bg-white rounded-xl border border-gray-200 p-6 mb-6">
            <div className="flex items-center justify-between mb-4">
              <div>
                <h1 className="text-2xl font-bold text-gray-900">{quiz.title}</h1>
                <p className="text-gray-600">Question {currentQuestion + 1} of {questions.length}</p>
              </div>
              <div className="flex items-center gap-4">
                <div className="flex items-center gap-2 text-sm">
                  <ClockIcon className="w-4 h-4 text-gray-500" />
                  <span className={`font-medium ${timeLeft < 300 ? 'text-red-600' : 'text-gray-900'}`}>
                    {formatTime(timeLeft)}
                </span>
              </div>
              <div className="text-sm text-gray-600">
                Attempt {quiz.current_attempt} of {quiz.attempts_allowed}
              </div>
            </div>
          </div>
          
          {/* Progress Bar */}
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div 
              className="bg-primary-600 h-2 rounded-full transition-all duration-300"
              style={{ width: `${getCompletionPercentage()}%` }}
            />
          </div>
        </div>

        {/* Question Content */}
        <motion.div
          key={currentQuestion}
          initial={{ opacity: 0, x: 50 }}
          animate={{ opacity: 1, x: 0 }}
          exit={{ opacity: 0, x: -50 }}
          transition={{ duration: 0.3 }}
          className="bg-white rounded-xl border border-gray-200 p-6 mb-6"
        >
          <div className="flex items-start justify-between mb-6">
            <div className="flex-1">
              <div className="flex items-center gap-3 mb-4">
                <span className="bg-primary-100 text-primary-700 px-3 py-1 rounded-full text-sm font-medium">
                  {currentQuestionData.points} points
                </span>
                <button
                  onClick={() => toggleFlag(currentQuestionData.id)}
                  className={`p-2 rounded-lg transition-colors ${
                    flaggedQuestions.has(currentQuestionData.id)
                      ? 'bg-yellow-100 text-yellow-600'
                      : 'bg-gray-100 text-gray-500 hover:bg-gray-200'
                  }`}
                >
                  <FlagIcon className="w-4 h-4" />
                </button>
              </div>
              
              <h2 className="text-xl font-semibold text-gray-900 mb-6">
                {currentQuestionData.question}
              </h2>
              
              {/* Answer Options */}
              <div className="space-y-4">
                {currentQuestionData.type === 'multiple_choice' && (
                  <div className="space-y-3">
                    {currentQuestionData.options?.map((option, index) => (
                      <label
                        key={index}
                        className="flex items-center p-4 border border-gray-200 rounded-lg hover:bg-gray-50 cursor-pointer transition-colors"
                      >
                        <input
                          type="radio"
                          name={currentQuestionData.id}
                          value={option}
                          checked={answers[currentQuestionData.id] === option}
                          onChange={(e) => handleAnswerChange(currentQuestionData.id, e.target.value)}
                          className="w-4 h-4 text-primary-600 border-gray-300 focus:ring-primary-500"
                        />
                        <span className="ml-3 text-gray-900">{option}</span>
                      </label>
                    ))}
                  </div>
                )}
                
                {currentQuestionData.type === 'true_false' && (
                  <div className="space-y-3">
                    {['True', 'False'].map((option) => (
                      <label
                        key={option}
                        className="flex items-center p-4 border border-gray-200 rounded-lg hover:bg-gray-50 cursor-pointer transition-colors"
                      >
                        <input
                          type="radio"
                          name={currentQuestionData.id}
                          value={option}
                          checked={answers[currentQuestionData.id] === option}
                          onChange={(e) => handleAnswerChange(currentQuestionData.id, e.target.value)}
                          className="w-4 h-4 text-primary-600 border-gray-300 focus:ring-primary-500"
                        />
                        <span className="ml-3 text-gray-900">{option}</span>
                      </label>
                    ))}
                  </div>
                )}
                
                {currentQuestionData.type === 'short_answer' && (
                  <textarea
                    value={answers[currentQuestionData.id] || ''}
                    onChange={(e) => handleAnswerChange(currentQuestionData.id, e.target.value)}
                    placeholder="Type your answer here..."
                    className="w-full p-4 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                    rows={4}
                  />
                )}
              </div>
            </div>
          </div>
        </motion.div>

        {/* Navigation */}
        <div className="flex items-center justify-between">
          <button
            onClick={() => setCurrentQuestion(Math.max(0, currentQuestion - 1))}
            disabled={currentQuestion === 0}
            className="flex items-center gap-2 px-4 py-2 text-gray-600 hover:text-gray-900 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <ArrowLeftIcon className="w-4 h-4" />
            Previous
          </button>
          
          <div className="flex items-center gap-2">
            {questions.map((_, index) => (
              <button
                key={index}
                onClick={() => setCurrentQuestion(index)}
                className={`w-8 h-8 rounded-full text-sm font-medium transition-colors ${
                  index === currentQuestion
                    ? 'bg-primary-600 text-white'
                    : answers[questions[index].id]
                    ? 'bg-green-100 text-green-700'
                    : flaggedQuestions.has(questions[index].id)
                    ? 'bg-yellow-100 text-yellow-700'
                    : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                }`}
              >
                {index + 1}
              </button>
            ))}
          </div>
          
          {currentQuestion === questions.length - 1 ? (
            <button
              onClick={handleSubmit}
              disabled={submitting}
              className="flex items-center gap-2 px-6 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 disabled:opacity-50 transition-colors"
            >
              {submitting ? (
                <>
                  <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                  Submitting...
                </>
              ) : (
                <>
                  <CheckCircleIcon className="w-4 h-4" />
                  Submit Quiz
                </>
              )}
            </button>
          ) : (
            <button
              onClick={() => setCurrentQuestion(Math.min(questions.length - 1, currentQuestion + 1))}
              className="flex items-center gap-2 px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors"
            >
              Next
              <ArrowRightIcon className="w-4 h-4" />
            </button>
          )}
        </div>
        </div>
      </div>
    </div>
  )
}
