'use client'

import { useState } from 'react'
import { motion } from 'framer-motion'
import { useNotificationPermission } from '@/contexts/NotificationContext'
import { 
  BellIcon, 
  CheckIcon, 
  XMarkIcon,
  ExclamationTriangleIcon
} from '@heroicons/react/24/outline'

export function NotificationPermissionBanner() {
  const [dismissed, setDismissed] = useState(false)
  const { isSupported, requestPermission } = useNotificationPermission()

  // Don't show if notifications aren't supported or already granted or dismissed
  if (!isSupported || Notification.permission === 'granted' || dismissed) {
    return null
  }

  const handleEnable = async () => {
    const granted = await requestPermission()
    if (granted) {
      setDismissed(true)
    }
  }

  const handleDismiss = () => {
    setDismissed(true)
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: -50 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -50 }}
      className="bg-gradient-to-r from-blue-500 to-purple-600 text-white px-4 py-3 shadow-lg"
    >
      <div className="max-w-7xl mx-auto flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <BellIcon className="w-6 h-6 flex-shrink-0" />
          <div>
            <p className="font-medium">Enable notifications to stay updated</p>
            <p className="text-sm opacity-90">Get instant alerts for new assignments, grades, and messages</p>
          </div>
        </div>
        
        <div className="flex items-center space-x-2">
          <button
            onClick={handleEnable}
            className="bg-white text-blue-600 px-4 py-2 rounded-lg font-medium hover:bg-blue-50 transition-colors flex items-center space-x-2"
          >
            <CheckIcon className="w-4 h-4" />
            <span>Enable</span>
          </button>
          <button
            onClick={handleDismiss}
            className="text-white hover:text-blue-100 p-2 rounded-lg transition-colors"
          >
            <XMarkIcon className="w-5 h-5" />
          </button>
        </div>
      </div>
    </motion.div>
  )
}

export function NotificationStatus() {
  const { isSupported, token, requestPermission } = useNotificationPermission()

  if (!isSupported) {
    return (
      <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
        <div className="flex items-center space-x-3">
          <ExclamationTriangleIcon className="w-6 h-6 text-yellow-600" />
          <div>
            <h3 className="font-medium text-yellow-800">Notifications not supported</h3>
            <p className="text-sm text-yellow-700">Your browser doesn't support push notifications</p>
          </div>
        </div>
      </div>
    )
  }

  const permission = Notification.permission

  if (permission === 'granted' && token) {
    return (
      <div className="bg-green-50 border border-green-200 rounded-lg p-4">
        <div className="flex items-center space-x-3">
          <CheckIcon className="w-6 h-6 text-green-600" />
          <div>
            <h3 className="font-medium text-green-800">Notifications enabled</h3>
            <p className="text-sm text-green-700">You'll receive push notifications for important updates</p>
          </div>
        </div>
      </div>
    )
  }

  if (permission === 'denied') {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-4">
        <div className="flex items-center space-x-3">
          <XMarkIcon className="w-6 h-6 text-red-600" />
          <div>
            <h3 className="font-medium text-red-800">Notifications blocked</h3>
            <p className="text-sm text-red-700">Please enable notifications in your browser settings</p>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <BellIcon className="w-6 h-6 text-blue-600" />
          <div>
            <h3 className="font-medium text-blue-800">Enable notifications</h3>
            <p className="text-sm text-blue-700">Stay updated with important alerts and messages</p>
          </div>
        </div>
        <button
          onClick={requestPermission}
          className="bg-blue-600 text-white px-4 py-2 rounded-lg font-medium hover:bg-blue-700 transition-colors"
        >
          Enable
        </button>
      </div>
    </div>
  )
}
