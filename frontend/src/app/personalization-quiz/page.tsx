'use client'

import { useState } from 'react'
import { motion } from 'framer-motion'
import { useRouter } from 'next/navigation'
import { useAuth } from '@/contexts/AuthContext'
import { useToast } from '@/contexts/ToastContext'
import {
  AcademicCapIcon,
  BookOpenIcon,
  ClockIcon,
  LightBulbIcon,
  UserGroupIcon,
  ChartBarIcon,
  ArrowRightIcon,
  CheckCircleIcon
} from '@heroicons/react/24/outline'

interface QuizQuestion {
  id: string
  question: string
  type: 'single' | 'multiple' | 'scale'
  options: string[]
  category: 'learning_style' | 'subjects' | 'study_habits' | 'goals'
}

interface QuizResponse {
  questionId: string
  answer: string | string[]
  score?: number
}

const QUIZ_QUESTIONS: QuizQuestion[] = [
  {
    id: 'q1',
    question: 'How do you prefer to learn new concepts?',
    type: 'single',
    category: 'learning_style',
    options: [
      'Reading textbooks and taking notes',
      'Watching videos and demonstrations', 
      'Listening to explanations and discussions',
      'Hands-on practice and experiments'
    ]
  },
  {
    id: 'q2',
    question: 'Which subjects interest you the most? (Select all that apply)',
    type: 'multiple',
    category: 'subjects',
    options: [
      'Mathematics',
      'English Language',
      'Physics',
      'Chemistry',
      'Biology',
      'Geography',
      'History',
      'Economics',
      'Literature',
      'Further Mathematics'
    ]
  },
  {
    id: 'q3',
    question: 'What time of day do you study most effectively?',
    type: 'single',
    category: 'study_habits',
    options: [
      'Early morning (5 AM - 8 AM)',
      'Morning (8 AM - 12 PM)',
      'Afternoon (12 PM - 6 PM)',
      'Evening (6 PM - 10 PM)',
      'Late night (10 PM - 2 AM)'
    ]
  },
  {
    id: 'q4',
    question: 'How long can you typically focus on studying without a break?',
    type: 'single',
    category: 'study_habits',
    options: [
      '15-30 minutes',
      '30-45 minutes',
      '45-60 minutes',
      '1-2 hours',
      'More than 2 hours'
    ]
  },
  {
    id: 'q5',
    question: 'What is your primary goal for this academic year?',
    type: 'single',
    category: 'goals',
    options: [
      'Improve overall grades',
      'Excel in specific subjects',
      'Prepare for WAEC/JAMB',
      'Develop study skills',
      'Build confidence in learning'
    ]
  },
  {
    id: 'q6',
    question: 'Rate your confidence in each area (1 = Low, 5 = High)',
    type: 'scale',
    category: 'subjects',
    options: [
      'Problem-solving skills',
      'Written communication',
      'Memorization',
      'Critical thinking',
      'Time management'
    ]
  },
  {
    id: 'q7',
    question: 'Which study environment helps you focus best?',
    type: 'single',
    category: 'study_habits',
    options: [
      'Complete silence',
      'Soft background music',
      'Natural sounds (rain, birds)',
      'Busy environment with activity',
      'Study groups with friends'
    ]
  },
  {
    id: 'q8',
    question: 'How do you prefer to review before exams?',
    type: 'single',
    category: 'learning_style',
    options: [
      'Create detailed notes and summaries',
      'Practice past questions repeatedly',
      'Discuss topics with classmates',
      'Use flashcards and quick reviews',
      'Teach concepts to others'
    ]
  }
]

