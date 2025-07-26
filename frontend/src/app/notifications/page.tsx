// src/app/notifications/page.tsx
'use client'

import { useState } from 'react'
import { motion } from 'framer-motion'
import { useApi } from '../../hooks/useApi'
import { useAuth } from '../../contexts/AuthContext'
import { NotificationCard } from '../../components/notifications/NotificationCard'
import { LoadingSpinner } from '../../components/ui/LoadingSpinner'
import {
  BellIcon,
  CheckIcon,
  TrashIcon,
  FunnelIcon,
  Cog6ToothIcon,
  MagnifyingGlassIcon
} from '@heroicons/react/24/outline'

export default function NotificationsPage() {
  const [filter, setFilter] = useState<string>('all')
  const [searchTerm, setSearchTerm] = useState('')
  const [showSettings, setShowSettings] = useState(false)

  const { user } = useAuth()
  const { 
    useNotifications, 
    markAllNotificationsAsRead, 
    deleteAllNotifications,
    useNotificationSettings,
    updateNotificationSettings
  } = useApi()

  const { 
    data: notificationsData = { notifications: [], total: 0, unreadCount: 0 }, 
    isLoading,
    error 
  } = useNotifications(user?.id)

  const { data: settings } = useNotificationSettings(user?.id)

  const filteredNotifications = notificationsData.notifications.filter((notification: any) => {
    // Filter by type
    if (filter !== 'all' && filter !== 'read' && filter !== 'unread' && notification.type !== filter) {
      return false
    }

    // Filter by read status
    if (filter === 'read' && !notification.isRead) return false
    if (filter === 'unread' && notification.isRead) return false

    // Filter by search term
    if (searchTerm) {
      const searchLower = searchTerm.toLowerCase()
      return (
        notification.title.toLowerCase().includes(searchLower) ||
        notification.message.toLowerCase().includes(searchLower)
      )
    }

    return true
  })

  const unreadCount = notificationsData.notifications.filter((n: any) => !n.isRead).length

  const handleMarkAllAsRead = async () => {
    try {
      await markAllNotificationsAsRead.mutateAsync(user?.id!)
    } catch (error) {
      console.error('Failed to mark all notifications as read:', error)
    }
  }

  const handleDeleteAll = async () => {
    if (window.confirm('Are you sure you want to delete all notifications? This action cannot be undone.')) {
      try {
        await deleteAllNotifications.mutateAsync(user?.id!)
      } catch (error) {
        console.error('Failed to delete all notifications:', error)
      }
    }
  }

  const toggleNotificationSetting = async (type: string, enabled: boolean) => {
    try {
      await updateNotificationSettings.mutateAsync({
        userId: user?.id!,
        settings: {
          ...settings,
          [type]: enabled
        }
      })
    } catch (error) {
      console.error('Failed to update notification settings:', error)
    }
  }

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <LoadingSpinner size="lg" />
      </div>
    )
  }

  if (error) {
    return (
      <div className="text-center py-12">
        <p className="text-red-600">Failed to load notifications</p>
      </div>
    )
  }

  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* Header */}
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Notifications</h1>
          <p className="text-gray-600 mt-2">
            Stay updated with your courses, quizzes, and announcements
          </p>
          {unreadCount > 0 && (
            <p className="text-sm text-blue-600 mt-1">
              You have {unreadCount} unread notification{unreadCount !== 1 ? 's' : ''}
            </p>
          )}
        </div>

        <div className="flex items-center space-x-3">
          <button
            onClick={() => setShowSettings(!showSettings)}
            className="flex items-center space-x-2 px-4 py-2 text-gray-700 border border-gray-300 rounded-lg hover:bg-gray-50"
          >
            <Cog6ToothIcon className="w-4 h-4" />
            <span>Settings</span>
          </button>

          {unreadCount > 0 && (
            <button
              onClick={handleMarkAllAsRead}
              disabled={markAllNotificationsAsRead.isPending}
              className="flex items-center space-x-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
            >
              <CheckIcon className="w-4 h-4" />
              <span>Mark All Read</span>
            </button>
          )}
        </div>
      </div>

      {/* Settings Panel */}
      {showSettings && settings && (
        <motion.div
          initial={{ opacity: 0, height: 0 }}
          animate={{ opacity: 1, height: 'auto' }}
          exit={{ opacity: 0, height: 0 }}
          className="bg-white rounded-xl shadow-lg p-6 mb-8"
        >
          <h2 className="text-xl font-semibold text-gray-900 mb-4">Notification Settings</h2>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {[
              { 
                key: 'emailNotifications', 
                label: 'Email Notifications',
                description: 'Receive notifications via email'
              },
              { 
                key: 'pushNotifications', 
                label: 'Push Notifications',
                description: 'Receive browser push notifications'
              },
              { 
                key: 'quizReminders', 
                label: 'Quiz Reminders',
                description: 'Get reminded about upcoming quiz deadlines'
              },
              { 
                key: 'courseUpdates', 
                label: 'Course Updates',
                description: 'Notifications about course content changes'
              },
              { 
                key: 'announcements', 
                label: 'Announcements',
                description: 'Important announcements from instructors'
              },
              { 
                key: 'gradeUpdates', 
                label: 'Grade Updates',
                description: 'Notifications when assignments are graded'
              }
            ].map(({ key, label, description }) => (
              <div key={key} className="flex items-start space-x-3">
                <input
                  type="checkbox"
                  id={key}
                  checked={settings[key] || false}
                  onChange={(e) => toggleNotificationSetting(key, e.target.checked)}
                  className="mt-1 rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                />
                <div className="flex-1">
                  <label htmlFor={key} className="text-sm font-medium text-gray-900 cursor-pointer">
                    {label}
                  </label>
                  <p className="text-sm text-gray-500 mt-1">{description}</p>
                </div>
              </div>
            ))}
          </div>
        </motion.div>
      )}

      {/* Filters */}
      <div className="bg-white rounded-xl shadow-lg p-6 mb-8">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center space-x-4">
            <FunnelIcon className="w-5 h-5 text-gray-400" />
            <span className="font-medium text-gray-700">Filter & Search</span>
          </div>

          {notificationsData.notifications.length > 0 && (
            <button
              onClick={handleDeleteAll}
              disabled={deleteAllNotifications.isPending}
              className="flex items-center space-x-2 px-3 py-1 text-sm text-red-600 hover:text-red-700 border border-red-200 rounded-lg hover:bg-red-50 disabled:opacity-50"
            >
              <TrashIcon className="w-4 h-4" />
              <span>Delete All</span>
            </button>
          )}
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {/* Search */}
          <div className="relative">
            <MagnifyingGlassIcon className="w-5 h-5 absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" />
            <input
              type="text"
              placeholder="Search notifications..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>

          {/* Type Filter */}
          <select
            value={filter}
            onChange={(e) => setFilter(e.target.value)}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          >
            <option value="all">All Notifications</option>
            <option value="unread">Unread Only</option>
            <option value="read">Read Only</option>
            <option value="quiz_assigned">Quiz Assignments</option>
            <option value="quiz_reminder">Quiz Reminders</option>
            <option value="course_enrolled">Course Enrollments</option>
            <option value="course_updated">Course Updates</option>
            <option value="assignment_graded">Grade Updates</option>
            <option value="announcement">Announcements</option>
            <option value="system">System Notifications</option>
          </select>
        </div>

        <div className="mt-4 text-sm text-gray-500">
          Showing {filteredNotifications.length} of {notificationsData.notifications.length} notifications
        </div>
      </div>

      {/* Notifications List */}
      {filteredNotifications.length > 0 ? (
        <div className="space-y-4">
          {filteredNotifications.map((notification: any, index: number) => (
            <motion.div
              key={notification.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.05 }}
            >
              <NotificationCard notification={notification} />
            </motion.div>
          ))}
        </div>
      ) : (
        <div className="text-center py-12">
          <BellIcon className="w-16 h-16 mx-auto text-gray-300 mb-4" />
          <h3 className="text-xl font-medium text-gray-900 mb-2">No Notifications Found</h3>
          <p className="text-gray-600">
            {searchTerm || filter !== 'all'
              ? 'No notifications match your current filters.'
              : "You don't have any notifications yet."
            }
          </p>
        </div>
      )}
    </div>
  )
}
