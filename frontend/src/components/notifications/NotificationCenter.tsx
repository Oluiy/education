// src/components/notifications/NotificationCenter.tsx
'use client'

import { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { useApi } from '@/hooks/useApi'
import { useAuth } from '@/contexts/AuthContext'
import { NotificationCard } from './NotificationCard'
import { Notification } from '@/api/notifications'
import {
  BellIcon,
  CheckIcon,
  TrashIcon,
  FunnelIcon,
  XMarkIcon,
  Cog6ToothIcon
} from '@heroicons/react/24/outline'

interface NotificationCenterProps {
  isOpen: boolean
  onClose: () => void
}

export function NotificationCenter({ isOpen, onClose }: NotificationCenterProps) {
  const [filter, setFilter] = useState<string>('all')
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
    data: notificationsData, 
    isLoading,
    refetch: refetchNotifications 
  } = useNotifications(user?.id)

  const notifications = notificationsData?.notifications || []
  const totalNotifications = notificationsData?.total || 0
  const apiUnreadCount = notificationsData?.unreadCount || 0

  const { data: settings } = useNotificationSettings(user?.id)

  // Real-time updates
  useEffect(() => {
    if (!isOpen) return

    const interval = setInterval(() => {
      refetchNotifications()
    }, 30000) // Refetch every 30 seconds

    return () => clearInterval(interval)
  }, [isOpen, refetchNotifications])

  const filteredNotifications = notifications.filter(notification => {
    if (filter === 'all') return true
    if (filter === 'unread') return !notification.isRead
    if (filter === 'read') return notification.isRead
    return notification.type === filter
  })

  const unreadCount = notifications.filter(n => !n.isRead).length

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

  if (!isOpen) return null

  return (
    <AnimatePresence>
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        className="fixed inset-0 bg-black bg-opacity-50 z-50"
        onClick={onClose}
      >
        <motion.div
          initial={{ opacity: 0, x: 400 }}
          animate={{ opacity: 1, x: 0 }}
          exit={{ opacity: 0, x: 400 }}
          transition={{ type: 'spring', damping: 25, stiffness: 200 }}
          className="absolute right-0 top-0 h-full w-full max-w-md bg-white shadow-2xl"
          onClick={(e) => e.stopPropagation()}
        >
          <div className="flex flex-col h-full">
            {/* Header */}
            <div className="flex items-center justify-between p-6 border-b border-gray-200">
              <div className="flex items-center space-x-3">
                <BellIcon className="w-6 h-6 text-gray-700" />
                <div>
                  <h2 className="text-lg font-semibold text-gray-900">Notifications</h2>
                  {unreadCount > 0 && (
                    <p className="text-sm text-gray-600">{unreadCount} unread</p>
                  )}
                </div>
              </div>

              <div className="flex items-center space-x-2">
                <button
                  onClick={() => setShowSettings(!showSettings)}
                  className="p-2 text-gray-500 hover:text-gray-700 rounded-lg hover:bg-gray-100"
                >
                  <Cog6ToothIcon className="w-5 h-5" />
                </button>
                
                <button
                  onClick={onClose}
                  className="p-2 text-gray-500 hover:text-gray-700 rounded-lg hover:bg-gray-100"
                >
                  <XMarkIcon className="w-5 h-5" />
                </button>
              </div>
            </div>

            {/* Settings Panel */}
            <AnimatePresence>
              {showSettings && settings && (
                <motion.div
                  initial={{ height: 0, opacity: 0 }}
                  animate={{ height: 'auto', opacity: 1 }}
                  exit={{ height: 0, opacity: 0 }}
                  className="border-b border-gray-200 bg-gray-50 p-4 overflow-hidden"
                >
                  <h3 className="text-sm font-medium text-gray-900 mb-3">Notification Settings</h3>
                  
                  <div className="space-y-3">
                    {[
                      { key: 'emailNotifications', label: 'Email Notifications' },
                      { key: 'pushNotifications', label: 'Push Notifications' },
                      { key: 'quizReminders', label: 'Quiz Reminders' },
                      { key: 'courseUpdates', label: 'Course Updates' },
                      { key: 'announcements', label: 'Announcements' }
                    ].map(({ key, label }) => (
                      <label key={key} className="flex items-center justify-between">
                        <span className="text-sm text-gray-700">{label}</span>
                        <input
                          type="checkbox"
                          checked={settings[key] || false}
                          onChange={(e) => toggleNotificationSetting(key, e.target.checked)}
                          className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                        />
                      </label>
                    ))}
                  </div>
                </motion.div>
              )}
            </AnimatePresence>

            {/* Filters and Actions */}
            <div className="p-4 border-b border-gray-200 bg-gray-50">
              <div className="flex items-center justify-between mb-3">
                <div className="flex items-center space-x-2">
                  <FunnelIcon className="w-4 h-4 text-gray-500" />
                  <select
                    value={filter}
                    onChange={(e) => setFilter(e.target.value)}
                    className="text-sm border border-gray-300 rounded-lg px-3 py-1 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  >
                    <option value="all">All</option>
                    <option value="unread">Unread</option>
                    <option value="read">Read</option>
                    <option value="quiz_assigned">Quizzes</option>
                    <option value="course_enrolled">Courses</option>
                    <option value="announcement">Announcements</option>
                    <option value="assignment_graded">Grades</option>
                    <option value="system">System</option>
                  </select>
                </div>

                <div className="flex items-center space-x-2">
                  {unreadCount > 0 && (
                    <button
                      onClick={handleMarkAllAsRead}
                      disabled={markAllNotificationsAsRead.isPending}
                      className="text-sm text-blue-600 hover:text-blue-700 disabled:opacity-50"
                    >
                      <CheckIcon className="w-4 h-4" />
                    </button>
                  )}
                  
                  {notifications.length > 0 && (
                    <button
                      onClick={handleDeleteAll}
                      disabled={deleteAllNotifications.isPending}
                      className="text-sm text-red-600 hover:text-red-700 disabled:opacity-50"
                    >
                      <TrashIcon className="w-4 h-4" />
                    </button>
                  )}
                </div>
              </div>

              <div className="text-xs text-gray-500">
                Showing {filteredNotifications.length} of {notifications.length} notifications
              </div>
            </div>

            {/* Notifications List */}
            <div className="flex-1 overflow-y-auto">
              {isLoading ? (
                <div className="flex items-center justify-center h-32">
                  <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600" />
                </div>
              ) : filteredNotifications.length > 0 ? (
                <div className="divide-y divide-gray-100">
                  {filteredNotifications.map((notification: any) => (
                    <NotificationCard
                      key={notification.id}
                      notification={notification}
                      compact
                      showActions={false}
                    />
                  ))}
                </div>
              ) : (
                <div className="flex flex-col items-center justify-center h-64 text-gray-500">
                  <BellIcon className="w-12 h-12 text-gray-300 mb-4" />
                  <p className="text-gray-600 font-medium">No notifications</p>
                  <p className="text-sm text-gray-500 text-center mt-2">
                    {filter === 'unread' 
                      ? "You're all caught up! No unread notifications."
                      : filter !== 'all'
                      ? `No ${filter.replace('_', ' ')} notifications found.`
                      : "You don't have any notifications yet."
                    }
                  </p>
                </div>
              )}
            </div>

            {/* Footer */}
            <div className="p-4 border-t border-gray-200 bg-gray-50">
              <div className="text-center">
                <a
                  href="/notifications"
                  onClick={onClose}
                  className="text-sm text-blue-600 hover:text-blue-700 font-medium"
                >
                  View All Notifications
                </a>
              </div>
            </div>
          </div>
        </motion.div>
      </motion.div>
    </AnimatePresence>
  )
}