export default function PersonalizationQuiz() {
  const [currentQuestion, setCurrentQuestion] = useState(0)
  const [responses, setResponses] = useState<QuizResponse[]>([])
  const [isCompleting, setIsCompleting] = useState(false)
  const [selectedAnswers, setSelectedAnswers] = useState<string[]>([])
  const [scaleAnswers, setScaleAnswers] = useState<{ [key: string]: number }>({})
  
  const { user } = useAuth()
  const { success: showSuccess, error: showError } = useToast()
  const router = useRouter()
  
  const currentQ = QUIZ_QUESTIONS[currentQuestion]
  const isLastQuestion = currentQuestion === QUIZ_QUESTIONS.length - 1

  const handleSingleChoice = (answer: string) => {
    setSelectedAnswers([answer])
  }

  const handleMultipleChoice = (answer: string) => {
    setSelectedAnswers(prev => 
      prev.includes(answer) 
        ? prev.filter(a => a !== answer)
        : [...prev, answer]
    )
  }

  const handleScaleAnswer = (option: string, score: number) => {
    setScaleAnswers(prev => ({
      ...prev,
      [option]: score
    }))
  }

  const handleNext = () => {
    // Save current response
    let response: QuizResponse
    
    if (currentQ.type === 'scale') {
      response = {
        questionId: currentQ.id,
        answer: Object.keys(scaleAnswers),
        score: Object.values(scaleAnswers).reduce((a, b) => a + b, 0) / Object.keys(scaleAnswers).length
      }
    } else {
      response = {
        questionId: currentQ.id,
        answer: currentQ.type === 'multiple' ? selectedAnswers : selectedAnswers[0] || ''
      }
    }
    
    const newResponses = [...responses]
    const existingIndex = responses.findIndex(r => r.questionId === currentQ.id)
    
    if (existingIndex >= 0) {
      newResponses[existingIndex] = response
    } else {
      newResponses.push(response)
    }
    
    setResponses(newResponses)
    
    if (isLastQuestion) {
      completeQuiz(newResponses)
    } else {
      setCurrentQuestion(prev => prev + 1)
      setSelectedAnswers([])
      setScaleAnswers({})
    }
  }

  const handlePrevious = () => {
    if (currentQuestion > 0) {
      setCurrentQuestion(prev => prev - 1)
      
      // Load previous answers
      const prevResponse = responses.find(r => r.questionId === QUIZ_QUESTIONS[currentQuestion - 1].id)
      if (prevResponse) {
        if (Array.isArray(prevResponse.answer)) {
          setSelectedAnswers(prevResponse.answer)
        } else {
          setSelectedAnswers([prevResponse.answer])
        }
      }
    }
  }

  const completeQuiz = async (finalResponses: QuizResponse[]) => {
    setIsCompleting(true)
    
    try {
      // Analyze responses to create personalization profile
      const profile = analyzeResponses(finalResponses)
      
      // Save to backend
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_GATEWAY_URL}/auth/api/v1/users/${user?.id}/profile`, {
        method: 'PATCH',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify({
          personalization_profile: profile,
          quiz_completed: true,
          quiz_responses: finalResponses
        })
      })

      if (!response.ok) {
        throw new Error('Failed to save quiz results')
      }

      showSuccess('Personalization quiz completed! Your learning experience is now customized.')
      router.push('/dashboard')
      
    } catch (error) {
      console.error('Error completing quiz:', error)
      showError('Failed to save quiz results. Please try again.')
    } finally {
      setIsCompleting(false)
    }
  }

  const analyzeResponses = (responses: QuizResponse[]) => {
    const profile: any = {
      learning_style: 'visual',
      preferred_subjects: [],
      study_schedule: 'morning',
      focus_duration: 45,
      study_environment: 'quiet',
      confidence_areas: [],
      weak_areas: [],
      goals: [],
      recommendations: []
    }

    responses.forEach(response => {
      const question = QUIZ_QUESTIONS.find(q => q.id === response.questionId)
      if (!question) return

      switch (question.category) {
        case 'learning_style':
          if (typeof response.answer === 'string') {
            if (response.answer.includes('Reading')) profile.learning_style = 'reading'
            else if (response.answer.includes('videos')) profile.learning_style = 'visual'
            else if (response.answer.includes('Listening')) profile.learning_style = 'auditory'
            else if (response.answer.includes('Hands-on')) profile.learning_style = 'kinesthetic'
          }
          break
          
        case 'subjects':
          if (Array.isArray(response.answer)) {
            profile.preferred_subjects = response.answer
          }
          break
          
        case 'study_habits':
          if (typeof response.answer === 'string') {
            if (response.answer.includes('morning')) profile.study_schedule = 'morning'
            else if (response.answer.includes('afternoon')) profile.study_schedule = 'afternoon'
            else if (response.answer.includes('evening')) profile.study_schedule = 'evening'
            
            if (response.answer.includes('15-30')) profile.focus_duration = 25
            else if (response.answer.includes('30-45')) profile.focus_duration = 35
            else if (response.answer.includes('45-60')) profile.focus_duration = 50
            else if (response.answer.includes('1-2')) profile.focus_duration = 90
          }
          break
          
        case 'goals':
          if (typeof response.answer === 'string') {
            profile.goals.push(response.answer)
          }
          break
      }
    })

    // Generate recommendations based on profile
    profile.recommendations = generateRecommendations(profile)
    
    return profile
  }

  const generateRecommendations = (profile: any) => {
    const recommendations = []
    
    if (profile.learning_style === 'visual') {
      recommendations.push('Use mind maps and diagrams for better understanding')
      recommendations.push('Watch educational videos and animations')
    }
    
    if (profile.focus_duration <= 30) {
      recommendations.push('Try the Pomodoro Technique with 25-minute study sessions')
      recommendations.push('Take regular 5-10 minute breaks between sessions')
    }
    
    if (profile.preferred_subjects.includes('Mathematics')) {
      recommendations.push('Practice daily math problems to build confidence')
      recommendations.push('Focus on understanding concepts before memorizing formulas')
    }
    
    return recommendations
  }

  const canProceed = () => {
    if (currentQ.type === 'single') {
      return selectedAnswers.length > 0
    } else if (currentQ.type === 'multiple') {
      return selectedAnswers.length > 0
    } else if (currentQ.type === 'scale') {
      return Object.keys(scaleAnswers).length === currentQ.options.length
    }
    return false
  }

  const progressPercentage = ((currentQuestion + 1) / QUIZ_QUESTIONS.length) * 100

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50 py-8">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="text-center mb-8">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="inline-flex items-center space-x-2 bg-blue-100 text-blue-800 px-4 py-2 rounded-full text-sm font-medium mb-4"
          >
            <LightBulbIcon className="w-4 h-4" />
            <span>Personalization Quiz</span>
          </motion.div>
          
          <motion.h1
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
            className="text-3xl font-bold text-gray-900 mb-2"
          >
            Let's Personalize Your Learning Experience
          </motion.h1>
          
          <motion.p
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
            className="text-lg text-gray-600 max-w-2xl mx-auto"
          >
            Answer these questions to help us customize your dashboard, study recommendations, and learning path.
          </motion.p>
        </div>

        {/* Progress Bar */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
          className="mb-8"
        >
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm font-medium text-gray-700">
              Question {currentQuestion + 1} of {QUIZ_QUESTIONS.length}
            </span>
            <span className="text-sm font-medium text-blue-600">
              {Math.round(progressPercentage)}% Complete
            </span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2">
            <motion.div
              className="bg-blue-600 h-2 rounded-full"
              initial={{ width: 0 }}
              animate={{ width: `${progressPercentage}%` }}
              transition={{ duration: 0.3 }}
            />
          </div>
        </motion.div>

        {/* Quiz Card */}
        <motion.div
          key={currentQuestion}
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          exit={{ opacity: 0, x: -20 }}
          className="bg-white rounded-2xl shadow-lg p-8 mb-8"
        >
          <div className="flex items-start space-x-4 mb-6">
            <div className="flex-shrink-0">
              <div className="w-12 h-12 bg-blue-100 rounded-xl flex items-center justify-center">
                {currentQ.category === 'learning_style' && <BookOpenIcon className="w-6 h-6 text-blue-600" />}
                {currentQ.category === 'subjects' && <AcademicCapIcon className="w-6 h-6 text-blue-600" />}
                {currentQ.category === 'study_habits' && <ClockIcon className="w-6 h-6 text-blue-600" />}
                {currentQ.category === 'goals' && <ChartBarIcon className="w-6 h-6 text-blue-600" />}
              </div>
            </div>
            <div className="flex-1">
              <h2 className="text-xl font-semibold text-gray-900 mb-2">
                {currentQ.question}
              </h2>
              {currentQ.type === 'multiple' && (
                <p className="text-sm text-gray-600">Select all that apply</p>
              )}
              {currentQ.type === 'scale' && (
                <p className="text-sm text-gray-600">Rate each item from 1 (Low) to 5 (High)</p>
              )}
            </div>
          </div>

          {/* Answer Options */}
          <div className="space-y-3">
            {currentQ.type === 'scale' ? (
              // Scale questions
              currentQ.options.map((option, index) => (
                <div key={index} className="flex items-center justify-between p-4 border border-gray-200 rounded-lg">
                  <span className="font-medium text-gray-900">{option}</span>
                  <div className="flex space-x-2">
                    {[1, 2, 3, 4, 5].map((score) => (
                      <button
                        key={score}
                        onClick={() => handleScaleAnswer(option, score)}
                        className={`w-10 h-10 rounded-full border-2 flex items-center justify-center text-sm font-medium transition-colors ${
                          scaleAnswers[option] === score
                            ? 'bg-blue-600 border-blue-600 text-white'
                            : 'border-gray-300 text-gray-600 hover:border-blue-300'
                        }`}
                      >
                        {score}
                      </button>
                    ))}
                  </div>
                </div>
              ))
            ) : (
              // Single/Multiple choice questions
              currentQ.options.map((option, index) => (
                <button
                  key={index}
                  onClick={() => 
                    currentQ.type === 'single' 
                      ? handleSingleChoice(option)
                      : handleMultipleChoice(option)
                  }
                  className={`w-full text-left p-4 border-2 rounded-lg transition-all ${
                    selectedAnswers.includes(option)
                      ? 'border-blue-500 bg-blue-50 text-blue-900'
                      : 'border-gray-200 hover:border-gray-300 text-gray-900'
                  }`}
                >
                  <div className="flex items-center space-x-3">
                    <div className={`w-5 h-5 rounded-full border-2 flex items-center justify-center ${
                      selectedAnswers.includes(option)
                        ? 'border-blue-500 bg-blue-500'
                        : 'border-gray-300'
                    }`}>
                      {selectedAnswers.includes(option) && (
                        <CheckCircleIcon className="w-3 h-3 text-white" />
                      )}
                    </div>
                    <span className="font-medium">{option}</span>
                  </div>
                </button>
              ))
            )}
          </div>
        </motion.div>

        {/* Navigation */}
        <div className="flex items-center justify-between">
          <button
            onClick={handlePrevious}
            disabled={currentQuestion === 0}
            className="px-6 py-3 text-gray-600 font-medium disabled:opacity-50 disabled:cursor-not-allowed hover:text-gray-800 transition-colors"
          >
            ← Previous
          </button>
          
          <button
            onClick={handleNext}
            disabled={!canProceed() || isCompleting}
            className="px-8 py-3 bg-blue-600 text-white font-medium rounded-lg disabled:opacity-50 disabled:cursor-not-allowed hover:bg-blue-700 transition-colors flex items-center space-x-2"
          >
            {isCompleting ? (
              <>
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white" />
                <span>Completing...</span>
              </>
            ) : (
              <>
                <span>{isLastQuestion ? 'Complete Quiz' : 'Next'}</span>
                <ArrowRightIcon className="w-4 h-4" />
              </>
            )}
          </button>
        </div>
      </div>
    </div>
  )
}
