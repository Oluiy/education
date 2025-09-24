// src/api/auth.ts
import { User } from '@/contexts/AuthContext'

// Normalize base URL (strip trailing slash). We rely on build-time replacement of NEXT_PUBLIC_API_URL.
// If it's missing at build time in a production (non-localhost) environment, log a loud error to surface misconfiguration.
let rawBase = process.env.NEXT_PUBLIC_API_URL || ''
if (!rawBase) {
  // Build-time env missing.
  if (typeof window !== 'undefined') {
    const host = window.location.hostname
    if (host !== 'localhost' && host !== '127.0.0.1') {
      // Expose a global so user can inspect quickly in console.
      ;(window as any).__MISSING_NEXT_PUBLIC_API_URL__ = true
      console.error('[auth] NEXT_PUBLIC_API_URL was not defined at build time. Falling back to http://localhost:8000 which will NOT work in production. Set it in Vercel Project > Settings > Environment Variables and redeploy.')
    }
  }
  rawBase = 'http://localhost:8000'
}
const API_URL = rawBase.replace(/\/$/, '')
// Temporary debug: expose the resolved value (remove after verification)
if (typeof window !== 'undefined') {
  ;(window as any).__API_URL__ = API_URL
  if (process.env.NODE_ENV !== 'production') {
    // eslint-disable-next-line no-console
    console.log('[auth] Resolved API_URL =', API_URL)
  }
}

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
  // Debug instrumentation
  if (typeof window !== 'undefined') {
    // eslint-disable-next-line no-console
    console.log('[auth.login] using API_URL', API_URL)
  }
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
  if (typeof window !== 'undefined') {
    // eslint-disable-next-line no-console
    console.log('[auth.signup] starting signup with API_URL', API_URL)
  }
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
    if (typeof window !== 'undefined') {
      // eslint-disable-next-line no-console
      console.warn('[auth.signup] register failed status', regRes.status)
    }
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
