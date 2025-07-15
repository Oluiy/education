// API configuration and utilities for microservices
const API_GATEWAY_URL = process.env.NEXT_PUBLIC_API_GATEWAY_URL || 'http://localhost:8000'

const API_URLS = {
  AUTH: `${API_GATEWAY_URL}/api/v1/auth`,
  CONTENT: `${API_GATEWAY_URL}/api/v1/content`,
  QUIZZES: `${API_GATEWAY_URL}/api/v1/quizzes`,
  ASSISTANT: `${API_GATEWAY_URL}/api/v1/assistant`,
  ADMIN: `${API_GATEWAY_URL}/api/v1/admin`,
  SYNC: `${API_GATEWAY_URL}/api/v1/sync`,
  MESSAGES: `${API_GATEWAY_URL}/api/v1/messages`,
  FILES: `${API_GATEWAY_URL}/api/v1/files`,
  UPLOAD: `${API_GATEWAY_URL}/api/v1/upload`,
  NOTIFICATIONS: `${API_GATEWAY_URL}/api/v1/notifications`,
}

// Auth token management
export const getAuthToken = (): string | null => {
  if (typeof window !== 'undefined') {
    return localStorage.getItem('auth_token')
  }
  return null
}

export const setAuthToken = (token: string): void => {
  if (typeof window !== 'undefined') {
    localStorage.setItem('auth_token', token)
  }
}

export const removeAuthToken = (): void => {
  if (typeof window !== 'undefined') {
    localStorage.removeItem('auth_token')
  }
}

// API request wrapper with authentication
export const apiRequest = async (
  service: keyof typeof API_URLS,
  endpoint: string,
  options: RequestInit = {}
): Promise<Response> => {
  const token = getAuthToken()
  
  const defaultHeaders: Record<string, string> = {
    'Content-Type': 'application/json',
  }
  
  if (token) {
    defaultHeaders.Authorization = `Bearer ${token}`
  }

  const config: RequestInit = {
    ...options,
    headers: {
      ...defaultHeaders,
      ...options.headers,
    },
  }

  const response = await fetch(`${API_URLS[service]}${endpoint}`, config)
  
  // Handle unauthorized responses
  if (response.status === 401) {
    removeAuthToken()
    // Redirect to login page
    if (typeof window !== 'undefined') {
      window.location.href = '/login'
    }
  }
  
  return response
}

