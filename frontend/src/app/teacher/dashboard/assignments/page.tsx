'use client'

import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import Link from 'next/link'
import {
  AcademicCapIcon,
  PlusIcon,
  EyeIcon,
  PencilIcon,
  TrashIcon,
  ClockIcon,
  CheckCircleIcon,
  ExclamationTriangleIcon,
  MagnifyingGlassIcon,
  UserGroupIcon,
  DocumentTextIcon,
  CalendarIcon
} from '@heroicons/react/24/outline'

interface Assignment {
  id: string
  title: string
  description: string
  course_id: string
  course_name: string
  due_date: string
  max_points: number
  status: 'draft' | 'published' | 'closed'
  created_at: string
  updated_at: string
  submissions_count: number
  graded_count: number
  students_enrolled: number
  avg_score: number
  instructions: string
  attachment_url?: string
}

interface Course {
  id: string
  name: string
  code: string
  students_enrolled: number
}

export default function TeacherAssignmentsPage() {
  const [assignments, setAssignments] = useState<Assignment[]>([])
  const [courses, setCourses] = useState<Course[]>([])
  const [loading, setLoading] = useState(true)
  const [searchTerm, setSearchTerm] = useState('')
  const [selectedCourse, setSelectedCourse] = useState('all')
  const [statusFilter, setStatusFilter] = useState('all')

  useEffect(() => {
    fetchAssignmentsData()
  }, [])

  const fetchAssignmentsData = async () => {
    try {
      // Mock data - replace with actual API calls
      const mockCourses: Course[] = [
        { id: '1', name: 'Advanced Mathematics', code: 'MATH301', students_enrolled: 45 },
        { id: '2', name: 'Physics Fundamentals', code: 'PHY101', students_enrolled: 38 },
        { id: '3', name: 'Chemistry Basics', code: 'CHEM100', students_enrolled: 42 },
        { id: '4', name: 'Biology Essentials', code: 'BIO150', students_enrolled: 31 }
      ]

      const mockAssignments: Assignment[] = [
        {
          id: '1',
          title: 'Calculus Problem Set 1',
          description: 'Solve differentiation and integration problems',
          course_id: '1',
          course_name: 'Advanced Mathematics',
          due_date: '2024-01-25T23:59:00Z',
          max_points: 100,
          status: 'published',
          created_at: '2024-01-15T10:00:00Z',
          updated_at: '2024-01-15T10:00:00Z',
          submissions_count: 42,
          graded_count: 35,
          students_enrolled: 45,
          avg_score: 85.2,
          instructions: 'Complete all problems showing your work. Submit as PDF.',
          attachment_url: '/assignments/calculus-problems.pdf'
        },
        {
          id: '2',
          title: 'Physics Lab Report',
          description: 'Analysis of pendulum motion experiment',
          course_id: '2',
          course_name: 'Physics Fundamentals',
          due_date: '2024-01-30T23:59:00Z',
          max_points: 75,
          status: 'published',
          created_at: '2024-01-12T14:00:00Z',
          updated_at: '2024-01-12T14:00:00Z',
          submissions_count: 28,
          graded_count: 20,
          students_enrolled: 38,
          avg_score: 78.5,
          instructions: 'Write a comprehensive lab report including methodology, results, and conclusion.',
          attachment_url: '/assignments/lab-report-template.docx'
        },
        {
          id: '3',
          title: 'Chemical Equation Balancing',
          description: 'Balance complex chemical equations and explain stoichiometry',
          course_id: '3',
          course_name: 'Chemistry Basics',
          due_date: '2024-02-05T23:59:00Z',
          max_points: 50,
          status: 'draft',
          created_at: '2024-01-18T09:00:00Z',
          updated_at: '2024-01-18T09:00:00Z',
          submissions_count: 0,
          graded_count: 0,
          students_enrolled: 42,
          avg_score: 0,
          instructions: 'Balance the provided chemical equations and explain the stoichiometry principles.'
        },
        {
          id: '4',
          title: 'Cell Structure Essay',
          description: 'Write an essay on prokaryotic vs eukaryotic cells',
          course_id: '4',
          course_name: 'Biology Essentials',
          due_date: '2024-01-28T23:59:00Z',
          max_points: 80,
          status: 'published',
          created_at: '2024-01-10T11:30:00Z',
          updated_at: '2024-01-10T11:30:00Z',
          submissions_count: 31,
          graded_count: 31,
          students_enrolled: 31,
          avg_score: 82.7,
          instructions: 'Write a 1000-word essay comparing prokaryotic and eukaryotic cells.'
        }
      ]

      setCourses(mockCourses)
      setAssignments(mockAssignments)
      setLoading(false)
    } catch (error) {
      console.error('Error fetching assignments:', error)
      setLoading(false)
    }
  }

  const filteredAssignments = assignments.filter(assignment => {
    const matchesSearch = assignment.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         assignment.course_name.toLowerCase().includes(searchTerm.toLowerCase())
    const matchesCourse = selectedCourse === 'all' || assignment.course_id === selectedCourse
    const matchesStatus = statusFilter === 'all' || assignment.status === statusFilter
    return matchesSearch && matchesCourse && matchesStatus
  })

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'published':
        return 'bg-green-100 text-green-800'
      case 'draft':
        return 'bg-yellow-100 text-yellow-800'
      case 'closed':
        return 'bg-gray-100 text-gray-800'
      default:
        return 'bg-gray-100 text-gray-800'
    }
  }

  const getDaysUntilDue = (dueDate: string) => {
    const due = new Date(dueDate)
    const now = new Date()
    const diffTime = due.getTime() - now.getTime()
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24))
    return diffDays
  }

  const getSubmissionRate = (assignment: Assignment) => {
    if (assignment.students_enrolled === 0) return 0
    return Math.round((assignment.submissions_count / assignment.students_enrolled) * 100)
  }

  const getGradingProgress = (assignment: Assignment) => {
    if (assignment.submissions_count === 0) return 100
    return Math.round((assignment.graded_count / assignment.submissions_count) * 100)
  }

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    })
  }

  const getDueDateStatus = (dueDate: string) => {
    const daysUntil = getDaysUntilDue(dueDate)
    if (daysUntil < 0) return { color: 'text-red-600', text: 'Overdue' }
    if (daysUntil === 0) return { color: 'text-orange-600', text: 'Due today' }
    if (daysUntil <= 3) return { color: 'text-yellow-600', text: `Due in ${daysUntil} day${daysUntil > 1 ? 's' : ''}` }
    return { color: 'text-gray-600', text: `Due in ${daysUntil} days` }
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
              <h1 className="text-2xl sm:text-3xl font-bold text-gray-900">Assignment Management</h1>
              <p className="text-gray-600 mt-1">Create and manage assignments for your courses</p>
            </div>
            <Link href="/teacher/dashboard/assignments/create">
              <button className="btn-primary flex items-center justify-center space-x-2 w-full sm:w-auto">
                <PlusIcon className="w-5 h-5" />
                <span>Create Assignment</span>
              </button>
            </Link>
          </div>

          {/* Search and Filter */}
          <div className="flex flex-col sm:flex-row gap-4">
            <div className="relative flex-1">
              <MagnifyingGlassIcon className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
              <input
                type="text"
                placeholder="Search assignments or courses..."
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
              <option value="closed">Closed</option>
            </select>
          </div>
        </div>

        {/* Assignments List */}
        <div className="space-y-4">
          {filteredAssignments.map((assignment, index) => (
            <motion.div
              key={assignment.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.1 }}
              className="bg-white rounded-xl shadow-soft border border-gray-200 p-4 sm:p-6 hover:shadow-strong transition-shadow duration-200"
            >
              <div className="flex flex-col lg:flex-row lg:items-start lg:justify-between gap-4">
                <div className="flex-1">
                  <div className="flex flex-col sm:flex-row sm:items-center gap-2 sm:gap-3 mb-2">
                    <h3 className="text-lg font-semibold text-gray-900">{assignment.title}</h3>
                    <span className={`px-3 py-1 rounded-full text-xs font-medium w-fit ${getStatusColor(assignment.status)}`}>
                      {assignment.status}
                    </span>
                  </div>
                  
                  <p className="text-gray-600 mb-3">{assignment.description}</p>
                  
                  <div className="flex flex-wrap items-center gap-4 sm:gap-6 text-sm text-gray-500 mb-4">
                    <div className="flex items-center gap-1">
                      <AcademicCapIcon className="w-4 h-4 flex-shrink-0" />
                      <span className="truncate">{assignment.course_name}</span>
                    </div>
                    <div className="flex items-center gap-1">
                      <CalendarIcon className="w-4 h-4 flex-shrink-0" />
                      <span className={getDueDateStatus(assignment.due_date).color}>
                        {getDueDateStatus(assignment.due_date).text}
                      </span>
                    </div>
                    <div className="flex items-center gap-1">
                      <span>{assignment.max_points} points</span>
                    </div>
                    {assignment.attachment_url && (
                      <div className="flex items-center gap-1">
                        <DocumentTextIcon className="w-4 h-4 flex-shrink-0" />
                        <span>Has attachment</span>
                      </div>
                    )}
                  </div>

                  {assignment.status === 'published' && (
                    <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 text-sm">
                      <div className="flex items-center gap-1">
                        <UserGroupIcon className="w-4 h-4 text-blue-500 flex-shrink-0" />
                        <div>
                          <p className="font-medium text-gray-900">{assignment.submissions_count}/{assignment.students_enrolled}</p>
                          <p className="text-gray-600">Submitted</p>
                        </div>
                      </div>
                      <div className="flex items-center gap-1">
                        <CheckCircleIcon className="w-4 h-4 text-green-500 flex-shrink-0" />
                        <div>
                          <p className="font-medium text-gray-900">{getGradingProgress(assignment)}%</p>
                          <p className="text-gray-600">Graded</p>
                        </div>
                      </div>
                      <div className="flex items-center gap-1">
                        <ClockIcon className="w-4 h-4 text-purple-500 flex-shrink-0" />
                        <div>
                          <p className="font-medium text-gray-900">{getSubmissionRate(assignment)}%</p>
                          <p className="text-gray-600">Submission Rate</p>
                        </div>
                      </div>
                      <div className="flex items-center gap-1">
                        <AcademicCapIcon className="w-4 h-4 text-orange-500 flex-shrink-0" />
                        <div>
                          <p className="font-medium text-gray-900">{assignment.avg_score.toFixed(1)}%</p>
                          <p className="text-gray-600">Avg Score</p>
                        </div>
                      </div>
                    </div>
                  )}

                  {assignment.status === 'draft' && (
                    <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-3">
                      <p className="text-sm text-yellow-800">
                        This assignment is in draft mode. Publish it to make it available to students.
                      </p>
                    </div>
                  )}

                  {assignment.status === 'published' && assignment.graded_count < assignment.submissions_count && (
                    <div className="bg-blue-50 border border-blue-200 rounded-lg p-3 mt-3">
                      <div className="flex items-center gap-2">
                        <ExclamationTriangleIcon className="w-4 h-4 text-blue-600" />
                        <p className="text-sm text-blue-800">
                          {assignment.submissions_count - assignment.graded_count} submissions need grading
                        </p>
                      </div>
                    </div>
                  )}
                </div>

                <div className="flex flex-wrap sm:flex-nowrap items-center gap-2">
                  <Link href={`/teacher/dashboard/assignments/${assignment.id}`} className="flex-1 sm:flex-none">
                    <button className="flex items-center justify-center gap-1 px-3 py-1.5 text-sm bg-primary-100 text-primary-700 rounded-lg hover:bg-primary-200 transition-colors w-full sm:w-auto">
                      <EyeIcon className="w-4 h-4" />
                      <span className="hidden sm:inline">View</span>
                    </button>
                  </Link>
                  <Link href={`/teacher/dashboard/assignments/${assignment.id}/edit`} className="flex-1 sm:flex-none">
                    <button className="flex items-center justify-center gap-1 px-3 py-1.5 text-sm bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors w-full sm:w-auto">
                      <PencilIcon className="w-4 h-4" />
                      <span className="hidden sm:inline">Edit</span>
                    </button>
                  </Link>
                  {assignment.status === 'published' && (
                    <Link href={`/teacher/dashboard/assignments/${assignment.id}/submissions`} className="flex-1 sm:flex-none">
                      <button className="flex items-center justify-center gap-1 px-3 py-1.5 text-sm bg-blue-100 text-blue-700 rounded-lg hover:bg-blue-200 transition-colors w-full sm:w-auto">
                        <CheckCircleIcon className="w-4 h-4" />
                        <span className="hidden sm:inline">Grade</span>
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

        {filteredAssignments.length === 0 && (
          <div className="text-center py-12 px-4">
            <AcademicCapIcon className="w-12 h-12 sm:w-16 sm:h-16 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">No assignments found</h3>
            <p className="text-gray-600 mb-4 text-sm sm:text-base">
              {searchTerm || selectedCourse !== 'all' || statusFilter !== 'all'
                ? 'Try adjusting your search or filter criteria'
                : 'Create your first assignment to get started'}
            </p>
            {!searchTerm && selectedCourse === 'all' && statusFilter === 'all' && (
              <Link href="/teacher/dashboard/assignments/create">
                <button className="btn-primary inline-flex items-center">
                  <PlusIcon className="w-5 h-5 mr-2" />
                  Create Your First Assignment
                </button>
              </Link>
            )}
          </div>
        )}
      </div>
    </div>
  )
}
