import { User } from '@/contexts/AuthContext'

export interface AuthState {
  user: User | null
  token: string | null
  isAuthenticated: boolean
  isLoading: boolean
  error: string | null
}

export interface LoginRequest {
  email: string
  password: string
  rememberMe?: boolean
}

export interface RegisterRequest {
  email: string
  password: string
  firstName: string
  lastName: string
  role: 'student' | 'teacher' | 'admin'
  confirmPassword: string
}

export interface LoginResponse {
  user: User
  token: string
  refreshToken: string
  expiresIn: number
}

export interface RefreshTokenRequest {
  refreshToken: string
}

export interface ForgotPasswordRequest {
  email: string
}

export interface ResetPasswordRequest {
  token: string
  newPassword: string
  confirmPassword: string
}

export interface VerifyEmailRequest {
  token: string
}

export interface ChangePasswordRequest {
  currentPassword: string
  newPassword: string
  confirmPassword: string
}

export interface AuthError {
  code: string
  message: string
  field?: string
}

// Re-export User and UserRole from user types
export type { User, UserRole } from './user'
