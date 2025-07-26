// src/app/quizzes/page.tsx
'use client'

import { useState } from 'react'
import { motion } from 'framer-motion'
import { useApi } from '../../hooks/useApi'
import { useAuth } from '../../contexts/AuthContext'
import { QuizCard } from '../../components/quizzes/QuizCard'
import { LoadingSpinner } from '../../components/ui/LoadingSpinner'
import { ErrorBoundary } from '../../components/ui/ErrorBoundary'
import Link from 'next/link'
import {
  PlusIcon,
  MagnifyingGlassIcon,
  FunnelIcon,
  AcademicCapIcon,
  CheckCircleIcon,
  TrophyIcon,
  ClockIcon
} from '@heroicons/react/24/outline'

export default function QuizzesPage() {
  const [searchTerm, setSearchTerm] = useState('')
  const [selectedCourse, setSelectedCourse] = useState<string>('')
  const [difficulty, setDifficulty] = useState<string>('')
  const [status, setStatus] = useState<string>('')

  const { user } = useAuth()
  const { 
    useQuizzes, 
    useCourses, 
    useQuizAttempts,
    useUserQuizStats 
  } = useApi()

  const { data: quizzesData, isLoading: quizzesLoading, error: quizzesError } = useQuizzes({
    search: searchTerm,
    courseId: selectedCourse
  })

  const { data: coursesData } = useCourses()
  const { data: userAttempts } = useQuizAttempts(user?.id ?? '')
  const { data: userStats } = useUserQuizStats(user?.id ?? '')

  const quizzes = quizzesData?.quizzes ?? []
  const courses = coursesData?.courses ?? []

  const filteredQuizzes = quizzes.filter((quiz: any) => {
    // Difficulty filter
    if (difficulty) {
      const avgPoints = quiz.questions.reduce((acc: number, q: any) => acc + q.points, 0) / quiz.questions.length
      const quizDifficulty = avgPoints <= 2 ? 'easy' : avgPoints <= 4 ? 'medium' : 'hard'
      if (quizDifficulty !== difficulty) return false
    }

    // Status filter for students
    if (user?.role === 'student' && status) {
      const attempts = userAttempts?.filter(attempt => attempt.quizId === quiz.id) || []
      const bestScore = Math.max(...attempts.map(a => a.score), 0)
      
      if (status === 'completed' && attempts.length === 0) return false
      if (status === 'passed' && bestScore < quiz.passingScore) return false
      if (status === 'failed' && (attempts.length === 0 || bestScore >= quiz.passingScore)) return false
      if (status === 'not-started' && attempts.length > 0) return false
    }

    return true
  })

  if (quizzesLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <LoadingSpinner size="lg" />
      </div>
    )
  }

  if (quizzesError) {
    return (
      <ErrorBoundary>
        <div className="text-center py-12">
          <p className="text-red-600">Failed to load quizzes</p>
        </div>
      </ErrorBoundary>
    )
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* Header */}
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Quizzes</h1>
          <p className="text-gray-600 mt-2">
            {user?.role === 'student' 
              ? 'Test your knowledge with interactive quizzes'
              : 'Create and manage quizzes for your courses'
            }
          </p>
        </div>

        {user?.role === 'teacher' && (
          <Link href="/quizzes/create">
            <button className="flex items-center space-x-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700">
              <PlusIcon className="w-4 h-4" />
              <span>Create Quiz</span>
            </button>
          </Link>
        )}
      </div>

      {/* Stats for Students */}
      {user?.role === 'student' && userStats && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8"
        >
          <div className="bg-white rounded-xl shadow-sm p-6">
            <div className="flex items-center space-x-3">
              <div className="p-2 bg-blue-100 rounded-lg">
                <AcademicCapIcon className="w-6 h-6 text-blue-600" />
              </div>
              <div>
                <p className="text-2xl font-bold text-gray-900">{userStats.totalAttempts}</p>
                <p className="text-sm text-gray-600">Total Attempts</p>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-xl shadow-sm p-6">
            <div className="flex items-center space-x-3">
              <div className="p-2 bg-green-100 rounded-lg">
                <CheckCircleIcon className="w-6 h-6 text-green-600" />
              </div>
              <div>
                <p className="text-2xl font-bold text-gray-900">{userStats.quizzesPassed}</p>
                <p className="text-sm text-gray-600">Quizzes Passed</p>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-xl shadow-sm p-6">
            <div className="flex items-center space-x-3">
              <div className="p-2 bg-yellow-100 rounded-lg">
                <TrophyIcon className="w-6 h-6 text-yellow-600" />
              </div>
              <div>
                <p className="text-2xl font-bold text-gray-900">{userStats.averageScore}%</p>
                <p className="text-sm text-gray-600">Average Score</p>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-xl shadow-sm p-6">
            <div className="flex items-center space-x-3">
              <div className="p-2 bg-purple-100 rounded-lg">
                <ClockIcon className="w-6 h-6 text-purple-600" />
              </div>
              <div>
                <p className="text-2xl font-bold text-gray-900">{userStats.totalTimeSpent}</p>
                <p className="text-sm text-gray-600">Time Spent</p>
              </div>
            </div>
          </div>
        </motion.div>
      )}

      {/* Filters */}
      <div className="bg-white rounded-xl shadow-sm p-6 mb-8">
        <div className="flex items-center space-x-4 mb-4">
          <FunnelIcon className="w-5 h-5 text-gray-400" />
          <span className="font-medium text-gray-700">Filters</span>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          {/* Search */}
          <div className="relative">
            <MagnifyingGlassIcon className="w-5 h-5 absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" />
            <input
              type="text"
              placeholder="Search quizzes..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>

          {/* Course Filter */}
          <select
            value={selectedCourse}
            onChange={(e) => setSelectedCourse(e.target.value)}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          >
            <option value="">All Courses</option>
            {courses.map((course: any) => (
              <option key={course.id} value={course.id}>
                {course.title}
              </option>
            ))}
          </select>

          {/* Difficulty Filter */}
          <select
            value={difficulty}
            onChange={(e) => setDifficulty(e.target.value)}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          >
            <option value="">All Difficulties</option>
            <option value="easy">Easy</option>
            <option value="medium">Medium</option>
            <option value="hard">Hard</option>
          </select>

          {/* Status Filter (Students only) */}
          {user?.role === 'student' && (
            <select
              value={status}
              onChange={(e) => setStatus(e.target.value)}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value="">All Status</option>
              <option value="not-started">Not Started</option>
              <option value="completed">Completed</option>
              <option value="passed">Passed</option>
              <option value="failed">Failed</option>
            </select>
          )}
        </div>
      </div>

      {/* Quiz Grid */}
      {filteredQuizzes && filteredQuizzes.length > 0 ? (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6"
        >
          {filteredQuizzes.map((quiz: any, index: any) => {
            const attempts = (userAttempts ?? []).filter((attempt: any) => attempt.quizId === quiz.id)
            const bestScore = attempts.length > 0 ? Math.max(...attempts.map((a: any) => a.score)) : undefined

            return (
              <motion.div
                key={quiz.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.1 }}
              >
                <QuizCard
                  quiz={quiz}
                  showEditButton={user?.role === 'teacher'}
                  showTakeButton={user?.role === 'student'}
                  userAttempts={attempts.length}
                  bestScore={bestScore}
                />
              </motion.div>
            )
          })}
        </motion.div>
      ) : (
        <div className="text-center py-12">
          <AcademicCapIcon className="w-16 h-16 mx-auto text-gray-300 mb-4" />
          <h3 className="text-xl font-medium text-gray-900 mb-2">No Quizzes Found</h3>
          <p className="text-gray-600 mb-6">
            {searchTerm || selectedCourse || difficulty || status
              ? 'No quizzes match your current filters.'
              : user?.role === 'teacher'
              ? 'You haven\'t created any quizzes yet.'
              : 'No quizzes are available at the moment.'
            }
          </p>
          
          {user?.role === 'teacher' && !searchTerm && !selectedCourse && (
            <Link href="/quizzes/create">
              <button className="flex items-center space-x-2 px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 mx-auto">
                <PlusIcon className="w-5 h-5" />
                <span>Create Your First Quiz</span>
              </button>
            </Link>
          )}
        </div>
      )}
    </div>
  )
}
