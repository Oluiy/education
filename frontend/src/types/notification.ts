export interface Notification {
  id: string
  title: string
  message: string
  type: 'info' | 'success' | 'warning' | 'error'
  read: boolean
  userId: string
  createdAt: string
  updatedAt: string
  actionUrl?: string
  actionText?: string
  category?: NotificationCategory
  priority?: NotificationPriority
  metadata?: Record<string, any>
}

export type NotificationCategory = 
  | 'assignment'
  | 'grade'
  | 'announcement'
  | 'reminder'
  | 'system'
  | 'quiz'
  | 'course'
  | 'message'

export type NotificationPriority = 'low' | 'medium' | 'high' | 'urgent'

export interface NotificationSettings {
  id: string
  userId: string
  emailNotifications: boolean
  pushNotifications: boolean
  categories: {
    assignment: boolean
    grade: boolean
    announcement: boolean
    reminder: boolean
    system: boolean
    quiz: boolean
    course: boolean
    message: boolean
  }
  frequency: 'immediate' | 'daily' | 'weekly'
  quietHours: {
    enabled: boolean
    start: string
    end: string
  }
}

export interface CreateNotificationRequest {
  title: string
  message: string
  type: Notification['type']
  userId: string
  actionUrl?: string
  actionText?: string
  category?: NotificationCategory
  priority?: NotificationPriority
  metadata?: Record<string, any>
}

export interface UpdateNotificationRequest {
  read?: boolean
}

export interface NotificationFilters {
  read?: boolean
  type?: Notification['type']
  category?: NotificationCategory
  priority?: NotificationPriority
  dateFrom?: string
  dateTo?: string
}

export interface NotificationStats {
  total: number
  unread: number
  byType: Record<Notification['type'], number>
  byCategory: Record<NotificationCategory, number>
  recent: Notification[]
}
