'use client'

import { createContext, useContext, useEffect, useState } from 'react'
// Mock Firebase functions for build compatibility
const getFCMToken = async (): Promise<string | null> => {
  console.warn('Firebase not configured')
  return null
}

const onForegroundMessage = (callback: (payload: any) => void) => {
  console.warn('Firebase not configured')
  return () => {}
}
import { useAuth } from './AuthContext'
import { useToast } from './ToastContext'

interface NotificationContextType {
  token: string | null
  isSupported: boolean
  requestPermission: () => Promise<boolean>
  refreshToken: () => Promise<void>
}

const NotificationContext = createContext<NotificationContextType | undefined>(undefined)

export function NotificationProvider({ children }: { children: React.ReactNode }) {
  const [token, setToken] = useState<string | null>(null)
  const [isSupported, setIsSupported] = useState(false)
  const { user } = useAuth()
  const { success: showSuccess, info: showInfo } = useToast()

  useEffect(() => {
    // Check if browser supports notifications and service workers
    const supported = 'Notification' in window && 'serviceWorker' in navigator
    setIsSupported(supported)

    if (supported) {
      initializeNotifications()
    }
  }, [])

  useEffect(() => {
    if (user && token) {
      // Register device token with backend
      registerDeviceToken(token)
    }
  }, [user, token])

  const initializeNotifications = async () => {
    try {
      // Register service worker
      if ('serviceWorker' in navigator) {
        const registration = await navigator.serviceWorker.register('/firebase-messaging-sw.js')
        console.log('Service Worker registered:', registration)
      }

      // Request initial token
      if (Notification.permission === 'granted') {
        await getAndSetToken()
      }

      // Listen for foreground messages
      onForegroundMessage((payload) => {
        showInfo(
          `${payload.notification?.title || 'New notification'}: ${payload.notification?.body || ''}`
        )
      })
    } catch (error) {
      console.error('Error initializing notifications:', error)
    }
  }

  const requestPermission = async (): Promise<boolean> => {
    try {
      const permission = await Notification.requestPermission()
      
      if (permission === 'granted') {
        await getAndSetToken()
        showSuccess('Notifications enabled successfully!')
        return true
      } else {
        console.log('Notification permission denied')
        return false
      }
    } catch (error) {
      console.error('Error requesting notification permission:', error)
      return false
    }
  }

  const getAndSetToken = async () => {
    try {
      const fcmToken = await getFCMToken()
      if (fcmToken) {
        setToken(fcmToken)
      }
    } catch (error) {
      console.error('Error getting FCM token:', error)
    }
  }

  const refreshToken = async () => {
    await getAndSetToken()
  }

  const registerDeviceToken = async (deviceToken: string) => {
    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_GATEWAY_URL}/sync-messaging/api/v1/devices/register`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify({
          userId: user?.id,
          deviceToken,
          platform: 'web',
          deviceInfo: {
            userAgent: navigator.userAgent,
            language: navigator.language,
            timezone: Intl.DateTimeFormat().resolvedOptions().timeZone
          }
        })
      })

      if (!response.ok) {
        throw new Error('Failed to register device token')
      }

      console.log('Device token registered successfully')
    } catch (error) {
      console.error('Error registering device token:', error)
    }
  }

  const value = {
    token,
    isSupported,
    requestPermission,
    refreshToken
  }

  return (
    <NotificationContext.Provider value={value}>
      {children}
    </NotificationContext.Provider>
  )
}

export function useNotificationPermission() {
  const context = useContext(NotificationContext)
  if (context === undefined) {
    throw new Error('useNotificationPermission must be used within a NotificationProvider')
  }
  return context
}
