'use client'

import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import {
  ChartBarIcon,
  AcademicCapIcon,
  UserGroupIcon,
  ClockIcon,
  ArrowTrendingUpIcon,
  ArrowTrendingDownIcon,
  ArrowPathIcon
} from '@heroicons/react/24/outline'

interface CourseAnalytics {
  course_id: string
  course_name: string
  students_enrolled: number
  completion_rate: number
  avg_score: number
  quiz_attempts: number
  assignment_submissions: number
  engagement_score: number
  trend: 'up' | 'down' | 'stable'
}

interface StudentPerformance {
  student_id: string
  student_name: string
  courses: {
    course_id: string
    course_name: string
    progress: number
    last_activity: string
    performance_score: number
    status: 'excellent' | 'good' | 'needs_attention' | 'at_risk'
  }[]
}

interface AnalyticsOverview {
  total_engagement_hours: number
  avg_completion_time: number
  student_satisfaction: number
  resource_usage: number
  quiz_pass_rate: number
  assignment_submission_rate: number
}

export default function TeacherAnalyticsPage() {
  const [courseAnalytics, setCourseAnalytics] = useState<CourseAnalytics[]>([])
  const [studentPerformance, setStudentPerformance] = useState<StudentPerformance[]>([])
  const [overview, setOverview] = useState<AnalyticsOverview | null>(null)
  const [selectedCourse, setSelectedCourse] = useState<string>('all')
  const [timeRange, setTimeRange] = useState<'week' | 'month' | 'semester'>('month')
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchAnalyticsData()
  }, [selectedCourse, timeRange])

  const fetchAnalyticsData = async () => {
    setLoading(true)
    try {
      // Mock data - replace with actual API calls
      const mockOverview: AnalyticsOverview = {
        total_engagement_hours: 1245,
        avg_completion_time: 45.2,
        student_satisfaction: 4.2,
        resource_usage: 78.5,
        quiz_pass_rate: 82.3,
        assignment_submission_rate: 91.7
      }

      const mockCourseAnalytics: CourseAnalytics[] = [
        {
          course_id: '1',
          course_name: 'Advanced Mathematics',
          students_enrolled: 45,
          completion_rate: 82.5,
          avg_score: 78.2,
          quiz_attempts: 234,
          assignment_submissions: 187,
          engagement_score: 85.3,
          trend: 'up'
        },
        {
          course_id: '2',
          course_name: 'Physics Fundamentals',
          students_enrolled: 38,
          completion_rate: 76.8,
          avg_score: 74.1,
          quiz_attempts: 195,
          assignment_submissions: 142,
          engagement_score: 79.2,
          trend: 'stable'
        },
        {
          course_id: '3',
          course_name: 'Chemistry Basics',
          students_enrolled: 42,
          completion_rate: 84.2,
          avg_score: 81.5,
          quiz_attempts: 218,
          assignment_submissions: 165,
          engagement_score: 88.1,
          trend: 'up'
        },
        {
          course_id: '4',
          course_name: 'Biology Essentials',
          students_enrolled: 31,
          completion_rate: 79.1,
          avg_score: 76.8,
          quiz_attempts: 157,
          assignment_submissions: 124,
          engagement_score: 82.4,
          trend: 'down'
        }
      ]

      const mockStudentPerformance: StudentPerformance[] = [
        {
          student_id: '1',
          student_name: 'Emily Johnson',
          courses: [
            {
              course_id: '1',
              course_name: 'Advanced Mathematics',
              progress: 92,
              last_activity: '2024-01-15T11:00:00Z',
              performance_score: 89,
              status: 'excellent'
            },
            {
              course_id: '2',
              course_name: 'Physics Fundamentals',
              progress: 87,
              last_activity: '2024-01-14T15:30:00Z',
              performance_score: 84,
              status: 'good'
            }
          ]
        },
        {
          student_id: '2',
          student_name: 'Michael Chen',
          courses: [
            {
              course_id: '1',
              course_name: 'Advanced Mathematics',
              progress: 45,
              last_activity: '2024-01-10T16:30:00Z',
              performance_score: 52,
              status: 'at_risk'
            }
          ]
        },
        {
          student_id: '3',
          student_name: 'Sarah Williams',
          courses: [
            {
              course_id: '3',
              course_name: 'Chemistry Basics',
              progress: 78,
              last_activity: '2024-01-14T09:15:00Z',
              performance_score: 81,
              status: 'good'
            }
          ]
        }
      ]

      setOverview(mockOverview)
      setCourseAnalytics(mockCourseAnalytics)
      setStudentPerformance(mockStudentPerformance)
      setLoading(false)
    } catch (error) {
      console.error('Error fetching analytics data:', error)
      setLoading(false)
    }
  }

  const getTrendIcon = (trend: string) => {
    switch (trend) {
      case 'up':
        return <ArrowTrendingUpIcon className="w-4 h-4 text-green-500" />
      case 'down':
        return <ArrowTrendingDownIcon className="w-4 h-4 text-red-500" />
      default:
        return <ArrowPathIcon className="w-4 h-4 text-gray-500" />
    }
  }

  const getPerformanceColor = (status: string) => {
    switch (status) {
      case 'excellent':
        return 'bg-green-100 text-green-800'
      case 'good':
        return 'bg-blue-100 text-blue-800'
      case 'needs_attention':
        return 'bg-yellow-100 text-yellow-800'
      case 'at_risk':
        return 'bg-red-100 text-red-800'
      default:
        return 'bg-gray-100 text-gray-800'
    }
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
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between mb-8 gap-4">
          <div>
            <h1 className="text-2xl sm:text-3xl font-bold text-gray-900">Analytics Dashboard</h1>
            <p className="text-gray-600 mt-1">Track student performance and engagement across your courses</p>
          </div>
          
          <div className="flex flex-col sm:flex-row gap-4">
            <select
              value={selectedCourse}
              onChange={(e) => setSelectedCourse(e.target.value)}
              className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
            >
              <option value="all">All Courses</option>
              {courseAnalytics.map((course) => (
                <option key={course.course_id} value={course.course_id}>
                  {course.course_name}
                </option>
              ))}
            </select>
            
            <select
              value={timeRange}
              onChange={(e) => setTimeRange(e.target.value as 'week' | 'month' | 'semester')}
              className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
            >
              <option value="week">This Week</option>
              <option value="month">This Month</option>
              <option value="semester">This Semester</option>
            </select>
          </div>
        </div>

        {/* Overview Metrics */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 sm:gap-6 mb-8">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
            className="bg-white rounded-xl shadow-soft border border-gray-200 p-6"
          >
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Engagement Hours</p>
                <p className="text-2xl font-bold text-gray-900">{overview?.total_engagement_hours}</p>
                <p className="text-xs text-gray-500 mt-1">Total student hours</p>
              </div>
              <ClockIcon className="h-8 w-8 text-blue-600" />
            </div>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
            className="bg-white rounded-xl shadow-soft border border-gray-200 p-6"
          >
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Quiz Pass Rate</p>
                <p className="text-2xl font-bold text-gray-900">{overview?.quiz_pass_rate}%</p>
                <p className="text-xs text-gray-500 mt-1">Students passing quizzes</p>
              </div>
              <ChartBarIcon className="h-8 w-8 text-green-600" />
            </div>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3 }}
            className="bg-white rounded-xl shadow-soft border border-gray-200 p-6"
          >
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Assignment Submission</p>
                <p className="text-2xl font-bold text-gray-900">{overview?.assignment_submission_rate}%</p>
                <p className="text-xs text-gray-500 mt-1">On-time submissions</p>
              </div>
              <AcademicCapIcon className="h-8 w-8 text-purple-600" />
            </div>
          </motion.div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Course Performance */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.4 }}
            className="bg-white rounded-xl shadow-soft border border-gray-200 p-6"
          >
            <h2 className="text-xl font-bold text-gray-900 mb-6">Course Performance</h2>
            <div className="space-y-4">
              {courseAnalytics.map((course) => (
                <div key={course.course_id} className="border border-gray-200 rounded-lg p-4">
                  <div className="flex items-start justify-between mb-3">
                    <div>
                      <h3 className="font-semibold text-gray-900">{course.course_name}</h3>
                      <p className="text-sm text-gray-600">{course.students_enrolled} students enrolled</p>
                    </div>
                    <div className="flex items-center space-x-1">
                      {getTrendIcon(course.trend)}
                      <span className="text-sm font-medium text-gray-700">
                        {course.engagement_score}%
                      </span>
                    </div>
                  </div>
                  
                  <div className="grid grid-cols-2 gap-4 text-sm">
                    <div>
                      <p className="text-gray-600">Completion Rate</p>
                      <p className="font-medium">{course.completion_rate}%</p>
                    </div>
                    <div>
                      <p className="text-gray-600">Avg Score</p>
                      <p className="font-medium">{course.avg_score}%</p>
                    </div>
                    <div>
                      <p className="text-gray-600">Quiz Attempts</p>
                      <p className="font-medium">{course.quiz_attempts}</p>
                    </div>
                    <div>
                      <p className="text-gray-600">Submissions</p>
                      <p className="font-medium">{course.assignment_submissions}</p>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </motion.div>

          {/* Student Performance Tracker */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.5 }}
            className="bg-white rounded-xl shadow-soft border border-gray-200 p-6"
          >
            <h2 className="text-xl font-bold text-gray-900 mb-6">Student Performance Tracker</h2>
            <div className="space-y-4">
              {studentPerformance.map((student) => (
                <div key={student.student_id} className="border border-gray-200 rounded-lg p-4">
                  <div className="flex items-center justify-between mb-3">
                    <div className="flex items-center space-x-3">
                      <div className="h-10 w-10 rounded-full bg-gray-300 flex items-center justify-center">
                        <span className="text-sm font-medium text-gray-700">
                          {student.student_name.charAt(0)}
                        </span>
                      </div>
                      <div>
                        <h3 className="font-semibold text-gray-900">{student.student_name}</h3>
                        <p className="text-sm text-gray-600">{student.courses.length} course(s)</p>
                      </div>
                    </div>
                  </div>
                  
                  <div className="space-y-2">
                    {student.courses.map((course) => (
                      <div key={course.course_id} className="flex items-center justify-between py-2 px-3 bg-gray-50 rounded-lg">
                        <div>
                          <p className="text-sm font-medium text-gray-900">{course.course_name}</p>
                          <p className="text-xs text-gray-600">Progress: {course.progress}%</p>
                        </div>
                        <div className="flex items-center space-x-2">
                          <span className="text-sm font-medium text-gray-700">{course.performance_score}%</span>
                          <span className={`px-2 py-1 rounded-full text-xs font-medium ${getPerformanceColor(course.status)}`}>
                            {course.status.replace('_', ' ')}
                          </span>
                        </div>
                      </div>
                    ))}
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
