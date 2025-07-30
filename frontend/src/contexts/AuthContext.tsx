'use client'

import React, { createContext, useContext, useState, useEffect } from 'react'
import * as authAPI from '@/api/auth'
import * as profileAPI from '@/api/profile'

export interface User {
  id: string
  email: string
  name: string
  firstName?: string
  lastName?: string
  role: 'student' | 'teacher' | 'admin' | 'parent'
  avatar?: string
  schoolId?: string
  grade?: string
  subjects?: string[]
  permissions?: string[]
  bio?: string
  createdAt?: string
  isEmailVerified?: boolean
}

interface AuthContextType {
  user: User | null
  isLoading: boolean
  login: (email: string, password: string) => Promise<void>
  logout: () => void
  signup: (userData: any) => Promise<void>
  updateProfile: (data: Partial<User>) => Promise<void>
  hasPermission: (permission: string) => boolean
  isRole: (role: string) => boolean
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

export function useAuth() {
  const context = useContext(AuthContext)
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}

interface AuthProviderProps {
  children: React.ReactNode
}

export function AuthProvider({ children }: AuthProviderProps) {
  const [user, setUser] = useState<User | null>(null)
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    const checkAuth = async () => {
      try {
        const token = localStorage.getItem('auth_token')
        if (token) {
          const userData = await authAPI.getSession(token)
          setUser(userData)
        }
      } catch (error) {
        console.error('Auth check failed:', error)
        localStorage.removeItem('auth_token')
      } finally {
        setIsLoading(false)
      }
    }

    checkAuth()
  }, [])

  const login = async (email: string, password: string) => {
    try {
      const { user, token } = await authAPI.login(email, password)
      localStorage.setItem('auth_token', token)
      setUser(user)
    } catch (error) {
      throw error
    }
  }

  const signup = async (userData: any) => {
    try {
      const { user, token } = await authAPI.signup(userData)
      localStorage.setItem('auth_token', token)
      setUser(user)
    } catch (error) {
      throw error
    }
  }

  const logout = () => {
    authAPI.logout()
    localStorage.removeItem('auth_token')
    setUser(null)
  }

  const updateProfile = async (data: Partial<User>) => {
    try {
      const updatedUser = await profileAPI.updateProfile(data)
      setUser(updatedUser)
    } catch (error) {
      throw error
    }
  }

  const hasPermission = (permission: string): boolean => {
    if (!user?.permissions) return false
    return user.permissions.includes(permission)
  }

  const isRole = (role: string): boolean => {
    return user?.role === role
  }

  const value = {
    user,
    isLoading,
    login,
    logout,
    signup,
    updateProfile,
    hasPermission,
    isRole
  }

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  )
}
