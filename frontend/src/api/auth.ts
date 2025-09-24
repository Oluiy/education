// src/api/auth.ts
import { User as FrontendUser } from '@/contexts/AuthContext'

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/'

// Backend response shapes (from auth-service)
type BackendUserResponse = {
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

type BackendTokenResponse = {
  access_token: string
  refresh_token: string
  token_type: string
  expires_in: number
  user: BackendUserResponse
}

// Map backend user to frontend user shape
function toFrontendUser(u: BackendUserResponse): FrontendUser {
  return {
    id: String(u.id),
    email: u.email,
    name: u.full_name,
    role: (u.role as FrontendUser['role']),
    createdAt: u.created_at,
    isEmailVerified: u.is_verified,
  }
}

export type { FrontendUser as User }

export async function login(emailOrUsername: string, password: string): Promise<{ user: FrontendUser; token: string }> {
  const response = await fetch(`${API_URL}/auth/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ username_or_email: emailOrUsername, password, remember_me: false })
  })
  if (!response.ok) throw new Error('Login failed')
  const data: BackendTokenResponse = await response.json()
  return { user: toFrontendUser(data.user), token: data.access_token }
}

// Accepts the signup page's formData, maps to backend register payload, then logs in to get a token
export async function signup(formData: any): Promise<{ user: FrontendUser; token: string }> {
  // Derive a safe username if not provided
  const emailLocal = (formData.email ? String(formData.email).split('@')[0] : '').toLowerCase()
  let derivedUsername = (formData.username || emailLocal).replace(/[^a-z0-9_\.\-]/gi, '')
  if (derivedUsername.length < 3) {
    derivedUsername = `${emailLocal}123`.slice(0, 12) || 'user123'
  }
  const fullNameRaw = `${formData.firstName ?? ''} ${formData.lastName ?? ''}`.trim()
  const fullName = fullNameRaw || (formData.email || '').split('@')[0]

  const registerPayload = {
    username: derivedUsername,
    email: formData.email,
    password: formData.password,
    full_name: fullName,
    role: formData.accountType || 'student',
  }

  // Basic validation to avoid 422s from backend
  if (!registerPayload.username || !registerPayload.email || !registerPayload.password || !registerPayload.full_name) {
    throw new Error('Missing required signup fields')
  }

  const regRes = await fetch(`${API_URL}/auth/register`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(registerPayload)
  })
  if (!regRes.ok) {
    const msg = await safeError(regRes, 'Signup failed')
    throw new Error(msg)
  }

  // Auto-login to obtain token
  return login(registerPayload.email, registerPayload.password)
}

export async function getSession(token: string): Promise<FrontendUser> {
  const response = await fetch(`${API_URL}/auth/me`, {
    headers: { 'Authorization': `Bearer ${token}` }
  })
  if (!response.ok) throw new Error('Session check failed')
  const data: BackendUserResponse = await response.json()
  return toFrontendUser(data)
}

export async function logout(): Promise<void> {
  const token = typeof window !== 'undefined' ? localStorage.getItem('auth_token') : null
  if (!token) return
  await fetch(`${API_URL}/auth/logout`, {
    method: 'POST',
    headers: { 'Authorization': `Bearer ${token}` }
  })
}

async function safeError(res: Response, fallback: string): Promise<string> {
  try {
    const data = await res.json()
    return data?.detail || fallback
  } catch {
    return fallback
  }
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
