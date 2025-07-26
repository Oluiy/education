'use client'

import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import {
  UserGroupIcon,
  MagnifyingGlassIcon,
  ChartBarIcon,
  AcademicCapIcon,
  ClockIcon,
  CheckCircleIcon,
  ExclamationTriangleIcon,
  EyeIcon,
  EnvelopeIcon
} from '@heroicons/react/24/outline'

interface StudentProgress {
  student_id: string
  student_name: string
  student_email: string
  enrollment_date: string
  last_active: string
  overall_progress: number
  overall_grade: number
  courses: {
    course_id: string
    course_name: string
    progress: number
    grade: number
    assignments_completed: number
    assignments_total: number
    quizzes_completed: number
    quizzes_total: number
    last_activity: string
    status: 'excellent' | 'good' | 'needs_attention' | 'at_risk'
  }[]
}

interface Course {
  id: string
  name: string
  code: string
  students_enrolled: number
}

export default function StudentProgressPage() {
  const [students, setStudents] = useState<StudentProgress[]>([])
  const [courses, setCourses] = useState<Course[]>([])
  const [loading, setLoading] = useState(true)
  const [searchTerm, setSearchTerm] = useState('')
  const [selectedCourse, setSelectedCourse] = useState('all')
  const [statusFilter, setStatusFilter] = useState('all')
  const [selectedStudent, setSelectedStudent] = useState<StudentProgress | null>(null)

  useEffect(() => {
    fetchStudentProgressData()
  }, [selectedCourse])

  const fetchStudentProgressData = async () => {
    try {
      // Mock data - replace with actual API calls
      const mockCourses: Course[] = [
        { id: '1', name: 'Advanced Mathematics', code: 'MATH301', students_enrolled: 45 },
        { id: '2', name: 'Physics Fundamentals', code: 'PHY101', students_enrolled: 38 },
        { id: '3', name: 'Chemistry Basics', code: 'CHEM100', students_enrolled: 42 },
        { id: '4', name: 'Biology Essentials', code: 'BIO150', students_enrolled: 31 }
      ]

      const mockStudents: StudentProgress[] = [
        {
          student_id: '1',
          student_name: 'Emily Johnson',
          student_email: 'emily.johnson@email.com',
          enrollment_date: '2024-01-01T00:00:00Z',
          last_active: '2024-01-15T11:00:00Z',
          overall_progress: 92,
          overall_grade: 89.5,
          courses: [
            {
              course_id: '1',
              course_name: 'Advanced Mathematics',
              progress: 95,
              grade: 91.2,
              assignments_completed: 7,
              assignments_total: 8,
              quizzes_completed: 10,
              quizzes_total: 12,
              last_activity: '2024-01-15T11:00:00Z',
              status: 'excellent'
            },
            {
              course_id: '2',
              course_name: 'Physics Fundamentals',
              progress: 89,
              grade: 87.8,
              assignments_completed: 5,
              assignments_total: 6,
              quizzes_completed: 8,
              quizzes_total: 10,
              last_activity: '2024-01-14T15:30:00Z',
              status: 'excellent'
            }
          ]
        },
        {
          student_id: '2',
          student_name: 'Michael Chen',
          student_email: 'michael.chen@email.com',
          enrollment_date: '2024-01-01T00:00:00Z',
          last_active: '2024-01-10T16:30:00Z',
          overall_progress: 45,
          overall_grade: 52.3,
          courses: [
            {
              course_id: '1',
              course_name: 'Advanced Mathematics',
              progress: 45,
              grade: 52.3,
              assignments_completed: 3,
              assignments_total: 8,
              quizzes_completed: 4,
              quizzes_total: 12,
              last_activity: '2024-01-10T16:30:00Z',
              status: 'at_risk'
            }
          ]
        },
        {
          student_id: '3',
          student_name: 'Sarah Williams',
          student_email: 'sarah.williams@email.com',
          enrollment_date: '2024-01-01T00:00:00Z',
          last_active: '2024-01-14T09:15:00Z',
          overall_progress: 78,
          overall_grade: 81.7,
          courses: [
            {
              course_id: '3',
              course_name: 'Chemistry Basics',
              progress: 82,
              grade: 84.5,
              assignments_completed: 6,
              assignments_total: 7,
              quizzes_completed: 7,
              quizzes_total: 9,
              last_activity: '2024-01-14T09:15:00Z',
              status: 'good'
            },
            {
              course_id: '4',
              course_name: 'Biology Essentials',
              progress: 74,
              grade: 78.9,
              assignments_completed: 4,
              assignments_total: 5,
              quizzes_completed: 6,
              quizzes_total: 8,
              last_activity: '2024-01-13T14:20:00Z',
              status: 'good'
            },
            {
              course_id: '1',
              course_name: 'Advanced Mathematics',
              progress: 45,
              grade: 52.3,
              assignments_completed: 3,
              assignments_total: 8,
              quizzes_completed: 4,
              quizzes_total: 12,
              last_activity: '2024-01-10T16:30:00Z',
              status: 'excellent'
            }
          ]
        },
        {
          student_id: '4',
          student_name: 'David Brown',
          student_email: 'david.brown@email.com',
          enrollment_date: '2024-01-01T00:00:00Z',
          last_active: '2024-01-08T13:45:00Z',
          overall_progress: 23,
          overall_grade: 28.1,
          courses: [
            {
              course_id: '2',
              course_name: 'Physics Fundamentals',
              progress: 23,
              grade: 28.1,
              assignments_completed: 1,
              assignments_total: 6,
              quizzes_completed: 2,
              quizzes_total: 10,
              last_activity: '2024-01-08T13:45:00Z',
              status: 'at_risk'
            }
          ]
        },
        {
          student_id: '5',
          student_name: 'Jessica Martinez',
          student_email: 'jessica.martinez@email.com',
          enrollment_date: '2024-01-01T00:00:00Z',
          last_active: '2024-01-14T12:30:00Z',
          overall_progress: 67,
          overall_grade: 72.4,
          courses: [
            {
              course_id: '1',
              course_name: 'Advanced Mathematics',
              progress: 71,
              grade: 76.2,
              assignments_completed: 5,
              assignments_total: 8,
              quizzes_completed: 8,
              quizzes_total: 12,
              last_activity: '2024-01-14T12:30:00Z',
              status: 'needs_attention'
            },
            {
              course_id: '3',
              course_name: 'Chemistry Basics',
              progress: 63,
              grade: 68.6,
              assignments_completed: 4,
              assignments_total: 7,
              quizzes_completed: 5,
              quizzes_total: 9,
              last_activity: '2024-01-13T10:15:00Z',
              status: 'needs_attention'
            }
          ]
        }
      ]

      setCourses(mockCourses)
      setStudents(mockStudents)
      setLoading(false)
    } catch (error) {
      console.error('Error fetching student progress:', error)
      setLoading(false)
    }
  }

  const getStatusColor = (status: string) => {
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

  const getOverallStatus = (grade: number) => {
    if (grade >= 90) return 'excellent'
    if (grade >= 80) return 'good'
    if (grade >= 70) return 'needs_attention'
    return 'at_risk'
  }

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    })
  }

  const getDaysInactive = (lastActive: string) => {
    const last = new Date(lastActive)
    const now = new Date()
    const diffTime = now.getTime() - last.getTime()
    const diffDays = Math.floor(diffTime / (1000 * 60 * 60 * 24))
    return diffDays
  }

  const filteredStudents = students.filter(student => {
    const matchesSearch = student.student_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         student.student_email.toLowerCase().includes(searchTerm.toLowerCase())
    
    const matchesCourse = selectedCourse === 'all' || 
                         student.courses.some(course => course.course_id === selectedCourse)
    
    const overallStatus = getOverallStatus(student.overall_grade)
    const matchesStatus = statusFilter === 'all' || overallStatus === statusFilter
    
    return matchesSearch && matchesCourse && matchesStatus
  })

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
          <h1 className="text-2xl sm:text-3xl font-bold text-gray-900">Student Progress Tracking</h1>
          <p className="text-gray-600 mt-1">Monitor individual student performance and engagement</p>
        </div>

        {/* Filters */}
        <div className="flex flex-col sm:flex-row gap-4 mb-6">
          <div className="relative flex-1">
            <MagnifyingGlassIcon className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
            <input
              type="text"
              placeholder="Search students..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="pl-10 pr-4 py-2 w-full border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
            />
          </div>
          <select
            value={selectedCourse}
            onChange={(e) => setSelectedCourse(e.target.value)}
            className="px-8 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
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
            className="px-8 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
          >
            <option value="all">All Performance</option>
            <option value="excellent">Excellent</option>
            <option value="good">Good</option>
            <option value="needs_attention">Needs Attention</option>
            <option value="at_risk">At Risk</option>
          </select>
        </div>

        {/* Students List */}
        <div className="space-y-4">
          {filteredStudents.map((student, index) => (
            <motion.div
              key={student.student_id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.1 }}
              className="bg-white rounded-xl shadow-soft border border-gray-200 p-4 sm:p-6 hover:shadow-strong transition-shadow duration-200"
            >
              <div className="flex flex-col lg:flex-row lg:items-start lg:justify-between gap-4">
                <div className="flex-1">
                  <div className="flex flex-col sm:flex-row sm:items-center gap-2 sm:gap-3 mb-3">
                    <div className="flex items-center space-x-3">
                      <div className="h-12 w-12 rounded-full bg-primary-100 flex items-center justify-center">
                        <span className="text-lg font-semibold text-primary-700">
                          {student.student_name.charAt(0)}
                        </span>
                      </div>
                      <div>
                        <h3 className="text-lg font-semibold text-gray-900">{student.student_name}</h3>
                        <p className="text-sm text-gray-600">{student.student_email}</p>
                      </div>
                    </div>
                    <span className={`px-3 py-1 rounded-full text-xs font-medium w-fit ${getStatusColor(getOverallStatus(student.overall_grade))}`}>
                      {getOverallStatus(student.overall_grade).replace('_', ' ')}
                    </span>
                  </div>

                  <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 text-sm mb-4">
                    <div className="flex items-center gap-1">
                      <ChartBarIcon className="w-4 h-4 text-blue-500 flex-shrink-0" />
                      <div>
                        <p className="font-medium text-gray-900">{student.overall_progress}%</p>
                        <p className="text-gray-600">Progress</p>
                      </div>
                    </div>
                    <div className="flex items-center gap-1">
                      <AcademicCapIcon className="w-4 h-4 text-green-500 flex-shrink-0" />
                      <div>
                        <p className="font-medium text-gray-900">{student.overall_grade.toFixed(1)}%</p>
                        <p className="text-gray-600">Grade</p>
                      </div>
                    </div>
                    <div className="flex items-center gap-1">
                      <ClockIcon className="w-4 h-4 text-purple-500 flex-shrink-0" />
                      <div>
                        <p className="font-medium text-gray-900">{getDaysInactive(student.last_active)}d</p>
                        <p className="text-gray-600">Days ago</p>
                      </div>
                    </div>
                    <div className="flex items-center gap-1">
                      <UserGroupIcon className="w-4 h-4 text-orange-500 flex-shrink-0" />
                      <div>
                        <p className="font-medium text-gray-900">{student.courses.length}</p>
                        <p className="text-gray-600">Courses</p>
                      </div>
                    </div>
                  </div>

                  {/* Course Details */}
                  <div className="space-y-2">
                    {student.courses.map((course) => (
                      <div key={course.course_id} className="bg-gray-50 rounded-lg p-3">
                        <div className="flex items-center justify-between mb-2">
                          <h4 className="font-medium text-gray-900">{course.course_name}</h4>
                          <span className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(course.status)}`}>
                            {course.status.replace('_', ' ')}
                          </span>
                        </div>
                        <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 text-xs text-gray-600">
                          <div>
                            <p className="font-medium">{course.progress}%</p>
                            <p>Progress</p>
                          </div>
                          <div>
                            <p className="font-medium">{course.grade.toFixed(1)}%</p>
                            <p>Grade</p>
                          </div>
                          <div>
                            <p className="font-medium">{course.assignments_completed}/{course.assignments_total}</p>
                            <p>Assignments</p>
                          </div>
                          <div>
                            <p className="font-medium">{course.quizzes_completed}/{course.quizzes_total}</p>
                            <p>Quizzes</p>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>

                  {/* Alerts */}
                  {getDaysInactive(student.last_active) > 7 && (
                    <div className="bg-red-50 border border-red-200 rounded-lg p-3 mt-3">
                      <div className="flex items-center gap-2">
                        <ExclamationTriangleIcon className="w-4 h-4 text-red-600" />
                        <p className="text-sm text-red-800">
                          Student has been inactive for {getDaysInactive(student.last_active)} days
                        </p>
                      </div>
                    </div>
                  )}

                  {student.overall_grade < 70 && (
                    <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-3 mt-3">
                      <div className="flex items-center gap-2">
                        <ExclamationTriangleIcon className="w-4 h-4 text-yellow-600" />
                        <p className="text-sm text-yellow-800">
                          Student performance is below 70% - may need additional support
                        </p>
                      </div>
                    </div>
                  )}
                </div>

                <div className="flex flex-wrap sm:flex-nowrap items-center gap-2">
                  <button 
                    onClick={() => setSelectedStudent(student)}
                    className="flex items-center justify-center gap-1 px-3 py-1.5 text-sm bg-primary-100 text-primary-700 rounded-lg hover:bg-primary-200 transition-colors flex-1 sm:flex-none w-full sm:w-auto"
                  >
                    <EyeIcon className="w-4 h-4" />
                    <span className="hidden sm:inline">Details</span>
                  </button>
                  <a 
                    href={`mailto:${student.student_email}`}
                    className="flex items-center justify-center gap-1 px-3 py-1.5 text-sm bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors flex-1 sm:flex-none w-full sm:w-auto"
                  >
                    <EnvelopeIcon className="w-4 h-4" />
                    <span className="hidden sm:inline">Email</span>
                  </a>
                </div>
              </div>
            </motion.div>
          ))}
        </div>

        {filteredStudents.length === 0 && (
          <div className="text-center py-12 px-4">
            <UserGroupIcon className="w-12 h-12 sm:w-16 sm:h-16 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">No students found</h3>
            <p className="text-gray-600 mb-4 text-sm sm:text-base">
              {searchTerm || selectedCourse !== 'all' || statusFilter !== 'all'
                ? 'Try adjusting your search or filter criteria'
                : 'No students are currently enrolled in your courses'}
            </p>
          </div>
        )}
      </div>
    </div>
  )
}
