// src/components/notifications/NotificationBell.tsx
'use client'

import { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { useApi } from '@/hooks/useApi'
import { useAuth } from '@/contexts/AuthContext'
import { NotificationCenter } from './NotificationCenter'
import { BellIcon } from '@heroicons/react/24/outline'

export function NotificationBell() {
  const [isOpen, setIsOpen] = useState(false)
  const [unreadCount, setUnreadCount] = useState(0)
  
  const { user } = useAuth()
  const { useNotifications } = useApi()

  const { data: notificationsData = { notifications: [], total: 0, unreadCount: 0 } } = useNotifications(user?.id)

  useEffect(() => {
    const count = notificationsData.notifications.filter((n: any) => !n.isRead).length
    setUnreadCount(count)
  }, [notificationsData.notifications])

  // Real-time notification updates
  useEffect(() => {
    if (!user?.id) return

    // In a real app, this would be a WebSocket connection
    const interval = setInterval(() => {
      // Refetch notifications every minute
    }, 60000)

    return () => clearInterval(interval)
  }, [user?.id])

  const handleToggle = () => {
    setIsOpen(!isOpen)
  }

  return (
    <>
      <motion.button
        whileHover={{ scale: 1.05 }}
        whileTap={{ scale: 0.95 }}
        onClick={handleToggle}
        className="relative p-2 text-gray-600 hover:text-gray-800 hover:bg-gray-100 rounded-lg transition-colors"
      >
        <BellIcon className="w-6 h-6" />
        
        <AnimatePresence>
          {unreadCount > 0 && (
            <motion.div
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              exit={{ scale: 0 }}
              className="absolute -top-1 -right-1 bg-red-500 text-white text-xs font-bold rounded-full min-w-[20px] h-5 flex items-center justify-center px-1"
            >
              {unreadCount > 99 ? '99+' : unreadCount}
            </motion.div>
          )}
        </AnimatePresence>
      </motion.button>

      <NotificationCenter
        isOpen={isOpen}
        onClose={() => setIsOpen(false)}
      />
    </>
  )
}
