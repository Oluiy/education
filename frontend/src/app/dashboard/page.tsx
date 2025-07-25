'use client'

import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { useDashboardStats, useRecentActivity } from '@/lib/hooks'
import { useAuth } from '@/contexts/AuthContext'
import { useToast } from '@/contexts/ToastContext'
import { LoadingSpinner, CardSkeleton } from '@/components/ui/Loading'
import { ErrorAlert, EmptyState } from '@/components/ui/Error'
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
  PlusIcon
} from '@heroicons/react/24/outline'

// Type definitions
interface Stat {
  title: string
  value: string
  change: string
  icon: any
  color: string
}

interface Course {
  id: number
  title: string
  instructor: string
  progress: number
  nextClass: string
  thumbnail: string
}

interface Assignment {
  id: number
  title: string
  course: string
  dueDate: string
  status: string
}

interface Notification {
  id: number
  type: string
  title: string
  message: string
  time: string
  read: boolean
}

// Mock data - replace with actual API calls
const mockData = {
  stats: [
    {
      title: 'Courses Enrolled',
      value: '12',
      change: '+2 this month',
      icon: BookOpenIcon,
      color: 'primary'
    },
    {
      title: 'Assignments Due',
      value: '5',
      change: '3 due this week',
      icon: ClockIcon,
      color: 'secondary'
    },
    {
      title: 'Average Grade',
      value: '85%',
      change: '+5% improvement',
      icon: TrophyIcon,
      color: 'green'
    },
    {
      title: 'Study Hours',
      value: '24h',
      change: 'This week',
      icon: ChartBarIcon,
      color: 'blue'
    }
  ],
  recentCourses: [
    {
      id: 1,
      title: 'Advanced Mathematics',
      instructor: 'Mr. Johnson',
      progress: 78,
      nextClass: '2024-01-15T10:00:00',
      thumbnail: '/api/placeholder/200/120'
    },
    {
      id: 2,
      title: 'Physics Fundamentals',
      instructor: 'Dr. Smith',
      progress: 65,
      nextClass: '2024-01-15T14:00:00',
      thumbnail: '/api/placeholder/200/120'
    },
    {
      id: 3,
      title: 'English Literature',
      instructor: 'Ms. Brown',
      progress: 92,
      nextClass: '2024-01-16T09:00:00',
      thumbnail: '/api/placeholder/200/120'
    }
  ],
  upcomingAssignments: [
    {
      id: 1,
      title: 'Calculus Problem Set #5',
      course: 'Advanced Mathematics',
      dueDate: '2024-01-18T23:59:00',
      status: 'pending'
    },
    {
      id: 2,
      title: 'Essay: Shakespearean Themes',
      course: 'English Literature',
      dueDate: '2024-01-20T23:59:00',
      status: 'in-progress'
    },
    {
      id: 3,
      title: 'Lab Report: Motion Analysis',
      course: 'Physics Fundamentals',
      dueDate: '2024-01-22T23:59:00',
      status: 'not-started'
    }
  ],
  notifications: [
    {
      id: 1,
      type: 'assignment',
      title: 'New assignment posted',
      message: 'Calculus Problem Set #5 has been posted',
      time: '2 hours ago',
      read: false
    },
    {
      id: 2,
      type: 'grade',
      title: 'Grade received',
      message: 'Your Physics quiz has been graded: 88%',
      time: '1 day ago',
      read: false
    },
    {
      id: 3,
      type: 'announcement',
      title: 'Class rescheduled',
      message: 'Tomorrow\'s Literature class moved to 2 PM',
      time: '2 days ago',
      read: true
    }
  ]
}

