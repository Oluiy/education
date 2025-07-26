'use client'

import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import Link from 'next/link'
import {
  AcademicCapIcon,
  UserGroupIcon,
  DocumentTextIcon,
  ClipboardDocumentListIcon,
  ChartBarIcon,
  PlusIcon,
  ArrowTrendingUpIcon,
  BookOpenIcon,
  ClockIcon,
  CheckCircleIcon,
  ExclamationTriangleIcon
} from '@heroicons/react/24/outline'

interface Course {
  id: string
  title: string
  code: string
  students_enrolled: number
  total_assignments: number
  total_quizzes: number
  avg_completion_rate: number
  last_activity: string
}

interface StudentProgress {
  student_id: string
  student_name: string
  progress_percentage: number
  last_active: string
  status: 'active' | 'inactive' | 'at_risk'
}

interface DashboardStats {
  total_students: number
  total_courses: number
  pending_submissions: number
  avg_class_performance: number
}

export default function TeacherDashboard() {
  const [courses, setCourses] = useState<Course[]>([])
  const [recentActivity, setRecentActivity] = useState<StudentProgress[]>([])
  const [stats, setStats] = useState<DashboardStats | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchDashboardData()
  }, [])

  const fetchDashboardData = async () => {
    try {
      // Mock data - replace with actual API calls
      const mockStats: DashboardStats = {
        total_students: 156,
        total_courses: 4,
        pending_submissions: 23,
        avg_class_performance: 78.5
      }

      const mockCourses: Course[] = [
        {
          id: '1',
          title: 'Advanced Mathematics',
          code: 'MATH301',
          students_enrolled: 45,
          total_assignments: 8,
          total_quizzes: 12,
          avg_completion_rate: 82.5,
          last_activity: '2024-01-15T10:30:00Z'
        },
        {
          id: '2',
          title: 'Physics Fundamentals',
          code: 'PHY101',
          students_enrolled: 38,
          total_assignments: 6,
          total_quizzes: 10,
          avg_completion_rate: 76.8,
          last_activity: '2024-01-14T15:45:00Z'
        },
        {
          id: '3',
          title: 'Chemistry Basics',
          code: 'CHEM100',
          students_enrolled: 42,
          total_assignments: 7,
          total_quizzes: 9,
          avg_completion_rate: 84.2,
          last_activity: '2024-01-13T09:20:00Z'
        },
        {
          id: '4',
          title: 'Biology Essentials',
          code: 'BIO150',
          students_enrolled: 31,
          total_assignments: 5,
          total_quizzes: 8,
          avg_completion_rate: 79.1,
          last_activity: '2024-01-12T14:10:00Z'
        }
      ]

      const mockRecentActivity: StudentProgress[] = [
        {
          student_id: '1',
          student_name: 'Emily Johnson',
          progress_percentage: 92,
          last_active: '2024-01-15T11:00:00Z',
          status: 'active'
        },
        {
          student_id: '2',
          student_name: 'Michael Chen',
          progress_percentage: 45,
          last_active: '2024-01-10T16:30:00Z',
          status: 'at_risk'
        },
        {
          student_id: '3',
          student_name: 'Sarah Williams',
          progress_percentage: 78,
          last_active: '2024-01-14T09:15:00Z',
          status: 'active'
        },
        {
          student_id: '4',
          student_name: 'David Brown',
          progress_percentage: 23,
          last_active: '2024-01-08T13:45:00Z',
          status: 'inactive'
        }
      ]

      setStats(mockStats)
      setCourses(mockCourses)
      setRecentActivity(mockRecentActivity)
      setLoading(false)
    } catch (error) {
      console.error('Error fetching dashboard data:', error)
      setLoading(false)
    }
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active':
        return 'bg-green-100 text-green-800'
      case 'at_risk':
        return 'bg-yellow-100 text-yellow-800'
      case 'inactive':
        return 'bg-red-100 text-red-800'
      default:
        return 'bg-gray-100 text-gray-800'
    }
  }

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
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
          <h1 className="text-2xl sm:text-3xl font-bold text-gray-900">Teacher Dashboard</h1>
          <p className="text-gray-600 mt-1">Manage your courses and track student progress</p>
        </div>

        {/* Stats Overview */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 sm:gap-6 mb-8">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
            className="bg-white rounded-xl shadow-soft border border-gray-200 p-6"
          >
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <UserGroupIcon className="h-8 w-8 text-blue-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Total Students</p>
                <p className="text-2xl font-bold text-gray-900">{stats?.total_students}</p>
              </div>
            </div>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
            className="bg-white rounded-xl shadow-soft border border-gray-200 p-6"
          >
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <BookOpenIcon className="h-8 w-8 text-green-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Active Courses</p>
                <p className="text-2xl font-bold text-gray-900">{stats?.total_courses}</p>
              </div>
            </div>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3 }}
            className="bg-white rounded-xl shadow-soft border border-gray-200 p-6"
          >
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <ClockIcon className="h-8 w-8 text-yellow-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Pending Reviews</p>
                <p className="text-2xl font-bold text-gray-900">{stats?.pending_submissions}</p>
              </div>
            </div>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.4 }}
            className="bg-white rounded-xl shadow-soft border border-gray-200 p-6"
          >
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <ArrowTrendingUpIcon className="h-8 w-8 text-purple-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Avg Performance</p>
                <p className="text-2xl font-bold text-gray-900">{stats?.avg_class_performance}%</p>
              </div>
            </div>
          </motion.div>
        </div>

        {/* Quick Actions */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
          <Link href="/teacher/dashboard/analytics">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.5 }}
              className="bg-white rounded-xl shadow-soft border border-gray-200 p-6 hover:shadow-strong transition-shadow cursor-pointer"
            >
              <div className="flex items-center">
                <ChartBarIcon className="h-8 w-8 text-blue-600" />
                <div className="ml-4">
                  <h3 className="text-lg font-semibold text-gray-900">Analytics</h3>
                  <p className="text-sm text-gray-600">View detailed insights</p>
                </div>
              </div>
            </motion.div>
          </Link>

          <Link href="/teacher/dashboard/resources">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.6 }}
              className="bg-white rounded-xl shadow-soft border border-gray-200 p-6 hover:shadow-strong transition-shadow cursor-pointer"
            >
              <div className="flex items-center">
                <DocumentTextIcon className="h-8 w-8 text-green-600" />
                <div className="ml-4">
                  <h3 className="text-lg font-semibold text-gray-900">Resources</h3>
                  <p className="text-sm text-gray-600">Upload materials</p>
                </div>
              </div>
            </motion.div>
          </Link>

          <Link href="/teacher/dashboard/quizzes">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.7 }}
              className="bg-white rounded-xl shadow-soft border border-gray-200 p-6 hover:shadow-strong transition-shadow cursor-pointer"
            >
              <div className="flex items-center">
                <ClipboardDocumentListIcon className="h-8 w-8 text-purple-600" />
                <div className="ml-4">
                  <h3 className="text-lg font-semibold text-gray-900">Quizzes</h3>
                  <p className="text-sm text-gray-600">Create assessments</p>
                </div>
              </div>
            </motion.div>
          </Link>

          <Link href="/teacher/dashboard/assignments">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.8 }}
              className="bg-white rounded-xl shadow-soft border border-gray-200 p-6 hover:shadow-strong transition-shadow cursor-pointer"
            >
              <div className="flex items-center">
                <AcademicCapIcon className="h-8 w-8 text-orange-600" />
                <div className="ml-4">
                  <h3 className="text-lg font-semibold text-gray-900">Assignments</h3>
                  <p className="text-sm text-gray-600">Manage tasks</p>
                </div>
              </div>
            </motion.div>
          </Link>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* My Courses */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.9 }}
            className="bg-white rounded-xl shadow-soft border border-gray-200 p-6"
          >
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-xl font-bold text-gray-900">My Courses</h2>
              <Link href="/teacher/dashboard/courses">
                <span className="text-primary-600 hover:text-primary-700 text-sm font-medium">View All</span>
              </Link>
            </div>
            <div className="space-y-4">
              {courses.slice(0, 3).map((course) => (
                <div key={course.id} className="border border-gray-200 rounded-lg p-4">
                  <div className="flex items-start justify-between mb-2">
                    <div>
                      <h3 className="font-semibold text-gray-900">{course.title}</h3>
                      <p className="text-sm text-gray-600">{course.code}</p>
                    </div>
                    <Link href={`/teacher/dashboard/courses/${course.id}`}>
                      <button className="text-primary-600 hover:text-primary-700 text-sm">View</button>
                    </Link>
                  </div>
                  <div className="flex items-center justify-between text-sm text-gray-600">
                    <span>{course.students_enrolled} students</span>
                    <span>{course.avg_completion_rate}% completion</span>
                  </div>
                </div>
              ))}
            </div>
          </motion.div>

          {/* Recent Student Activity */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 1.0 }}
            className="bg-white rounded-xl shadow-soft border border-gray-200 p-6"
          >
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-xl font-bold text-gray-900">Student Progress</h2>
              <Link href="/teacher/dashboard/students">
                <span className="text-primary-600 hover:text-primary-700 text-sm font-medium">View All</span>
              </Link>
            </div>
            <div className="space-y-4">
              {recentActivity.map((student) => (
                <div key={student.student_id} className="flex items-center justify-between py-3">
                  <div className="flex items-center space-x-3">
                    <div className="flex-shrink-0">
                      <div className="h-10 w-10 rounded-full bg-gray-300 flex items-center justify-center">
                        <span className="text-sm font-medium text-gray-700">
                          {student.student_name.charAt(0)}
                        </span>
                      </div>
                    </div>
                    <div>
                      <p className="text-sm font-medium text-gray-900">{student.student_name}</p>
                      <p className="text-xs text-gray-500">Last active: {formatDate(student.last_active)}</p>
                    </div>
                  </div>
                  <div className="flex items-center space-x-2">
                    <div className="text-right">
                      <p className="text-sm font-medium text-gray-900">{student.progress_percentage}%</p>
                      <span className={`inline-flex px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(student.status)}`}>
                        {student.status}
                      </span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </motion.div>
        </div>
      </div>
    </div>
  )
}
