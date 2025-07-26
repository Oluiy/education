// src/components/profile/ProfileStats.tsx
'use client'

import { motion } from 'framer-motion'
import { User } from '../../api/auth'
import { useApi } from '../../hooks/useApi'
import {
  AcademicCapIcon,
  BookOpenIcon,
  TrophyIcon,
  ClockIcon,
  CheckCircleIcon,
  StarIcon,
  UserGroupIcon,
  ChartBarIcon
} from '@heroicons/react/24/outline'

interface ProfileStatsProps {
  user: User
}

export function ProfileStats({ user }: ProfileStatsProps) {
  const { useUserStats } = useApi()
  const { data: stats, isLoading } = useUserStats(user.id)

  if (isLoading) {
    return (
      <div className="bg-white rounded-xl shadow-lg p-6">
        <div className="animate-pulse">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {[...Array(4)].map((_, i) => (
              <div key={i} className="text-center">
                <div className="w-12 h-12 bg-gray-200 rounded-lg mx-auto mb-3" />
                <div className="h-4 bg-gray-200 rounded mb-2" />
                <div className="h-3 bg-gray-200 rounded" />
              </div>
            ))}
          </div>
        </div>
      </div>
    )
  }

  if (!stats) return null

  const getStatsForRole = () => {
    switch (user.role) {
      case 'student':
        return [
          {
            icon: BookOpenIcon,
            value: stats.coursesEnrolled || 0,
            label: 'Courses Enrolled',
            color: 'text-blue-600',
            bgColor: 'bg-blue-100'
          },
          {
            icon: AcademicCapIcon,
            value: stats.quizzesCompleted || 0,
            label: 'Quizzes Completed',
            color: 'text-green-600',
            bgColor: 'bg-green-100'
          },
          {
            icon: TrophyIcon,
            value: `${stats.averageScore || 0}%`,
            label: 'Average Score',
            color: 'text-yellow-600',
            bgColor: 'bg-yellow-100'
          },
          {
            icon: ClockIcon,
            value: stats.totalStudyTime || '0h',
            label: 'Study Time',
            color: 'text-purple-600',
            bgColor: 'bg-purple-100'
          }
        ]

      case 'teacher':
        return [
          {
            icon: BookOpenIcon,
            value: stats.coursesCreated || 0,
            label: 'Courses Created',
            color: 'text-blue-600',
            bgColor: 'bg-blue-100'
          },
          {
            icon: AcademicCapIcon,
            value: stats.quizzesCreated || 0,
            label: 'Quizzes Created',
            color: 'text-green-600',
            bgColor: 'bg-green-100'
          },
          {
            icon: UserGroupIcon,
            value: stats.totalStudents || 0,
            label: 'Total Students',
            color: 'text-indigo-600',
            bgColor: 'bg-indigo-100'
          },
          {
            icon: StarIcon,
            value: `${stats.averageRating || 0}/5`,
            label: 'Average Rating',
            color: 'text-yellow-600',
            bgColor: 'bg-yellow-100'
          }
        ]

      case 'admin':
        return [
          {
            icon: UserGroupIcon,
            value: stats.totalUsers || 0,
            label: 'Total Users',
            color: 'text-blue-600',
            bgColor: 'bg-blue-100'
          },
          {
            icon: BookOpenIcon,
            value: stats.totalCourses || 0,
            label: 'Total Courses',
            color: 'text-green-600',
            bgColor: 'bg-green-100'
          },
          {
            icon: AcademicCapIcon,
            value: stats.totalQuizzes || 0,
            label: 'Total Quizzes',
            color: 'text-purple-600',
            bgColor: 'bg-purple-100'
          },
          {
            icon: ChartBarIcon,
            value: `${stats.systemHealth || 100}%`,
            label: 'System Health',
            color: 'text-red-600',
            bgColor: 'bg-red-100'
          }
        ]

      default:
        return []
    }
  }

  const statsData = getStatsForRole()

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 0.1 }}
      className="bg-white rounded-xl shadow-lg p-6"
    >
      <h2 className="text-xl font-semibold text-gray-900 mb-6">Statistics</h2>
      
      <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
        {statsData.map((stat, index) => (
          <motion.div
            key={index}
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: 0.1 + index * 0.05 }}
            className="text-center"
          >
            <div className={`inline-flex items-center justify-center w-12 h-12 rounded-lg mb-3 ${stat.bgColor}`}>
              <stat.icon className={`w-6 h-6 ${stat.color}`} />
            </div>
            
            <div className="text-2xl font-bold text-gray-900 mb-1">
              {stat.value}
            </div>
            
            <div className="text-sm text-gray-600">
              {stat.label}
            </div>
          </motion.div>
        ))}
      </div>

      {/* Additional Stats for Students */}
      {user.role === 'student' && stats.recentAchievements && stats.recentAchievements.length > 0 && (
        <div className="mt-8 pt-6 border-t border-gray-200">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Recent Achievements</h3>
          <div className="space-y-3">
            {stats.recentAchievements.slice(0, 3).map((achievement: any, index: number) => (
              <div key={index} className="flex items-center space-x-3 p-3 bg-yellow-50 rounded-lg">
                <TrophyIcon className="w-5 h-5 text-yellow-600" />
                <div>
                  <p className="text-sm font-medium text-gray-900">{achievement.title}</p>
                  <p className="text-xs text-gray-600">{achievement.description}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Progress Overview for Students */}
      {user.role === 'student' && stats.currentCourses && (
        <div className="mt-8 pt-6 border-t border-gray-200">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Current Progress</h3>
          <div className="space-y-4">
            {stats.currentCourses.slice(0, 3).map((course: any, index: number) => (
              <div key={index} className="space-y-2">
                <div className="flex justify-between items-center">
                  <span className="text-sm font-medium text-gray-900">{course.title}</span>
                  <span className="text-sm text-gray-600">{course.progress}%</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <motion.div
                    initial={{ width: 0 }}
                    animate={{ width: `${course.progress}%` }}
                    transition={{ duration: 1, delay: 0.2 + index * 0.1 }}
                    className="bg-blue-600 h-2 rounded-full"
                  />
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Teaching Performance for Teachers */}
      {user.role === 'teacher' && stats.performanceMetrics && (
        <div className="mt-8 pt-6 border-t border-gray-200">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Teaching Performance</h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="text-center p-4 bg-blue-50 rounded-lg">
              <div className="text-lg font-bold text-blue-600">
                {stats.performanceMetrics.studentSatisfaction}%
              </div>
              <div className="text-sm text-blue-800">Student Satisfaction</div>
            </div>
            
            <div className="text-center p-4 bg-green-50 rounded-lg">
              <div className="text-lg font-bold text-green-600">
                {stats.performanceMetrics.courseCompletionRate}%
              </div>
              <div className="text-sm text-green-800">Completion Rate</div>
            </div>
            
            <div className="text-center p-4 bg-purple-50 rounded-lg">
              <div className="text-lg font-bold text-purple-600">
                {stats.performanceMetrics.averageQuizScore}%
              </div>
              <div className="text-sm text-purple-800">Avg Quiz Score</div>
            </div>
          </div>
        </div>
      )}
    </motion.div>
  )
}
