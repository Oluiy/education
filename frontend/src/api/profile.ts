// src/api/profile.ts
import { User } from '@/contexts/AuthContext'

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

export async function updateProfile(data: Partial<User>): Promise<User> {
  const token = localStorage.getItem('auth_token')
  const response = await fetch(`${API_URL}/auth/profile`, {
    method: 'PUT',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`
    },
    body: JSON.stringify(data)
  })
  if (!response.ok) throw new Error('Profile update failed')
  return response.json()
}

export async function changePassword(currentPassword: string, newPassword: string): Promise<void> {
  const token = localStorage.getItem('auth_token')
  const response = await fetch(`${API_URL}/auth/change-password`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`
    },
    body: JSON.stringify({ currentPassword, newPassword })
  })
  if (!response.ok) throw new Error('Password change failed')
}

export async function requestPasswordReset(email: string): Promise<void> {
  const response = await fetch(`${API_URL}/auth/request-password-reset`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email })
  })
  if (!response.ok) throw new Error('Password reset request failed')
}

export async function resetPassword(token: string, newPassword: string): Promise<void> {
  const response = await fetch(`${API_URL}/auth/reset-password`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ token, newPassword })
  })
  if (!response.ok) throw new Error('Password reset failed')
}

export async function verifyEmail(token: string): Promise<void> {
  const response = await fetch(`${API_URL}/auth/verify-email`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ token })
  })
  if (!response.ok) throw new Error('Email verification failed')
}

// Additional methods needed by useApi hooks
export async function uploadAvatar(data: { userId: string; file: File }): Promise<User> {
  const token = localStorage.getItem('auth_token')
  const formData = new FormData()
  formData.append('avatar', data.file)
  
  const response = await fetch(`${API_URL}/users/${data.userId}/avatar`, {
    method: 'POST',
    headers: { 'Authorization': `Bearer ${token}` },
    body: formData
  })
  if (!response.ok) throw new Error('Failed to upload avatar')
  return response.json()
}

export async function getUserStats(userId: string): Promise<any> {
  const token = localStorage.getItem('auth_token')
  const response = await fetch(`${API_URL}/users/${userId}/stats`, {
    headers: { 'Authorization': `Bearer ${token}` }
  })
  if (!response.ok) throw new Error('Failed to fetch user stats')
  return response.json()
}

export async function getUserActivity(userId: string): Promise<any[]> {
  const token = localStorage.getItem('auth_token')
  const response = await fetch(`${API_URL}/users/${userId}/activity`, {
    headers: { 'Authorization': `Bearer ${token}` }
  })
  if (!response.ok) throw new Error('Failed to fetch user activity')
  return response.json()
}

export async function getUserCourses(userId: string): Promise<any[]> {
  const token = localStorage.getItem('auth_token')
  const response = await fetch(`${API_URL}/users/${userId}/courses`, {
    headers: { 'Authorization': `Bearer ${token}` }
  })
  if (!response.ok) throw new Error('Failed to fetch user courses')
  return response.json()
}

export async function getUserAchievements(userId: string): Promise<any[]> {
  const token = localStorage.getItem('auth_token')
  const response = await fetch(`${API_URL}/users/${userId}/achievements`, {
    headers: { 'Authorization': `Bearer ${token}` }
  })
  if (!response.ok) throw new Error('Failed to fetch user achievements')
  return response.json()
}
