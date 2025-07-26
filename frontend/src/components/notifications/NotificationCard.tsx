// src/components/notifications/NotificationCard.tsx
'use client'

import { motion } from 'framer-motion'
import { Notification } from '../../api/notifications'
import { useApi } from '../../hooks/useApi'
import {
  BellIcon,
  CheckCircleIcon,
  ExclamationTriangleIcon,
  InformationCircleIcon,
  AcademicCapIcon,
  BookOpenIcon,
  UserGroupIcon,
  ClockIcon,
  EyeIcon,
  TrashIcon
} from '@heroicons/react/24/outline'

interface NotificationCardProps {
  notification: Notification
  showActions?: boolean
  compact?: boolean
}

export function NotificationCard({ 
  notification, 
  showActions = true, 
  compact = false 
}: NotificationCardProps) {
  const { markNotificationAsRead, deleteNotification } = useApi()

  const getIcon = () => {
    switch (notification.type) {
      case 'quiz_assigned':
      case 'quiz_reminder':
        return <AcademicCapIcon className="w-5 h-5" />
      case 'course_enrolled':
      case 'course_updated':
        return <BookOpenIcon className="w-5 h-5" />
      case 'assignment_graded':
        return <CheckCircleIcon className="w-5 h-5" />
      case 'announcement':
        return <InformationCircleIcon className="w-5 h-5" />
      case 'system':
        return <ExclamationTriangleIcon className="w-5 h-5" />
      case 'social':
        return <UserGroupIcon className="w-5 h-5" />
      default:
        return <BellIcon className="w-5 h-5" />
    }
  }

  const getIconColor = () => {
    switch (notification.type) {
      case 'quiz_assigned':
      case 'quiz_reminder':
        return 'text-blue-600'
      case 'course_enrolled':
      case 'course_updated':
        return 'text-green-600'
      case 'assignment_graded':
        return 'text-purple-600'
      case 'announcement':
        return 'text-indigo-600'
      case 'system':
        return 'text-yellow-600'
      case 'social':
        return 'text-pink-600'
      default:
        return 'text-gray-600'
    }
  }

  const getBgColor = () => {
    if (notification.isRead) return 'bg-white'
    
    switch (notification.type) {
      case 'quiz_assigned':
      case 'quiz_reminder':
        return 'bg-blue-50'
      case 'course_enrolled':
      case 'course_updated':
        return 'bg-green-50'
      case 'assignment_graded':
        return 'bg-purple-50'
      case 'announcement':
        return 'bg-indigo-50'
      case 'system':
        return 'bg-yellow-50'
      case 'social':
        return 'bg-pink-50'
      default:
        return 'bg-gray-50'
    }
  }

  const handleMarkAsRead = async () => {
    if (!notification.isRead) {
      try {
        await markNotificationAsRead.mutateAsync(notification.id)
      } catch (error) {
        console.error('Failed to mark notification as read:', error)
      }
    }
  }

  const handleDelete = async () => {
    try {
      await deleteNotification.mutateAsync(notification.id)
    } catch (error) {
      console.error('Failed to delete notification:', error)
    }
  }

  const formatTime = (date: string) => {
    const now = new Date()
    const notificationDate = new Date(date)
    const diffInHours = Math.floor((now.getTime() - notificationDate.getTime()) / (1000 * 60 * 60))
    
    if (diffInHours < 1) {
      const diffInMinutes = Math.floor((now.getTime() - notificationDate.getTime()) / (1000 * 60))
      return diffInMinutes <= 1 ? 'Just now' : `${diffInMinutes}m ago`
    } else if (diffInHours < 24) {
      return `${diffInHours}h ago`
    } else {
      const diffInDays = Math.floor(diffInHours / 24)
      if (diffInDays < 7) {
        return `${diffInDays}d ago`
      } else {
        return notificationDate.toLocaleDateString()
      }
    }
  }

  if (compact) {
    return (
      <motion.div
        whileHover={{ backgroundColor: 'rgba(0, 0, 0, 0.02)' }}
        className={`p-3 border-l-4 transition-colors cursor-pointer ${
          notification.isRead ? 'border-gray-200' : 'border-blue-500'
        } ${getBgColor()}`}
        onClick={handleMarkAsRead}
      >
        <div className="flex items-start space-x-3">
          <div className={`flex-shrink-0 ${getIconColor()}`}>
            {getIcon()}
          </div>
          
          <div className="flex-1 min-w-0">
            <p className={`text-sm ${notification.isRead ? 'text-gray-600' : 'text-gray-900 font-medium'}`}>
              {notification.title}
            </p>
            <p className="text-xs text-gray-500 mt-1 line-clamp-1">
              {notification.message}
            </p>
          </div>
          
          <div className="flex-shrink-0 flex items-center space-x-2">
            <span className="text-xs text-gray-400">
              {formatTime(notification.createdAt)}
            </span>
            {!notification.isRead && (
              <div className="w-2 h-2 bg-blue-600 rounded-full" />
            )}
          </div>
        </div>
      </motion.div>
    )
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      whileHover={{ y: -2 }}
      className={`p-6 rounded-xl border transition-all duration-200 ${
        notification.isRead 
          ? 'border-gray-200 bg-white' 
          : 'border-blue-200 shadow-sm'
      } ${getBgColor()}`}
    >
      <div className="flex items-start space-x-4">
        {/* Icon */}
        <div className={`flex-shrink-0 p-2 rounded-lg ${
          notification.isRead ? 'bg-gray-100' : 'bg-white shadow-sm'
        }`}>
          <div className={getIconColor()}>
            {getIcon()}
          </div>
        </div>

        {/* Content */}
        <div className="flex-1 min-w-0">
          <div className="flex items-start justify-between mb-2">
            <h3 className={`text-lg font-medium ${
              notification.isRead ? 'text-gray-700' : 'text-gray-900'
            }`}>
              {notification.title}
            </h3>
            
            <div className="flex items-center space-x-2 ml-4">
              <div className="flex items-center space-x-1 text-sm text-gray-500">
                <ClockIcon className="w-4 h-4" />
                <span>{formatTime(notification.createdAt)}</span>
              </div>
              
              {!notification.isRead && (
                <div className="w-2 h-2 bg-blue-600 rounded-full" />
              )}
            </div>
          </div>

          <p className={`text-gray-600 mb-4 ${
            notification.isRead ? 'text-gray-500' : 'text-gray-700'
          }`}>
            {notification.message}
          </p>

          {/* Metadata */}
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4 text-sm text-gray-500">
              <span className="capitalize">{notification.type.replace('_', ' ')}</span>
              {notification.entityId && (
                <span>ID: {notification.entityId.slice(0, 8)}...</span>
              )}
            </div>

            {/* Actions */}
            {showActions && (
              <div className="flex items-center space-x-2">
                {!notification.isRead && (
                  <button
                    onClick={handleMarkAsRead}
                    disabled={markNotificationAsRead.isPending}
                    className="flex items-center space-x-1 px-3 py-1 text-sm text-blue-600 hover:text-blue-700 border border-blue-200 rounded-lg hover:bg-blue-50 transition-colors disabled:opacity-50"
                  >
                    <EyeIcon className="w-4 h-4" />
                    <span>Mark Read</span>
                  </button>
                )}

                <button
                  onClick={handleDelete}
                  disabled={deleteNotification.isPending}
                  className="flex items-center space-x-1 px-3 py-1 text-sm text-red-600 hover:text-red-700 border border-red-200 rounded-lg hover:bg-red-50 transition-colors disabled:opacity-50"
                >
                  <TrashIcon className="w-4 h-4" />
                  <span>Delete</span>
                </button>
              </div>
            )}
          </div>

          {/* Action Button */}
          {notification.actionUrl && (
            <div className="mt-4">
              <a
                href={notification.actionUrl}
                onClick={handleMarkAsRead}
                className="inline-flex items-center px-4 py-2 bg-blue-600 text-white text-sm font-medium rounded-lg hover:bg-blue-700 transition-colors"
              >
                {notification.actionText || 'View Details'}
              </a>
            </div>
          )}
        </div>
      </div>
    </motion.div>
  )
}
