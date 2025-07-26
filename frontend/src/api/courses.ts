// src/api/courses.ts
export interface Course {
  id: string
  title: string
  description: string
  instructor: {
    id: string
    name: string
    avatar?: string
  }
  thumbnail: string
  duration: number
  difficulty: 'beginner' | 'intermediate' | 'advanced'
  category: string
  tags: string[]
  enrollmentCount: number
  rating: number
  reviewCount: number
  price: number
  currency: string
  isPublished: boolean
  createdAt: string
  updatedAt: string
  modules: CourseModule[]
}

export interface CourseModule {
  id: string
  title: string
  description: string
  order: number
  lessons: Lesson[]
}

export interface Lesson {
  id: string
  title: string
  description: string
  type: 'video' | 'text' | 'quiz' | 'assignment'
  duration: number
  order: number
  content: string
  videoUrl?: string
  attachments?: string[]
}

export interface Enrollment {
  id: string
  courseId: string
  userId: string
  enrolledAt: string
  progress: number
  completedLessons: string[]
  lastAccessedAt: string
}

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

export async function getCourses(params?: {
  category?: string
  search?: string
  difficulty?: string
  page?: number
  limit?: number
}): Promise<{ courses: Course[]; total: number; page: number; limit: number }> {
  const token = localStorage.getItem('auth_token')
  const searchParams = new URLSearchParams()
  
  if (params) {
    Object.entries(params).forEach(([key, value]) => {
      if (value !== undefined) searchParams.append(key, value.toString())
    })
  }

  const response = await fetch(`${API_URL}/courses?${searchParams}`, {
    headers: { 'Authorization': `Bearer ${token}` }
  })
  if (!response.ok) throw new Error('Failed to fetch courses')
  return response.json()
}

export async function getCourse(id: string): Promise<Course> {
  const token = localStorage.getItem('auth_token')
  const response = await fetch(`${API_URL}/courses/${id}`, {
    headers: { 'Authorization': `Bearer ${token}` }
  })
  if (!response.ok) throw new Error('Failed to fetch course')
  return response.json()
}

export async function createCourse(data: Partial<Course>): Promise<Course> {
  const token = localStorage.getItem('auth_token')
  const response = await fetch(`${API_URL}/courses`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`
    },
    body: JSON.stringify(data)
  })
  if (!response.ok) throw new Error('Failed to create course')
  return response.json()
}

export async function updateCourse(id: string, data: Partial<Course>): Promise<Course> {
  const token = localStorage.getItem('auth_token')
  const response = await fetch(`${API_URL}/courses/${id}`, {
    method: 'PUT',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`
    },
    body: JSON.stringify(data)
  })
  if (!response.ok) throw new Error('Failed to update course')
  return response.json()
}

export async function deleteCourse(id: string): Promise<void> {
  const token = localStorage.getItem('auth_token')
  const response = await fetch(`${API_URL}/courses/${id}`, {
    method: 'DELETE',
    headers: { 'Authorization': `Bearer ${token}` }
  })
  if (!response.ok) throw new Error('Failed to delete course')
}

export async function enrollInCourse(courseId: string): Promise<Enrollment> {
  const token = localStorage.getItem('auth_token')
  const response = await fetch(`${API_URL}/courses/${courseId}/enroll`, {
    method: 'POST',
    headers: { 'Authorization': `Bearer ${token}` }
  })
  if (!response.ok) throw new Error('Failed to enroll in course')
  return response.json()
}

export async function unenrollFromCourse(courseId: string): Promise<void> {
  const token = localStorage.getItem('auth_token')
  const response = await fetch(`${API_URL}/courses/${courseId}/unenroll`, {
    method: 'DELETE',
    headers: { 'Authorization': `Bearer ${token}` }
  })
  if (!response.ok) throw new Error('Failed to unenroll from course')
}

export async function getUserEnrollments(): Promise<Enrollment[]> {
  const token = localStorage.getItem('auth_token')
  const response = await fetch(`${API_URL}/enrollments`, {
    headers: { 'Authorization': `Bearer ${token}` }
  })
  if (!response.ok) throw new Error('Failed to fetch enrollments')
  return response.json()
}

export async function updateProgress(courseId: string, lessonId: string): Promise<Enrollment> {
  const token = localStorage.getItem('auth_token')
  const response = await fetch(`${API_URL}/courses/${courseId}/progress`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`
    },
    body: JSON.stringify({ lessonId })
  })
  if (!response.ok) throw new Error('Failed to update progress')
  return response.json()
}
