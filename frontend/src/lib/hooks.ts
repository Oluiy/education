'use client'

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { api } from './api'

// Auth hooks
export const useAuth = () => {
  return useQuery({
    queryKey: ['auth', 'me'],
    queryFn: api.auth.me,
    retry: false,
    staleTime: 5 * 60 * 1000, // 5 minutes
  })
}

export const useLogin = () => {
  const queryClient = useQueryClient()
  
  return useMutation({
    mutationFn: ({ email, password }: { email: string; password: string }) =>
      api.auth.login(email, password),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['auth'] })
    },
  })
}

export const useRegister = () => {
  const queryClient = useQueryClient()
  
  return useMutation({
    mutationFn: (userData: any) => api.auth.register(userData),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['auth'] })
    },
  })
}

export const useLogout = () => {
  const queryClient = useQueryClient()
  
  return useMutation({
    mutationFn: api.auth.logout,
    onSuccess: () => {
      queryClient.clear()
    },
  })
}

// Course hooks
export const useCourses = (params?: { 
  search?: string
  category?: string
  page?: number 
}) => {
  return useQuery({
    queryKey: ['courses', params],
    queryFn: () => api.courses.getAll(params),
    staleTime: 2 * 60 * 1000, // 2 minutes
  })
}

export const useCourse = (id: string) => {
  return useQuery({
    queryKey: ['courses', id],
    queryFn: () => api.courses.getById(id),
    enabled: !!id,
  })
}

export const useEnrollCourse = () => {
  const queryClient = useQueryClient()
  
  return useMutation({
    mutationFn: (courseId: string) => api.courses.enroll(courseId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['courses'] })
      queryClient.invalidateQueries({ queryKey: ['dashboard'] })
    },
  })
}

export const useCourseProgress = (courseId: string) => {
  return useQuery({
    queryKey: ['courses', courseId, 'progress'],
    queryFn: () => api.courses.getProgress(courseId),
    enabled: !!courseId,
  })
}

// Assignment hooks
export const useAssignments = (params?: {
  status?: string
  course?: string
  page?: number
}) => {
  return useQuery({
    queryKey: ['assignments', params],
    queryFn: () => api.assignments.getAll(params),
    staleTime: 1 * 60 * 1000, // 1 minute
  })
}

export const useAssignment = (id: string) => {
  return useQuery({
    queryKey: ['assignments', id],
    queryFn: () => api.assignments.getById(id),
    enabled: !!id,
  })
}

export const useSubmitAssignment = () => {
  const queryClient = useQueryClient()
  
  return useMutation({
    mutationFn: ({ assignmentId, submission }: { 
      assignmentId: string
      submission: any 
    }) => api.assignments.submit(assignmentId, submission),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['assignments'] })
      queryClient.invalidateQueries({ queryKey: ['dashboard'] })
    },
  })
}

// Profile hooks
export const useProfile = () => {
  return useQuery({
    queryKey: ['profile'],
    queryFn: api.profile.get,
    staleTime: 5 * 60 * 1000, // 5 minutes
  })
}

export const useUpdateProfile = () => {
  const queryClient = useQueryClient()
  
  return useMutation({
    mutationFn: (profileData: any) => api.profile.update(profileData),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['profile'] })
      queryClient.invalidateQueries({ queryKey: ['auth'] })
    },
  })
}

export const useUploadAvatar = () => {
  const queryClient = useQueryClient()
  
  return useMutation({
    mutationFn: (file: File) => api.profile.uploadAvatar(file),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['profile'] })
    },
  })
}

// Notification hooks
export const useNotifications = (params?: {
  unread?: boolean
  page?: number
}) => {
  return useQuery({
    queryKey: ['notifications', params],
    queryFn: () => api.notifications.getAll(params),
    refetchInterval: 30 * 1000, // Refetch every 30 seconds
  })
}

export const useMarkNotificationAsRead = () => {
  const queryClient = useQueryClient()
  
  return useMutation({
    mutationFn: (id: string) => api.notifications.markAsRead(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['notifications'] })
    },
  })
}

export const useMarkAllNotificationsAsRead = () => {
  const queryClient = useQueryClient()
  
  return useMutation({
    mutationFn: api.notifications.markAllAsRead,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['notifications'] })
    },
  })
}

// AI Assistant hooks
export const useAskAssistant = () => {
  return useMutation({
    mutationFn: ({ question, context }: { 
      question: string
      context?: any 
    }) => api.assistant.ask(question, context),
  })
}

export const useAssistantHistory = (limit?: number) => {
  return useQuery({
    queryKey: ['assistant', 'history', limit],
    queryFn: () => api.assistant.getHistory(limit),
  })
}

// File upload hooks
export const useUploadFile = () => {
  return useMutation({
    mutationFn: ({ file, type }: { 
      file: File
      type: 'assignment' | 'profile' | 'content' 
    }) => api.files.upload(file, type),
  })
}

export const useDeleteFile = () => {
  const queryClient = useQueryClient()
  
  return useMutation({
    mutationFn: (fileId: string) => api.files.delete(fileId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['files'] })
    },
  })
}

// Dashboard hooks
export const useDashboardStats = () => {
  return useQuery({
    queryKey: ['dashboard', 'stats'],
    queryFn: api.dashboard.getStats,
    staleTime: 2 * 60 * 1000, // 2 minutes
  })
}

export const useRecentActivity = (limit?: number) => {
  return useQuery({
    queryKey: ['dashboard', 'activity', limit],
    queryFn: () => api.dashboard.getRecentActivity(limit),
    staleTime: 1 * 60 * 1000, // 1 minute
  })
}
