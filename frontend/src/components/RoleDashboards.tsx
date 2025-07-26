'use client'

import { useState } from 'react'
import { motion } from 'framer-motion'
import { useAuth } from '@/contexts/AuthContext'
import { useToast } from '@/contexts/ToastContext'
import { 
  useCourses, 
  useUserEnrollments, 
  useUserStats, 
  useUserActivity,
  useNotifications,
  useQuizzes,
  useUsers
} from '@/hooks/useApi'
import { LoadingPage, LoadingSpinner } from '@/components/ui/Loading'
import {
  BookOpenIcon,
  ClockIcon,
  ChartBarIcon,
  BellIcon,
  CalendarIcon,
  UserGroupIcon,
  TrophyIcon,
  PlayIcon,
  ExclamationCircleIcon,
  PlusIcon,
  AcademicCapIcon,
  CheckIcon,
  CogIcon,
  PencilIcon,
  UsersIcon,
  DocumentTextIcon
} from '@heroicons/react/24/outline'

// Higher-order component for role-based access control
export function withRoleAccess(Component: React.ComponentType, allowedRoles: string[]) {
  return function ProtectedComponent(props: any) {
    const { user, isLoading } = useAuth()

    if (isLoading) {
      return <LoadingPage />
    }

    if (!user || !allowedRoles.includes(user.role)) {
      return (
        <div className="flex items-center justify-center min-h-screen">
          <div className="text-center">
            <ExclamationCircleIcon className="w-16 h-16 text-red-500 mx-auto mb-4" />
            <h2 className="text-xl font-semibold text-gray-900 mb-2">Access Denied</h2>
            <p className="text-gray-600">You don't have permission to view this page.</p>
          </div>
        </div>
      )
    }

    return <Component {...props} />
  }
}

