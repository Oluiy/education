// src/api/users.ts
import { User } from '@/contexts/AuthContext'

export interface UserStats {
  totalCourses: number
  completedCourses: number
  totalQuizzes: number
  averageScore: number
  studyTime: number
  streak: number
}

export interface Activity {
  id: string
  type: 'course_enrollment' | 'quiz_completed' | 'lesson_completed' | 'assignment_submitted'
  title: string
  description: string
  timestamp: string
  metadata?: Record<string, any>
}

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

export async function getUsers(params?: {
  role?: string
  search?: string
  schoolId?: string
  page?: number
  limit?: number
}): Promise<{ users: User[]; total: number; page: number; limit: number }> {
  const token = localStorage.getItem('auth_token')
  const searchParams = new URLSearchParams()
  
  if (params) {
    Object.entries(params).forEach(([key, value]) => {
      if (value !== undefined) searchParams.append(key, value.toString())
    })
  }

  const response = await fetch(`${API_URL}/users?${searchParams}`, {
    headers: { 'Authorization': `Bearer ${token}` }
  })
  if (!response.ok) throw new Error('Failed to fetch users')
  return response.json()
}

export async function getUser(id: string): Promise<User> {
  const token = localStorage.getItem('auth_token')
  const response = await fetch(`${API_URL}/users/${id}`, {
    headers: { 'Authorization': `Bearer ${token}` }
  })
  if (!response.ok) throw new Error('Failed to fetch user')
  return response.json()
}

export async function updateUser(id: string, data: Partial<User>): Promise<User> {
  const token = localStorage.getItem('auth_token')
  const response = await fetch(`${API_URL}/users/${id}`, {
    method: 'PUT',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`
    },
    body: JSON.stringify(data)
  })
  if (!response.ok) throw new Error('Failed to update user')
  return response.json()
}

export async function deleteUser(id: string): Promise<void> {
  const token = localStorage.getItem('auth_token')
  const response = await fetch(`${API_URL}/users/${id}`, {
    method: 'DELETE',
    headers: { 'Authorization': `Bearer ${token}` }
  })
  if (!response.ok) throw new Error('Failed to delete user')
}

export async function getUserStats(userId?: string): Promise<UserStats> {
  const token = localStorage.getItem('auth_token')
  const url = userId ? `${API_URL}/users/${userId}/stats` : `${API_URL}/users/me/stats`
  const response = await fetch(url, {
    headers: { 'Authorization': `Bearer ${token}` }
  })
  if (!response.ok) throw new Error('Failed to fetch user stats')
  return response.json()
}

export async function getUserActivity(userId?: string, limit = 10): Promise<Activity[]> {
  const token = localStorage.getItem('auth_token')
  const url = userId 
    ? `${API_URL}/users/${userId}/activity?limit=${limit}` 
    : `${API_URL}/users/me/activity?limit=${limit}`
  const response = await fetch(url, {
    headers: { 'Authorization': `Bearer ${token}` }
  })
  if (!response.ok) throw new Error('Failed to fetch user activity')
  return response.json()
}

export async function inviteUser(data: {
  email: string
  role: string
  schoolId?: string
}): Promise<void> {
  const token = localStorage.getItem('auth_token')
  const response = await fetch(`${API_URL}/users/invite`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`
    },
    body: JSON.stringify(data)
  })
  if (!response.ok) throw new Error('Failed to invite user')
}

export async function createUser(data: Partial<User>): Promise<User> {
  const token = localStorage.getItem('auth_token')
  const response = await fetch(`${API_URL}/users`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`
    },
    body: JSON.stringify(data)
  })
  if (!response.ok) throw new Error('Failed to create user')
  return response.json()
}