// API methods
export const api = {
  // Auth endpoints
  auth: {
    login: async (email: string, password: string) => {
      const response = await apiRequest('AUTH', '/auth/login', {
        method: 'POST',
        body: JSON.stringify({ email, password }),
      })
      return response.json()
    },
    
    register: async (userData: any) => {
      const response = await apiRequest('AUTH', '/auth/register', {
        method: 'POST',
        body: JSON.stringify(userData),
      })
      return response.json()
    },
    
    me: async () => {
      const response = await apiRequest('AUTH', '/auth/me')
      return response.json()
    },
    
    logout: async () => {
      const response = await apiRequest('AUTH', '/auth/logout', {
        method: 'POST',
      })
      return response.json()
    },
  },

  // Course endpoints
  courses: {
    getAll: async (params?: { search?: string; category?: string; page?: number }) => {
      const searchParams = new URLSearchParams()
      if (params?.search) searchParams.append('search', params.search)
      if (params?.category) searchParams.append('category', params.category)
      if (params?.page) searchParams.append('page', params.page.toString())
      
      const response = await apiRequest('CONTENT', `/courses?${searchParams.toString()}`)
      return response.json()
    },
    
    getById: async (id: string) => {
      const response = await apiRequest('CONTENT', `/courses/${id}`)
      return response.json()
    },
    
    enroll: async (courseId: string) => {
      const response = await apiRequest('CONTENT', `/courses/${courseId}/enroll`, {
        method: 'POST',
      })
      return response.json()
    },
    
    getProgress: async (courseId: string) => {
      const response = await apiRequest('CONTENT', `/courses/${courseId}/progress`)
      return response.json()
    },
  },

  // Assignment endpoints
  assignments: {
    getAll: async (params?: { status?: string; course?: string; page?: number }) => {
      const searchParams = new URLSearchParams()
      if (params?.status) searchParams.append('status', params.status)
      if (params?.course) searchParams.append('course', params.course)
      if (params?.page) searchParams.append('page', params.page.toString())
      
      const response = await apiRequest('CONTENT', `/assignments?${searchParams.toString()}`)
      return response.json()
    },
    
    getById: async (id: string) => {
      const response = await apiRequest('CONTENT', `/assignments/${id}`)
      return response.json()
    },
    
    submit: async (assignmentId: string, submission: any) => {
      const response = await apiRequest('CONTENT', `/assignments/${assignmentId}/submit`, {
        method: 'POST',
        body: JSON.stringify(submission),
      })
      return response.json()
    },
  },

  // User profile endpoints
  profile: {
    get: async () => {
      const response = await apiRequest('AUTH', '/profile')
      return response.json()
    },
    
    update: async (profileData: any) => {
      const response = await apiRequest('AUTH', '/profile', {
        method: 'PUT',
        body: JSON.stringify(profileData),
      })
      return response.json()
    },
    
    uploadAvatar: async (file: File) => {
      const formData = new FormData()
      formData.append('avatar', file)
      
      const response = await apiRequest('FILES', '/profile/avatar', {
        method: 'POST',
        body: formData,
        headers: {}, // Let browser set content-type for FormData
      })
      return response.json()
    },
  },

  // Notification endpoints
  notifications: {
    getAll: async (params?: { unread?: boolean; page?: number }) => {
      const searchParams = new URLSearchParams()
      if (params?.unread) searchParams.append('unread', 'true')
      if (params?.page) searchParams.append('page', params.page.toString())
      
      const response = await apiRequest('NOTIFICATIONS', `/notifications?${searchParams.toString()}`)
      return response.json()
    },
    
    markAsRead: async (id: string) => {
      const response = await apiRequest('NOTIFICATIONS', `/notifications/${id}/read`, {
        method: 'PUT',
      })
      return response.json()
    },
    
    markAllAsRead: async () => {
      const response = await apiRequest('NOTIFICATIONS', '/notifications/read-all', {
        method: 'PUT',
      })
      return response.json()
    },
  },

  // AI Assistant endpoints
  assistant: {
    ask: async (question: string, context?: any) => {
      const response = await apiRequest('ASSISTANT', '/assistant/ask', {
        method: 'POST',
        body: JSON.stringify({ question, context }),
      })
      return response.json()
    },
    
    getHistory: async (limit?: number) => {
      const searchParams = new URLSearchParams()
      if (limit) searchParams.append('limit', limit.toString())
      
      const response = await apiRequest('ASSISTANT', `/assistant/history?${searchParams.toString()}`)
      return response.json()
    },
  },

  // File upload endpoints
  files: {
    upload: async (file: File, type: 'assignment' | 'profile' | 'content') => {
      const formData = new FormData()
      formData.append('file', file)
      formData.append('type', type)
      
      const response = await apiRequest('FILES', '/files/upload', {
        method: 'POST',
        body: formData,
        headers: {}, // Let browser set content-type for FormData
      })
      return response.json()
    },
    
    delete: async (fileId: string) => {
      const response = await apiRequest('FILES', `/files/${fileId}`, {
        method: 'DELETE',
      })
      return response.json()
    },
  },

  // Dashboard data
  dashboard: {
    getStats: async () => {
      const response = await apiRequest('CONTENT', '/dashboard/stats')
      return response.json()
    },
    
    getRecentActivity: async (limit?: number) => {
      const searchParams = new URLSearchParams()
      if (limit) searchParams.append('limit', limit.toString())
      
      const response = await apiRequest('CONTENT', `/dashboard/activity?${searchParams.toString()}`)
      return response.json()
    },
  },

  // Course Management API
  courseAPI: {
    // Get all courses
    getCourses: async (params?: { 
      page?: number; 
      limit?: number; 
      search?: string; 
      category?: string; 
      difficulty?: string;
      status?: string;
    }) => {
      try {
        const searchParams = new URLSearchParams()
        if (params?.page) searchParams.append('page', params.page.toString())
        if (params?.limit) searchParams.append('limit', params.limit.toString())
        if (params?.search) searchParams.append('search', params.search)
        if (params?.category) searchParams.append('category', params.category)
        if (params?.difficulty) searchParams.append('difficulty', params.difficulty)
        if (params?.status) searchParams.append('status', params.status)
        
        const response = await apiRequest('CONTENT', `/courses?${searchParams.toString()}`)
        return await response.json()
      } catch (error) {
        console.error('Error fetching courses:', error)
        throw error
      }
    },

    // Get single course
    getCourse: async (id: string) => {
      try {
        const response = await apiRequest('CONTENT', `/courses/${id}`)
        return await response.json()
      } catch (error) {
        console.error('Error fetching course:', error)
        throw error
      }
    },

    // Create new course
    createCourse: async (courseData: any) => {
      try {
        const response = await apiRequest('CONTENT', '/courses', {
          method: 'POST',
          body: JSON.stringify(courseData)
        })
        return await response.json()
      } catch (error) {
        console.error('Error creating course:', error)
        throw error
      }
    },

    // Update course
    updateCourse: async (id: string, courseData: any) => {
      try {
        const response = await apiRequest('CONTENT', `/courses/${id}`, {
          method: 'PUT',
          body: JSON.stringify(courseData)
        })
        return await response.json()
      } catch (error) {
        console.error('Error updating course:', error)
        throw error
      }
    },

    // Delete course
    deleteCourse: async (id: string) => {
      try {
        const response = await apiRequest('CONTENT', `/courses/${id}`, {
          method: 'DELETE'
        })
        return await response.json()
      } catch (error) {
        console.error('Error deleting course:', error)
        throw error
      }
    },

    // Enroll in course
    enrollInCourse: async (courseId: string) => {
      try {
        const response = await apiRequest('CONTENT', `/courses/${courseId}/enroll`, {
          method: 'POST'
        })
        return await response.json()
      } catch (error) {
        console.error('Error enrolling in course:', error)
        throw error
      }
    },

    // Get course progress
    getCourseProgress: async (courseId: string) => {
      try {
        const response = await apiRequest('CONTENT', `/courses/${courseId}/progress`)
        return await response.json()
      } catch (error) {
        console.error('Error fetching course progress:', error)
        throw error
      }
    }
  },

  // File Management API
  fileAPI: {
    // Upload file
    uploadFile: async (file: File, metadata?: { description?: string; tags?: string[] }) => {
      const formData = new FormData()
      formData.append('file', file)
      if (metadata?.description) {
        formData.append('description', metadata.description)
      }
      if (metadata?.tags) {
        formData.append('tags', JSON.stringify(metadata.tags))
      }
      
      const token = getAuthToken()
      const response = await fetch(`${API_URLS.FILES}/upload`, {
        method: 'POST',
        headers: {
          'Authorization': token ? `Bearer ${token}` : '',
        },
        body: formData,
      })
      
      if (!response.ok) {
        throw new Error(`Upload failed: ${response.statusText}`)
      }
      
      return response.json()
    },

    // Get files
    getFiles: async (params?: { 
      page?: number; 
      limit?: number; 
      search?: string; 
      file_type?: string;
      tags?: string[];
    }) => {
      const searchParams = new URLSearchParams()
      if (params?.page) searchParams.append('page', params.page.toString())
      if (params?.limit) searchParams.append('limit', params.limit.toString())
      if (params?.search) searchParams.append('search', params.search)
      if (params?.file_type) searchParams.append('file_type', params.file_type)
      if (params?.tags) searchParams.append('tags', params.tags.join(','))
      
      return apiRequest('FILES', `/files?${searchParams.toString()}`)
    },

    // Get file by ID
    getFile: async (fileId: string) => {
      return apiRequest('FILES', `/files/${fileId}`)
    },

    // Download file
    downloadFile: async (fileId: string) => {
      const token = getAuthToken()
      const response = await fetch(`${API_URLS.FILES}/files/${fileId}/download`, {
        headers: {
          'Authorization': token ? `Bearer ${token}` : '',
        },
      })
      
      if (!response.ok) {
        throw new Error(`Download failed: ${response.statusText}`)
      }
      
      return response.blob()
    },

    // Update file
    updateFile: async (fileId: string, data: { 
      filename?: string; 
      description?: string; 
      tags?: string[];
    }) => {
      return apiRequest('FILES', `/files/${fileId}`, {
        method: 'PUT',
        body: JSON.stringify(data),
      })
    },

    // Delete file
    deleteFile: async (fileId: string) => {
      return apiRequest('FILES', `/files/${fileId}`, {
        method: 'DELETE',
      })
    },

    // Share file
    shareFile: async (fileId: string, shareData: {
      shared_with_user_ids?: number[];
      shared_with_roles?: string[];
      access_level?: 'read' | 'write';
      expires_at?: string;
    }) => {
      return apiRequest('FILES', `/files/${fileId}/share`, {
        method: 'POST',
        body: JSON.stringify(shareData),
      })
    },

    // Get file shares
    getFileShares: async (fileId: string) => {
      return apiRequest('FILES', `/files/${fileId}/shares`)
    },

    // Create file collection
    createCollection: async (data: {
      name: string;
      description?: string;
      file_ids: string[];
    }) => {
      return apiRequest('FILES', '/collections', {
        method: 'POST',
        body: JSON.stringify(data),
      })
    },

    // Get collections
    getCollections: async () => {
      return apiRequest('FILES', '/collections')
    },

    // Get storage quota
    getStorageQuota: async () => {
      return apiRequest('FILES', '/storage/quota')
    },

    // Get file analytics
    getFileAnalytics: async (fileId: string) => {
      return apiRequest('FILES', `/files/${fileId}/analytics`)
    },
  },
}

export default api