export default function DashboardPage() {
  const { data: stats, isLoading: statsLoading, error: statsError } = useDashboardStats()
  const { data: activity, isLoading: activityLoading } = useRecentActivity(10)
  // Use API data if available, otherwise fallback to mock data
  const displayData = {
    stats: stats?.stats || mockData.stats,
    recentCourses: stats?.recentCourses || mockData.recentCourses,
    upcomingAssignments: stats?.upcomingAssignments || mockData.upcomingAssignments,
    notifications: activity?.notifications || mockData.notifications
  }

  const formatDate = (dateString: string) => {
    const date = new Date(dateString)
    return date.toLocaleDateString('en-US', {
      weekday: 'short',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    })
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'pending':
        return 'bg-yellow-100 text-yellow-800'
      case 'in-progress':
        return 'bg-blue-100 text-blue-800'
      case 'not-started':
        return 'bg-gray-100 text-gray-800'
      case 'completed':
        return 'bg-green-100 text-green-800'
      default:
        return 'bg-gray-100 text-gray-800'
    }
  }

  // Show loading state
  if (statsLoading && activityLoading) {
    return (
      <div className="w-full min-h-full">
        <div className="animate-pulse space-y-6">
          <div className="h-32 bg-gray-200 rounded-2xl"></div>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {[1, 2, 3, 4].map((i) => (
              <div key={i} className="h-24 bg-gray-200 rounded-xl"></div>
            ))}
          </div>
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <div className="lg:col-span-2 h-96 bg-gray-200 rounded-xl"></div>
            <div className="h-96 bg-gray-200 rounded-xl"></div>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* API Error Banner */}
      {statsError && (
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="bg-yellow-50 border border-yellow-200 rounded-lg p-4 flex items-center space-x-3"
        >
          <ExclamationCircleIcon className="w-5 h-5 text-yellow-600" />
          <div>
            <p className="text-sm font-medium text-yellow-800">
              API Connection Issue
            </p>
            <p className="text-xs text-yellow-600">
              Showing demo data. Check your backend services.
            </p>
          </div>
        </motion.div>
      )}

      {/* Welcome header */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="bg-gradient-to-r from-primary-600 to-secondary-600 rounded-2xl p-6 text-white"
        >
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-heading font-bold mb-2">
                Welcome back, John! 👋
              </h1>
              <p className="text-primary-100">
                You have {displayData.upcomingAssignments.filter((a: Assignment) => a.status === 'pending').length} assignments due this week. Keep up the great work!
              </p>
            </div>
            <div className="hidden md:block">
              <div className="w-24 h-24 bg-white bg-opacity-20 rounded-full flex items-center justify-center">
                <BookOpenIcon className="w-12 h-12 text-white" />
              </div>
            </div>
          </div>
        </motion.div>

        {/* Stats grid */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6"
        >
          {displayData.stats.map((stat: Stat, index: number) => (
            <div key={index} className="card hover:shadow-medium transition-shadow">
              <div className="card-body">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-gray-600 mb-1">{stat.title}</p>
                    <p className="text-2xl font-bold text-gray-900">{stat.value}</p>
                    <p className="text-xs text-gray-500 mt-1">{stat.change}</p>
                  </div>
                  <div className={`p-3 rounded-lg ${
                    stat.color === 'primary' ? 'bg-primary-100' :
                    stat.color === 'secondary' ? 'bg-secondary-100' :
                    stat.color === 'green' ? 'bg-green-100' :
                    stat.color === 'blue' ? 'bg-blue-100' : 'bg-gray-100'
                  }`}>
                    <stat.icon className={`w-6 h-6 ${
                      stat.color === 'primary' ? 'text-primary-600' :
                      stat.color === 'secondary' ? 'text-secondary-600' :
                      stat.color === 'green' ? 'text-green-600' :
                      stat.color === 'blue' ? 'text-blue-600' : 'text-gray-600'
                    }`} />
                  </div>
                </div>
              </div>
            </div>
          ))}
        </motion.div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Recent Courses */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
            className="lg:col-span-2"
          >
            <div className="card">
              <div className="card-header">
                <h3 className="card-title">Continue Learning</h3>
                <button className="text-sm text-primary-600 hover:text-primary-500">
                  View all
                </button>
              </div>
              <div className="card-body">
                <div className="space-y-4">
                  {displayData.recentCourses.map((course: Course) => (
                    <div key={course.id} className="flex items-center space-x-4 p-4 rounded-lg border border-gray-200 hover:border-gray-300 transition-colors">
                      <div className="w-16 h-16 bg-gray-100 rounded-lg flex items-center justify-center">
                        <BookOpenIcon className="w-8 h-8 text-gray-400" />
                      </div>
                      <div className="flex-1 min-w-0">
                        <h4 className="font-medium text-gray-900 truncate">
                          {course.title}
                        </h4>
                        <p className="text-sm text-gray-600">{course.instructor}</p>
                        <div className="mt-2 flex items-center space-x-4">
                          <div className="flex-1">
                            <div className="w-full bg-gray-200 rounded-full h-2">
                              <div 
                                className="bg-primary-600 h-2 rounded-full"
                                style={{ width: `${course.progress}%` }}
                              />
                            </div>
                            <p className="text-xs text-gray-500 mt-1">
                              {course.progress}% complete
                            </p>
                          </div>
                          <div className="text-xs text-gray-500">
                            Next: {formatDate(course.nextClass)}
                          </div>
                        </div>
                      </div>
                      <button className="btn-primary btn-sm">
                        <PlayIcon className="w-4 h-4 mr-1" />
                        Continue
                      </button>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </motion.div>

          {/* Notifications & Assignments */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3 }}
            className="space-y-6"
          >
            {/* Upcoming Assignments */}
            <div className="card">
              <div className="card-header">
                <h3 className="card-title">Upcoming Assignments</h3>
              </div>
              <div className="card-body">
                <div className="space-y-3">
                  {displayData.upcomingAssignments.slice(0, 5).map((assignment: Assignment) => (
                    <div key={assignment.id} className="p-3 rounded-lg border border-gray-200">
                      <div className="flex items-start justify-between mb-2">
                        <h4 className="font-medium text-gray-900 text-sm">
                          {assignment.title}
                        </h4>
                        <span className={`px-2 py-1 text-xs rounded-full ${getStatusColor(assignment.status)}`}>
                          {assignment.status.replace('-', ' ')}
                        </span>
                      </div>
                      <p className="text-xs text-gray-600 mb-1">{assignment.course}</p>
                      <p className="text-xs text-gray-500">
                        Due: {formatDate(assignment.dueDate)}
                      </p>
                    </div>
                  ))}
                </div>
                <button className="btn-secondary btn-sm w-full mt-4">
                  View all assignments
                </button>
              </div>
            </div>
          </motion.div>
        </div>

        {/* Quick Actions */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4 }}
        >
          <div className="card">
            <div className="card-header">
              <h3 className="card-title">Quick Actions</h3>
            </div>
            <div className="card-body">
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                {[
                  { title: 'Join Live Class', icon: UserGroupIcon, color: 'primary' },
                  { title: 'Take Quiz', icon: BookOpenIcon, color: 'secondary' },
                  { title: 'View Calendar', icon: CalendarIcon, color: 'green' },
                  { title: 'Ask AI Tutor', icon: ChartBarIcon, color: 'blue' }
                ].map((action, index) => (
                  <button
                    key={index}
                    className="p-4 rounded-lg border border-gray-200 hover:border-gray-300 transition-colors text-center group"
                  >
                    <action.icon className={`w-8 h-8 mx-auto mb-2 ${
                      action.color === 'primary' ? 'text-primary-600' :
                      action.color === 'secondary' ? 'text-secondary-600' :
                      action.color === 'green' ? 'text-green-600' :
                      action.color === 'blue' ? 'text-blue-600' : 'text-gray-600'
                    } group-hover:scale-110 transition-transform`} />
                    <span className="text-sm font-medium text-gray-900">
                      {action.title}
                    </span>
                  </button>
                ))}
              </div>
            </div>
          </div>
        </motion.div>
    </div>
  )
}