// Student Dashboard Component
export function StudentDashboard() {
  const { user } = useAuth()
  const { success: showSuccess, error: showError } = useToast()
  
  const { data: enrollments, isLoading: enrollmentsLoading } = useUserEnrollments()
  const { data: stats, isLoading: statsLoading } = useUserStats()
  const { data: activity, isLoading: activityLoading } = useUserActivity()
  const { data: notifications } = useNotifications(user?.id)

  if (enrollmentsLoading || statsLoading) {
    return <LoadingPage />
  }

  const statCards = [
    {
      title: 'Enrolled Courses',
      value: stats?.totalCourses || 0,
      change: '+2 this month',
      icon: BookOpenIcon,
      color: 'bg-primary-600'
    },
    {
      title: 'Hours This Week',
      value: Math.round((stats?.studyTime || 0) / 60),
      change: '+3.2 from last week',
      icon: ClockIcon,
      color: 'bg-secondary-600'
    },
    {
      title: 'Average Score',
      value: `${Math.round(stats?.averageScore || 0)}%`,
      change: '+5% improvement',
      icon: ChartBarIcon,
      color: 'bg-green-600'
    },
    {
      title: 'Streak Days',
      value: stats?.streak || 0,
      change: 'Keep it up!',
      icon: TrophyIcon,
      color: 'bg-yellow-600'
    }
  ]

  return (
    <div className="space-y-6">
      {/* Welcome Header */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="bg-gradient-to-r from-primary-600 to-secondary-600 rounded-2xl p-6 text-white"
      >
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold mb-2">Welcome back, {user?.name}!</h1>
            <p className="text-primary-100 text-sm">
              Ready to continue your learning journey? You have assignments due this week.
            </p>
          </div>
          <div className="hidden md:block">
            <div className="flex items-center space-x-4">
              <div className="text-right">
                <p className="text-sm text-primary-100">Current Streak</p>
                <p className="text-2xl font-bold">{stats?.streak || 0} Days</p>
              </div>
              <TrophyIcon className="w-12 h-12 text-yellow-400" />
            </div>
          </div>
        </div>
      </motion.div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {statCards.map((stat, index) => (
          <motion.div
            key={stat.title}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: index * 0.1 }}
            className="bg-white rounded-xl shadow-sm p-6"
          >
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">{stat.title}</p>
                <p className="text-2xl font-bold text-gray-900">{stat.value}</p>
                <p className="text-xs text-green-600">{stat.change}</p>
              </div>
              <div className={`p-3 rounded-full ${stat.color}`}>
                <stat.icon className="w-6 h-6 text-white" />
              </div>
            </div>
          </motion.div>
        ))}
      </div>

      {/* Main Content */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Continue Learning */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="lg:col-span-2 bg-white rounded-xl shadow-sm"
        >
          <div className="p-6 border-b border-gray-200">
            <div className="flex items-center justify-between">
              <h3 className="text-lg font-semibold text-gray-900">Continue Learning</h3>
              <button className="text-primary-600 hover:text-primary-700 text-sm font-medium">
                View All
              </button>
            </div>
          </div>
          <div className="p-6">
            <div className="space-y-4">
              {enrollments?.slice(0, 3).map((enrollment) => (
                <div key={enrollment.id} className="flex items-center space-x-4 p-4 rounded-lg border border-gray-200 hover:border-gray-300 transition-colors">
                  <div className="flex-shrink-0">
                    <div className="w-16 h-16 bg-gradient-to-br from-primary-100 to-secondary-100 rounded-lg flex items-center justify-center">
                      <BookOpenIcon className="w-8 h-8 text-primary-600" />
                    </div>
                  </div>
                  <div className="flex-grow">
                    <h4 className="font-semibold text-gray-900">Course {enrollment.courseId}</h4>
                    <p className="text-sm text-gray-600">Progress: {Math.round(enrollment.progress)}%</p>
                    <div className="mt-2">
                      <div className="w-full bg-gray-200 rounded-full h-2">
                        <div
                          className="bg-primary-600 h-2 rounded-full transition-all duration-300"
                          style={{ width: `${enrollment.progress}%` }}
                        />
                      </div>
                    </div>
                  </div>
                  <div className="flex-shrink-0">
                    <button className="bg-primary-600 text-white px-4 py-2 rounded-lg text-sm font-medium hover:bg-primary-700 transition-colors">
                      <PlayIcon className="w-4 h-4 mr-1 inline" />
                      Continue
                    </button>
                  </div>
                </div>
              )) || (
                <div className="text-center py-8">
                  <BookOpenIcon className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                  <p className="text-gray-600">No enrollments yet. Start learning today!</p>
                </div>
              )}
            </div>
          </div>
        </motion.div>

        {/* Sidebar */}
        <div className="space-y-6">
          {/* Recent Activity */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3 }}
            className="bg-white rounded-xl shadow-sm"
          >
            <div className="p-6 border-b border-gray-200">
              <h3 className="text-lg font-semibold text-gray-900">Recent Activity</h3>
            </div>
            <div className="p-6">
              <div className="space-y-4">
                {activity?.map((item: any) => (
                  <div key={item.id} className="flex items-start space-x-3">
                    <div className="flex-shrink-0 w-8 h-8 bg-primary-100 rounded-full flex items-center justify-center">
                      <CheckIcon className="w-4 h-4 text-primary-600" />
                    </div>
                    <div className="flex-grow">
                      <p className="text-sm font-medium text-gray-900">{item.title}</p>
                      <p className="text-xs text-gray-500">{new Date(item.timestamp).toLocaleDateString()}</p>
                    </div>
                  </div>
                )) || (
                  <p className="text-gray-600 text-sm">No recent activity</p>
                )}
              </div>
            </div>
          </motion.div>

          {/* Notifications */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.4 }}
            className="bg-white rounded-xl shadow-sm"
          >
            <div className="p-6 border-b border-gray-200">
              <div className="flex items-center justify-between">
                <h3 className="text-lg font-semibold text-gray-900">Notifications</h3>
                <BellIcon className="w-5 h-5 text-gray-400" />
              </div>
            </div>
            <div className="p-6">
              <div className="space-y-3">
                {notifications?.notifications?.slice(0, 3).map((notification) => (
                  <div key={notification.id} className={`p-3 rounded-lg border ${notification.isRead ? 'border-gray-200' : 'border-primary-200 bg-primary-50'}`}>
                    <p className="text-sm font-medium text-gray-900">{notification.title}</p>
                    <p className="text-xs text-gray-600">{notification.message}</p>
                  </div>
                )) || (
                  <p className="text-gray-600 text-sm">No notifications</p>
                )}
              </div>
            </div>
          </motion.div>
        </div>
      </div>
    </div>
  )
}

