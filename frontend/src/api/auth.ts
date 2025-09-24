// src/api/auth.ts
import { User } from '@/contexts/AuthContext'

// Normalize base URL (strip trailing slash)
const rawBase = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
const API_URL = rawBase.replace(/\/$/, '')

export type { User }

// Backend token response shape
interface BackendTokenResponse {
  access_token: string
  refresh_token: string
  token_type: string
  expires_in: number
  user: BackendUser
}

interface BackendUser {
  id: number
  username: string
  email: string
  full_name: string
  role: string
  is_active: boolean
  is_verified: boolean
  created_at: string
  last_login: string | null
}

function mapUser(u: BackendUser): User {
  return {
    id: String(u.id),
    email: u.email,
    name: u.full_name,
    role: (u.role as User['role']),
    createdAt: u.created_at,
    isEmailVerified: u.is_verified
  }
}

async function parseError(res: Response, fallback: string) {
  try {
    const data = await res.json()
    if (data?.detail) {
      if (Array.isArray(data.detail)) {
        return data.detail.map((d: any) => d.msg || d.detail).join('; ')
      }
      return data.detail
    }
    return fallback
  } catch {
    return fallback
  }
}

export async function login(usernameOrEmail: string, password: string): Promise<{ user: User; token: string }> {
  const response = await fetch(`${API_URL}/auth/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ username_or_email: usernameOrEmail, password, remember_me: false })
  })
  if (!response.ok) {
    throw new Error(await parseError(response, 'Login failed'))
  }
  const data: BackendTokenResponse = await response.json()
  return { user: mapUser(data.user), token: data.access_token }
}

// signup: map UI form fields to backend register schema, then auto-login to fetch tokens
export async function signup(formData: any): Promise<{ user: User; token: string }> {
  const email: string = formData.email
  const first: string = formData.firstName || ''
  const last: string = formData.lastName || ''
  const fullName = `${first} ${last}`.trim() || email.split('@')[0]
  // Derive username from email local part (sanitize)
  const emailLocal = (email || '').split('@')[0].toLowerCase()
  let username = (formData.username || emailLocal).replace(/[^a-zA-Z0-9_.-]/g, '')
  if (username.length < 3) username = (emailLocal + '123').slice(0, 12)

  const payload = {
    username,
    email,
    password: formData.password,
    full_name: fullName,
    role: formData.accountType || 'student'
  }

  // Basic guard
  if (!payload.email || !payload.password || !payload.full_name) {
    throw new Error('Missing required signup fields')
  }

  const regRes = await fetch(`${API_URL}/auth/register`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  })
  if (!regRes.ok) {
    throw new Error(await parseError(regRes, 'Signup failed'))
  }

  // Auto-login using email (backend accepts username or email) to obtain tokens
  return login(email, payload.password)
}

export async function getSession(token: string): Promise<User> {
  const response = await fetch(`${API_URL}/auth/me`, {
    headers: { 'Authorization': `Bearer ${token}` }
  })
  if (!response.ok) throw new Error(await parseError(response, 'Session check failed'))
  const data: BackendUser = await response.json()
  return mapUser(data)
}

export async function logout(): Promise<void> {
  const token = typeof window !== 'undefined' ? localStorage.getItem('auth_token') : null
  if (!token) return
  await fetch(`${API_URL}/auth/logout`, {
    method: 'POST',
    headers: { 'Authorization': `Bearer ${token}` }
  })
}

export async function changePassword(data: { currentPassword: string; newPassword: string }): Promise<void> {
  const token = localStorage.getItem('auth_token')
  const response = await fetch(`${API_URL}/auth/change-password`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`
    },
    body: JSON.stringify(data)
  })
  if (!response.ok) throw new Error('Failed to change password')
}

export async function deleteAccount(userId: string): Promise<void> {
  const token = localStorage.getItem('auth_token')
  const response = await fetch(`${API_URL}/auth/delete-account/${userId}`, {
    method: 'DELETE',
    headers: { 'Authorization': `Bearer ${token}` }
  })
  if (!response.ok) throw new Error('Failed to delete account')
}
