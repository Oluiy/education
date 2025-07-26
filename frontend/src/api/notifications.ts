// src/api/notifications.ts
export interface Notification {
  id: string
  userId: string
  type: 'assignment' | 'grade' | 'announcement' | 'reminder' | 'system' | 'quiz_assigned' | 'quiz_reminder' | 'course_enrolled' | 'course_updated' | 'assignment_graded' | 'social'
  title: string
  message: string
  data?: Record<string, any>
  entityId?: string
  actionUrl?: string
  actionText?: string
  isRead: boolean
  createdAt: string
  readAt?: string
}

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

export async function getNotifications(params?: {
  isRead?: boolean
  type?: string
  page?: number
  limit?: number
}): Promise<{ notifications: Notification[]; total: number; unreadCount: number }> {
  const token = localStorage.getItem('auth_token')
  const searchParams = new URLSearchParams()
  
  if (params) {
    Object.entries(params).forEach(([key, value]) => {
      if (value !== undefined) searchParams.append(key, value.toString())
    })
  }

  const response = await fetch(`${API_URL}/notifications?${searchParams}`, {
    headers: { 'Authorization': `Bearer ${token}` }
  })
  if (!response.ok) throw new Error('Failed to fetch notifications')
  return response.json()
}

export async function markAsRead(id: string): Promise<void> {
  const token = localStorage.getItem('auth_token')
  const response = await fetch(`${API_URL}/notifications/${id}/read`, {
    method: 'POST',
    headers: { 'Authorization': `Bearer ${token}` }
  })
  if (!response.ok) throw new Error('Failed to mark notification as read')
}

export async function markAllAsRead(): Promise<void> {
  const token = localStorage.getItem('auth_token')
  const response = await fetch(`${API_URL}/notifications/read-all`, {
    method: 'POST',
    headers: { 'Authorization': `Bearer ${token}` }
  })
  if (!response.ok) throw new Error('Failed to mark all notifications as read')
}

export async function deleteNotification(id: string): Promise<void> {
  const token = localStorage.getItem('auth_token')
  const response = await fetch(`${API_URL}/notifications/${id}`, {
    method: 'DELETE',
    headers: { 'Authorization': `Bearer ${token}` }
  })
  if (!response.ok) throw new Error('Failed to delete notification')
}

export async function createNotification(data: {
  userId: string | string[]
  type: string
  title: string
  message: string
  data?: Record<string, any>
}): Promise<Notification> {
  const token = localStorage.getItem('auth_token')
  const response = await fetch(`${API_URL}/notifications`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`
    },
    body: JSON.stringify(data)
  })
  if (!response.ok) throw new Error('Failed to create notification')
  return response.json()
}

// Additional methods needed by useApi hooks
export async function getNotification(id: string): Promise<Notification> {
  const token = localStorage.getItem('auth_token')
  const response = await fetch(`${API_URL}/notifications/${id}`, {
    headers: { 'Authorization': `Bearer ${token}` }
  })
  if (!response.ok) throw new Error('Failed to fetch notification')
  return response.json()
}

export async function markNotificationAsRead(id: string): Promise<void> {
  return markAsRead(id)
}

export async function markAllNotificationsAsRead(userId: string): Promise<void> {
  return markAllAsRead()
}

export async function deleteAllNotifications(userId: string): Promise<void> {
  const token = localStorage.getItem('auth_token')
  const response = await fetch(`${API_URL}/notifications/bulk-delete`, {
    method: 'DELETE',
    headers: { 'Authorization': `Bearer ${token}` }
  })
  if (!response.ok) throw new Error('Failed to delete all notifications')
}

export async function getNotificationSettings(userId: string): Promise<any> {
  const token = localStorage.getItem('auth_token')
  const response = await fetch(`${API_URL}/users/${userId}/notification-settings`, {
    headers: { 'Authorization': `Bearer ${token}` }
  })
  if (!response.ok) throw new Error('Failed to fetch notification settings')
  return response.json()
}

export async function updateNotificationSettings(data: { userId: string; settings: any }): Promise<any> {
  const token = localStorage.getItem('auth_token')
  const response = await fetch(`${API_URL}/users/${data.userId}/notification-settings`, {
    method: 'PUT',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`
    },
    body: JSON.stringify(data.settings)
  })
  if (!response.ok) throw new Error('Failed to update notification settings')
  return response.json()
}