// Teacher Dashboard Component
export function TeacherDashboard() {
  const { user } = useAuth()
  const { data: courses, isLoading: coursesLoading } = useCourses()
  const { data: quizzes, isLoading: quizzesLoading } = useQuizzes()
  const { data: students } = useUsers({ role: 'student', schoolId: user?.schoolId })

  if (coursesLoading || quizzesLoading) {
    return <LoadingPage />
  }

  return (
    <div className="space-y-6">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="bg-gradient-to-r from-purple-600 to-blue-600 rounded-2xl p-6 text-white"
      >
        <h1 className="text-2xl font-bold mb-2">Teacher Dashboard</h1>
        <p className="text-purple-100">Manage your courses, students, and assessments</p>
      </motion.div>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="bg-white rounded-xl shadow-sm p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">My Courses</p>
              <p className="text-2xl font-bold text-gray-900">{courses?.courses?.length || 0}</p>
            </div>
            <BookOpenIcon className="w-8 h-8 text-blue-600" />
          </div>
        </div>
        <div className="bg-white rounded-xl shadow-sm p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Students</p>
              <p className="text-2xl font-bold text-gray-900">{students?.users?.length || 0}</p>
            </div>
            <UsersIcon className="w-8 h-8 text-green-600" />
          </div>
        </div>
        <div className="bg-white rounded-xl shadow-sm p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Quizzes</p>
              <p className="text-2xl font-bold text-gray-900">{quizzes?.quizzes?.length || 0}</p>
            </div>
            <DocumentTextIcon className="w-8 h-8 text-purple-600" />
          </div>
        </div>
        <div className="bg-white rounded-xl shadow-sm p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Pending Reviews</p>
              <p className="text-2xl font-bold text-gray-900">12</p>
            </div>
            <ClockIcon className="w-8 h-8 text-yellow-600" />
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white rounded-xl shadow-sm">
          <div className="p-6 border-b border-gray-200">
            <div className="flex items-center justify-between">
              <h3 className="text-lg font-semibold text-gray-900">My Courses</h3>
              <button className="bg-blue-600 text-white px-4 py-2 rounded-lg text-sm font-medium hover:bg-blue-700 transition-colors">
                <PlusIcon className="w-4 h-4 mr-1 inline" />
                New Course
              </button>
            </div>
          </div>
          <div className="p-6">
            <div className="space-y-4">
              {courses?.courses?.slice(0, 3).map((course) => (
                <div key={course.id} className="flex items-center space-x-4 p-4 border border-gray-200 rounded-lg">
                  <div className="flex-grow">
                    <h4 className="font-semibold text-gray-900">{course.title}</h4>
                    <p className="text-sm text-gray-600">{course.enrollmentCount} students enrolled</p>
                  </div>
                  <button className="text-blue-600 hover:text-blue-700">
                    <PencilIcon className="w-5 h-5" />
                  </button>
                </div>
              )) || (
                <div className="text-center py-8">
                  <BookOpenIcon className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                  <p className="text-gray-600">No courses created yet</p>
                </div>
              )}
            </div>
          </div>
        </div>

        <div className="bg-white rounded-xl shadow-sm">
          <div className="p-6 border-b border-gray-200">
            <div className="flex items-center justify-between">
              <h3 className="text-lg font-semibold text-gray-900">Recent Quizzes</h3>
              <button className="bg-purple-600 text-white px-4 py-2 rounded-lg text-sm font-medium hover:bg-purple-700 transition-colors">
                <PlusIcon className="w-4 h-4 mr-1 inline" />
                New Quiz
              </button>
            </div>
          </div>
          <div className="p-6">
            <div className="space-y-4">
              {quizzes?.quizzes?.slice(0, 3).map((quiz) => (
                <div key={quiz.id} className="flex items-center space-x-4 p-4 border border-gray-200 rounded-lg">
                  <div className="flex-grow">
                    <h4 className="font-semibold text-gray-900">{quiz.title}</h4>
                    <p className="text-sm text-gray-600">{quiz.questions.length} questions</p>
                  </div>
                  <button className="text-purple-600 hover:text-purple-700">
                    <PencilIcon className="w-5 h-5" />
                  </button>
                </div>
              )) || (
                <div className="text-center py-8">
                  <DocumentTextIcon className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                  <p className="text-gray-600">No quizzes created yet</p>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

// Admin Dashboard Component
export function AdminDashboard() {
  const { user } = useAuth()
  const { data: allUsers } = useUsers({ schoolId: user?.schoolId })
  const { data: allCourses } = useCourses()
  const { data: allQuizzes } = useQuizzes()

  const teacherCount = allUsers?.users?.filter(u => u.role === 'teacher').length || 0
  const studentCount = allUsers?.users?.filter(u => u.role === 'student').length || 0

  return (
    <div className="space-y-6">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="bg-gradient-to-r from-indigo-600 to-purple-600 rounded-2xl p-6 text-white"
      >
        <h1 className="text-2xl font-bold mb-2">Admin Dashboard</h1>
        <p className="text-indigo-100">Manage your school's education platform</p>
      </motion.div>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="bg-white rounded-xl shadow-sm p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Total Students</p>
              <p className="text-2xl font-bold text-gray-900">{studentCount}</p>
            </div>
            <AcademicCapIcon className="w-8 h-8 text-blue-600" />
          </div>
        </div>
        <div className="bg-white rounded-xl shadow-sm p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Teachers</p>
              <p className="text-2xl font-bold text-gray-900">{teacherCount}</p>
            </div>
            <UsersIcon className="w-8 h-8 text-green-600" />
          </div>
        </div>
        <div className="bg-white rounded-xl shadow-sm p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Total Courses</p>
              <p className="text-2xl font-bold text-gray-900">{allCourses?.courses?.length || 0}</p>
            </div>
            <BookOpenIcon className="w-8 h-8 text-purple-600" />
          </div>
        </div>
        <div className="bg-white rounded-xl shadow-sm p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Active Quizzes</p>
              <p className="text-2xl font-bold text-gray-900">{allQuizzes?.quizzes?.filter(q => q.isPublished).length || 0}</p>
            </div>
            <DocumentTextIcon className="w-8 h-8 text-yellow-600" />
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white rounded-xl shadow-sm">
          <div className="p-6 border-b border-gray-200">
            <div className="flex items-center justify-between">
              <h3 className="text-lg font-semibold text-gray-900">User Management</h3>
              <button className="bg-indigo-600 text-white px-4 py-2 rounded-lg text-sm font-medium hover:bg-indigo-700 transition-colors">
                <PlusIcon className="w-4 h-4 mr-1 inline" />
                Invite User
              </button>
            </div>
          </div>
          <div className="p-6">
            <div className="space-y-4">
              {allUsers?.users?.slice(0, 5).map((user) => (
                <div key={user.id} className="flex items-center space-x-4 p-4 border border-gray-200 rounded-lg">
                  <div className="flex-grow">
                    <h4 className="font-semibold text-gray-900">{user.name}</h4>
                    <p className="text-sm text-gray-600">{user.role} - {user.email}</p>
                  </div>
                  <button className="text-indigo-600 hover:text-indigo-700">
                    <CogIcon className="w-5 h-5" />
                  </button>
                </div>
              )) || (
                <div className="text-center py-8">
                  <UsersIcon className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                  <p className="text-gray-600">No users found</p>
                </div>
              )}
            </div>
          </div>
        </div>

        <div className="bg-white rounded-xl shadow-sm">
          <div className="p-6 border-b border-gray-200">
            <h3 className="text-lg font-semibold text-gray-900">System Analytics</h3>
          </div>
          <div className="p-6">
            <div className="space-y-4">
              <div className="flex justify-between items-center">
                <span className="text-gray-600">Course Completion Rate</span>
                <span className="font-semibold">78%</span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div className="bg-green-600 h-2 rounded-full" style={{ width: '78%' }} />
              </div>
              
              <div className="flex justify-between items-center">
                <span className="text-gray-600">Quiz Success Rate</span>
                <span className="font-semibold">85%</span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div className="bg-blue-600 h-2 rounded-full" style={{ width: '85%' }} />
              </div>
              
              <div className="flex justify-between items-center">
                <span className="text-gray-600">Active Users (7 days)</span>
                <span className="font-semibold">{Math.round((studentCount + teacherCount) * 0.8)}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

// Protected versions of dashboards
export const ProtectedStudentDashboard = withRoleAccess(StudentDashboard, ['student'])
export const ProtectedTeacherDashboard = withRoleAccess(TeacherDashboard, ['teacher'])
export const ProtectedAdminDashboard = withRoleAccess(AdminDashboard, ['admin'])
