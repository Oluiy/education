'use client'

import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import Link from 'next/link'
import {
  ClipboardDocumentListIcon,
  PlusIcon,
  EyeIcon,
  PencilIcon,
  TrashIcon,
  ClockIcon,
  CheckCircleIcon,
  XCircleIcon,
  MagnifyingGlassIcon,
  ChartBarIcon,
  UserGroupIcon
} from '@heroicons/react/24/outline'

interface Quiz {
  id: string
  title: string
  description: string
  course_id: string
  course_name: string
  questions_count: number
  duration: number
  attempts_allowed: number
  pass_percentage: number
  status: 'draft' | 'published' | 'archived'
  created_at: string
  updated_at: string
  total_attempts: number
  avg_score: number
  students_completed: number
  students_enrolled: number
}

interface Course {
  id: string
  name: string
  code: string
  students_enrolled: number
}

export default function TeacherQuizzesPage() {
  const [quizzes, setQuizzes] = useState<Quiz[]>([])
  const [courses, setCourses] = useState<Course[]>([])
  const [loading, setLoading] = useState(true)
  const [searchTerm, setSearchTerm] = useState('')
  const [selectedCourse, setSelectedCourse] = useState('all')
  const [statusFilter, setStatusFilter] = useState('all')

  useEffect(() => {
    fetchQuizzesData()
  }, [])

  const fetchQuizzesData = async () => {
    try {
      // Mock data - replace with actual API calls
      const mockCourses: Course[] = [
        { id: '1', name: 'Advanced Mathematics', code: 'MATH301', students_enrolled: 45 },
        { id: '2', name: 'Physics Fundamentals', code: 'PHY101', students_enrolled: 38 },
        { id: '3', name: 'Chemistry Basics', code: 'CHEM100', students_enrolled: 42 },
        { id: '4', name: 'Biology Essentials', code: 'BIO150', students_enrolled: 31 }
      ]

      const mockQuizzes: Quiz[] = [
        {
          id: '1',
          title: 'Calculus Fundamentals',
          description: 'Test your understanding of basic calculus concepts',
          course_id: '1',
          course_name: 'Advanced Mathematics',
          questions_count: 15,
          duration: 30,
          attempts_allowed: 3,
          pass_percentage: 70,
          status: 'published',
          created_at: '2024-01-15T10:00:00Z',
          updated_at: '2024-01-15T10:00:00Z',
          total_attempts: 134,
          avg_score: 78.5,
          students_completed: 42,
          students_enrolled: 45
        },
        {
          id: '2',
          title: 'Physics Laws Quiz',
          description: 'Quiz on fundamental physics laws and principles',
          course_id: '2',
          course_name: 'Physics Fundamentals',
          questions_count: 20,
          duration: 45,
          attempts_allowed: 2,
          pass_percentage: 75,
          status: 'published',
          created_at: '2024-01-10T14:00:00Z',
          updated_at: '2024-01-10T14:00:00Z',
          total_attempts: 76,
          avg_score: 82.3,
          students_completed: 35,
          students_enrolled: 38
        },
        {
          id: '3',
          title: 'Chemical Reactions',
          description: 'Test your knowledge of chemical reaction types',
          course_id: '3',
          course_name: 'Chemistry Basics',
          questions_count: 12,
          duration: 25,
          attempts_allowed: 1,
          pass_percentage: 80,
          status: 'draft',
          created_at: '2024-01-08T09:00:00Z',
          updated_at: '2024-01-08T09:00:00Z',
          total_attempts: 0,
          avg_score: 0,
          students_completed: 0,
          students_enrolled: 42
        },
        {
          id: '4',
          title: 'Organic Chemistry Basics',
          description: 'Introduction to organic chemistry compounds',
          course_id: '3',
          course_name: 'Chemistry Basics',
          questions_count: 18,
          duration: 40,
          attempts_allowed: 2,
          pass_percentage: 75,
          status: 'published',
          created_at: '2024-01-05T11:30:00Z',
          updated_at: '2024-01-05T11:30:00Z',
          total_attempts: 89,
          avg_score: 74.2,
          students_completed: 38,
          students_enrolled: 42
        }
      ]

      setCourses(mockCourses)
      setQuizzes(mockQuizzes)
      setLoading(false)
    } catch (error) {
      console.error('Error fetching quizzes:', error)
      setLoading(false)
    }
  }

  const filteredQuizzes = quizzes.filter(quiz => {
    const matchesSearch = quiz.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         quiz.course_name.toLowerCase().includes(searchTerm.toLowerCase())
    const matchesCourse = selectedCourse === 'all' || quiz.course_id === selectedCourse
    const matchesStatus = statusFilter === 'all' || quiz.status === statusFilter
    return matchesSearch && matchesCourse && matchesStatus
  })

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'published':
        return 'bg-green-100 text-green-800'
      case 'draft':
        return 'bg-yellow-100 text-yellow-800'
      case 'archived':
        return 'bg-gray-100 text-gray-800'
      default:
        return 'bg-gray-100 text-gray-800'
    }
  }

  const formatDuration = (minutes: number) => {
    if (minutes >= 60) {
      const hours = Math.floor(minutes / 60)
      const mins = minutes % 60
      return mins > 0 ? `${hours}h ${mins}m` : `${hours}h`
    }
    return `${minutes}m`
  }

  const getCompletionRate = (quiz: Quiz) => {
    if (quiz.students_enrolled === 0) return 0
    return Math.round((quiz.students_completed / quiz.students_enrolled) * 100)
  }

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric'
    })
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

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4 sm:py-8">
        {/* Header */}
        <div className="mb-8">
          <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between mb-6 gap-4">
            <div>
              <h1 className="text-2xl sm:text-3xl font-bold text-gray-900">Quiz Management</h1>
              <p className="text-gray-600 mt-1">Create and manage quizzes for your courses</p>
            </div>
            <Link href="/teacher/dashboard/quizzes/create">
              <button className="btn-primary flex items-center justify-center space-x-2 w-full sm:w-auto">
                <PlusIcon className="w-5 h-5" />
                <span>Create Quiz</span>
              </button>
            </Link>
          </div>

          {/* Search and Filter */}
          <div className="flex flex-col sm:flex-row gap-4">
            <div className="relative flex-1">
              <MagnifyingGlassIcon className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
              <input
                type="text"
                placeholder="Search quizzes or courses..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-10 pr-4 py-2 w-full border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
              />
            </div>
            <select
              value={selectedCourse}
              onChange={(e) => setSelectedCourse(e.target.value)}
              className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
            >
              <option value="all">All Courses</option>
              {courses.map((course) => (
                <option key={course.id} value={course.id}>
                  {course.name} ({course.code})
                </option>
              ))}
            </select>
            <select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
              className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
            >
              <option value="all">All Status</option>
              <option value="published">Published</option>
              <option value="draft">Draft</option>
              <option value="archived">Archived</option>
            </select>
          </div>
        </div>

        {/* Quizzes List */}
        <div className="space-y-4">
          {filteredQuizzes.map((quiz, index) => (
            <motion.div
              key={quiz.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.1 }}
              className="bg-white rounded-xl shadow-soft border border-gray-200 p-4 sm:p-6 hover:shadow-strong transition-shadow duration-200"
            >
              <div className="flex flex-col lg:flex-row lg:items-start lg:justify-between gap-4">
                <div className="flex-1">
                  <div className="flex flex-col sm:flex-row sm:items-center gap-2 sm:gap-3 mb-2">
                    <h3 className="text-lg font-semibold text-gray-900">{quiz.title}</h3>
                    <span className={`px-3 py-1 rounded-full text-xs font-medium w-fit ${getStatusColor(quiz.status)}`}>
                      {quiz.status}
                    </span>
                  </div>
                  
                  <p className="text-gray-600 mb-3">{quiz.description}</p>
                  
                  <div className="flex flex-wrap items-center gap-4 sm:gap-6 text-sm text-gray-500 mb-4">
                    <div className="flex items-center gap-1">
                      <ClipboardDocumentListIcon className="w-4 h-4 flex-shrink-0" />
                      <span className="truncate">{quiz.course_name}</span>
                    </div>
                    <div className="flex items-center gap-1">
                      <ClockIcon className="w-4 h-4 flex-shrink-0" />
                      <span>{formatDuration(quiz.duration)}</span>
                    </div>
                    <div className="flex items-center gap-1">
                      <span>{quiz.questions_count} questions</span>
                    </div>
                    <div className="flex items-center gap-1">
                      <span>Created {formatDate(quiz.created_at)}</span>
                    </div>
                  </div>

                  {quiz.status === 'published' && (
                    <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 text-sm">
                      <div className="flex items-center gap-1">
                        <UserGroupIcon className="w-4 h-4 text-blue-500 flex-shrink-0" />
                        <div>
                          <p className="font-medium text-gray-900">{quiz.students_completed}/{quiz.students_enrolled}</p>
                          <p className="text-gray-600">Completed</p>
                        </div>
                      </div>
                      <div className="flex items-center gap-1">
                        <ChartBarIcon className="w-4 h-4 text-green-500 flex-shrink-0" />
                        <div>
                          <p className="font-medium text-gray-900">{quiz.avg_score.toFixed(1)}%</p>
                          <p className="text-gray-600">Avg Score</p>
                        </div>
                      </div>
                      <div className="flex items-center gap-1">
                        <CheckCircleIcon className="w-4 h-4 text-purple-500 flex-shrink-0" />
                        <div>
                          <p className="font-medium text-gray-900">{getCompletionRate(quiz)}%</p>
                          <p className="text-gray-600">Completion</p>
                        </div>
                      </div>
                      <div className="flex items-center gap-1">
                        <ClipboardDocumentListIcon className="w-4 h-4 text-orange-500 flex-shrink-0" />
                        <div>
                          <p className="font-medium text-gray-900">{quiz.total_attempts}</p>
                          <p className="text-gray-600">Attempts</p>
                        </div>
                      </div>
                    </div>
                  )}

                  {quiz.status === 'draft' && (
                    <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-3">
                      <p className="text-sm text-yellow-800">
                        This quiz is in draft mode. Publish it to make it available to students.
                      </p>
                    </div>
                  )}
                </div>

                <div className="flex flex-wrap sm:flex-nowrap items-center gap-2">
                  <Link href={`/teacher/dashboard/quizzes/${quiz.id}`} className="flex-1 sm:flex-none">
                    <button className="flex items-center justify-center gap-1 px-3 py-1.5 text-sm bg-primary-100 text-primary-700 rounded-lg hover:bg-primary-200 transition-colors w-full sm:w-auto">
                      <EyeIcon className="w-4 h-4" />
                      <span className="hidden sm:inline">View</span>
                    </button>
                  </Link>
                  <Link href={`/teacher/dashboard/quizzes/${quiz.id}/edit`} className="flex-1 sm:flex-none">
                    <button className="flex items-center justify-center gap-1 px-3 py-1.5 text-sm bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors w-full sm:w-auto">
                      <PencilIcon className="w-4 h-4" />
                      <span className="hidden sm:inline">Edit</span>
                    </button>
                  </Link>
                  {quiz.status === 'published' && (
                    <Link href={`/teacher/dashboard/quizzes/${quiz.id}/results`} className="flex-1 sm:flex-none">
                      <button className="flex items-center justify-center gap-1 px-3 py-1.5 text-sm bg-blue-100 text-blue-700 rounded-lg hover:bg-blue-200 transition-colors w-full sm:w-auto">
                        <ChartBarIcon className="w-4 h-4" />
                        <span className="hidden sm:inline">Results</span>
                      </button>
                    </Link>
                  )}
                  <button className="flex items-center justify-center gap-1 px-3 py-1.5 text-sm bg-red-100 text-red-700 rounded-lg hover:bg-red-200 transition-colors flex-1 sm:flex-none w-full sm:w-auto">
                    <TrashIcon className="w-4 h-4" />
                    <span className="hidden sm:inline">Delete</span>
                  </button>
                </div>
              </div>
            </motion.div>
          ))}
        </div>

        {filteredQuizzes.length === 0 && (
          <div className="text-center py-12 px-4">
            <ClipboardDocumentListIcon className="w-12 h-12 sm:w-16 sm:h-16 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">No quizzes found</h3>
            <p className="text-gray-600 mb-4 text-sm sm:text-base">
              {searchTerm || selectedCourse !== 'all' || statusFilter !== 'all'
                ? 'Try adjusting your search or filter criteria'
                : 'Create your first quiz to get started'}
            </p>
            {!searchTerm && selectedCourse === 'all' && statusFilter === 'all' && (
              <Link href="/teacher/dashboard/quizzes/create">
                <button className="btn-primary inline-flex items-center">
                  <PlusIcon className="w-5 h-5 mr-2" />
                  Create Your First Quiz
                </button>
              </Link>
            )}
          </div>
        )}
      </div>
    </div>
  )
}
