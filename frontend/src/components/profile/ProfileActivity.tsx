// src/components/profile/ProfileActivity.tsx
'use client'

import { useState } from 'react'
import { motion } from 'framer-motion'
import { User } from '../../api/auth'
import { useApi } from '../../hooks/useApi'
import Link from 'next/link'
import {
  ClockIcon,
  BookOpenIcon,
  AcademicCapIcon,
  TrophyIcon,
  ChatBubbleLeftRightIcon,
  DocumentTextIcon,
  CalendarIcon,
  EyeIcon
} from '@heroicons/react/24/outline'

interface ProfileActivityProps {
  user: User
}

export function ProfileActivity({ user }: ProfileActivityProps) {
  const [activeTab, setActiveTab] = useState<'recent' | 'courses' | 'achievements'>('recent')
  
  const { useUserActivity, useUserCourses, useUserAchievements } = useApi()
  
  const { data: activity, isLoading: activityLoading } = useUserActivity(user.id)
  const { data: courses, isLoading: coursesLoading } = useUserCourses(user.id)
  const { data: achievements, isLoading: achievementsLoading } = useUserAchievements(user.id)

  const getActivityIcon = (type: string) => {
    switch (type) {
      case 'quiz_completed':
        return AcademicCapIcon
      case 'course_enrolled':
      case 'course_completed':
        return BookOpenIcon
      case 'achievement_earned':
        return TrophyIcon
      case 'discussion_post':
        return ChatBubbleLeftRightIcon
      case 'assignment_submitted':
        return DocumentTextIcon
      default:
        return ClockIcon
    }
  }

  const getActivityColor = (type: string) => {
    switch (type) {
      case 'quiz_completed':
        return 'text-blue-600 bg-blue-100'
      case 'course_enrolled':
        return 'text-green-600 bg-green-100'
      case 'course_completed':
        return 'text-purple-600 bg-purple-100'
      case 'achievement_earned':
        return 'text-yellow-600 bg-yellow-100'
      case 'discussion_post':
        return 'text-indigo-600 bg-indigo-100'
      case 'assignment_submitted':
        return 'text-pink-600 bg-pink-100'
      default:
        return 'text-gray-600 bg-gray-100'
    }
  }

  const formatDate = (dateString: string) => {
    const date = new Date(dateString)
    const now = new Date()
    const diffInHours = Math.floor((now.getTime() - date.getTime()) / (1000 * 60 * 60))
    
    if (diffInHours < 24) {
      if (diffInHours < 1) {
        const diffInMinutes = Math.floor((now.getTime() - date.getTime()) / (1000 * 60))
        return diffInMinutes <= 1 ? 'Just now' : `${diffInMinutes}m ago`
      }
      return `${diffInHours}h ago`
    } else {
      const diffInDays = Math.floor(diffInHours / 24)
      if (diffInDays < 7) {
        return `${diffInDays}d ago`
      } else {
        return date.toLocaleDateString()
      }
    }
  }

  const tabs = [
    { id: 'recent', label: 'Recent Activity', count: activity?.length || 0 },
    { id: 'courses', label: 'Courses', count: courses?.length || 0 },
    { id: 'achievements', label: 'Achievements', count: achievements?.length || 0 }
  ]

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 0.2 }}
      className="bg-white rounded-xl shadow-lg p-6"
    >
      {/* Tab Navigation */}
      <div className="flex space-x-6 border-b border-gray-200 mb-6">
        {tabs.map((tab) => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id as any)}
            className={`pb-3 px-1 border-b-2 font-medium text-sm transition-colors ${
              activeTab === tab.id
                ? 'border-blue-500 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700'
            }`}
          >
            {tab.label}
            {tab.count > 0 && (
              <span className={`ml-2 px-2 py-1 rounded-full text-xs ${
                activeTab === tab.id
                  ? 'bg-blue-100 text-blue-600'
                  : 'bg-gray-100 text-gray-500'
              }`}>
                {tab.count}
              </span>
            )}
          </button>
        ))}
      </div>

      {/* Recent Activity Tab */}
      {activeTab === 'recent' && (
        <div>
          <h3 className="text-lg font-medium text-gray-900 mb-4">Recent Activity</h3>
          
          {activityLoading ? (
            <div className="space-y-4">
              {[...Array(5)].map((_, i) => (
                <div key={i} className="animate-pulse flex items-center space-x-4">
                  <div className="w-10 h-10 bg-gray-200 rounded-lg" />
                  <div className="flex-1 space-y-2">
                    <div className="h-4 bg-gray-200 rounded w-3/4" />
                    <div className="h-3 bg-gray-200 rounded w-1/2" />
                  </div>
                </div>
              ))}
            </div>
          ) : activity && activity.length > 0 ? (
            <div className="space-y-4">
              {activity.map((item: any, index: number) => {
                const Icon = getActivityIcon(item.type)
                const colorClasses = getActivityColor(item.type)
                
                return (
                  <motion.div
                    key={item.id}
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: index * 0.05 }}
                    className="flex items-start space-x-4 p-4 hover:bg-gray-50 rounded-lg transition-colors"
                  >
                    <div className={`flex-shrink-0 w-10 h-10 rounded-lg flex items-center justify-center ${colorClasses}`}>
                      <Icon className="w-5 h-5" />
                    </div>
                    
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-medium text-gray-900">
                        {item.description}
                      </p>
                      <div className="flex items-center mt-1 text-xs text-gray-500">
                        <CalendarIcon className="w-3 h-3 mr-1" />
                        <span>{formatDate(item.createdAt)}</span>
                        {item.entityId && (
                          <>
                            <span className="mx-2">•</span>
                            <Link 
                              href={item.entityUrl || '#'}
                              className="text-blue-600 hover:text-blue-700"
                            >
                              View Details
                            </Link>
                          </>
                        )}
                      </div>
                    </div>
                  </motion.div>
                )
              })}
            </div>
          ) : (
            <div className="text-center py-8 text-gray-500">
              <ClockIcon className="w-12 h-12 mx-auto text-gray-300 mb-3" />
              <p>No recent activity</p>
            </div>
          )}
        </div>
      )}

      {/* Courses Tab */}
      {activeTab === 'courses' && (
        <div>
          <h3 className="text-lg font-medium text-gray-900 mb-4">
            {user.role === 'student' ? 'Enrolled Courses' : 'Created Courses'}
          </h3>
          
          {coursesLoading ? (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {[...Array(4)].map((_, i) => (
                <div key={i} className="animate-pulse">
                  <div className="h-32 bg-gray-200 rounded-lg mb-3" />
                  <div className="h-4 bg-gray-200 rounded mb-2" />
                  <div className="h-3 bg-gray-200 rounded w-2/3" />
                </div>
              ))}
            </div>
          ) : courses && courses.length > 0 ? (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {courses.map((course: any, index: number) => (
                <motion.div
                  key={course.id}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: index * 0.1 }}
                  className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow"
                >
                  <div className="flex items-start space-x-3">
                    <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center">
                      <BookOpenIcon className="w-6 h-6 text-blue-600" />
                    </div>
                    
                    <div className="flex-1 min-w-0">
                      <h4 className="font-medium text-gray-900 line-clamp-1">
                        {course.title}
                      </h4>
                      <p className="text-sm text-gray-600 line-clamp-2 mt-1">
                        {course.description}
                      </p>
                      
                      <div className="flex items-center justify-between mt-3">
                        <div className="flex items-center space-x-4 text-xs text-gray-500">
                          {user.role === 'student' && course.progress !== undefined && (
                            <span>{course.progress}% complete</span>
                          )}
                          {user.role === 'teacher' && (
                            <span>{course.studentsCount || 0} students</span>
                          )}
                        </div>
                        
                        <Link 
                          href={`/courses/${course.id}`}
                          className="text-sm text-blue-600 hover:text-blue-700 font-medium"
                        >
                          View Course
                        </Link>
                      </div>

                      {user.role === 'student' && course.progress !== undefined && (
                        <div className="mt-2">
                          <div className="w-full bg-gray-200 rounded-full h-1.5">
                            <div 
                              className="bg-blue-600 h-1.5 rounded-full transition-all duration-300"
                              style={{ width: `${course.progress}%` }}
                            />
                          </div>
                        </div>
                      )}
                    </div>
                  </div>
                </motion.div>
              ))}
            </div>
          ) : (
            <div className="text-center py-8 text-gray-500">
              <BookOpenIcon className="w-12 h-12 mx-auto text-gray-300 mb-3" />
              <p>
                {user.role === 'student' ? 'No enrolled courses' : 'No created courses'}
              </p>
            </div>
          )}
        </div>
      )}

      {/* Achievements Tab */}
      {activeTab === 'achievements' && (
        <div>
          <h3 className="text-lg font-medium text-gray-900 mb-4">Achievements</h3>
          
          {achievementsLoading ? (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {[...Array(6)].map((_, i) => (
                <div key={i} className="animate-pulse flex items-center space-x-3 p-4">
                  <div className="w-12 h-12 bg-gray-200 rounded-lg" />
                  <div className="flex-1 space-y-2">
                    <div className="h-4 bg-gray-200 rounded" />
                    <div className="h-3 bg-gray-200 rounded w-2/3" />
                  </div>
                </div>
              ))}
            </div>
          ) : achievements && achievements.length > 0 ? (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {achievements.map((achievement: any, index: number) => (
                <motion.div
                  key={achievement.id}
                  initial={{ opacity: 0, scale: 0.9 }}
                  animate={{ opacity: 1, scale: 1 }}
                  transition={{ delay: index * 0.05 }}
                  className="flex items-center space-x-4 p-4 border border-gray-200 rounded-lg hover:bg-yellow-50 transition-colors"
                >
                  <div className="w-12 h-12 bg-yellow-100 rounded-lg flex items-center justify-center">
                    <TrophyIcon className="w-6 h-6 text-yellow-600" />
                  </div>
                  
                  <div className="flex-1 min-w-0">
                    <h4 className="font-medium text-gray-900">
                      {achievement.title}
                    </h4>
                    <p className="text-sm text-gray-600 mt-1">
                      {achievement.description}
                    </p>
                    <p className="text-xs text-gray-500 mt-2">
                      Earned {formatDate(achievement.earnedAt)}
                    </p>
                  </div>
                </motion.div>
              ))}
            </div>
          ) : (
            <div className="text-center py-8 text-gray-500">
              <TrophyIcon className="w-12 h-12 mx-auto text-gray-300 mb-3" />
              <p>No achievements earned yet</p>
              <p className="text-sm mt-2">
                Complete courses and quizzes to earn achievements!
              </p>
            </div>
          )}
        </div>
      )}
    </motion.div>
  )
}
