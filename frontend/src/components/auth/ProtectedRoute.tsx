'use client'

import { useAuth } from '@/contexts/AuthContext'
import { useRouter } from 'next/navigation'
import { useEffect } from 'react'
import { LoadingPage } from '@/components/ui/Loading'

interface ProtectedRouteProps {
  children: React.ReactNode
  allowedRoles?: ('student' | 'teacher' | 'admin' | 'parent')[]
  requiredPermissions?: string[]
  fallbackPath?: string
}

export function ProtectedRoute({ 
  children, 
  allowedRoles, 
  requiredPermissions,
  fallbackPath = '/login' 
}: ProtectedRouteProps) {
  const { user, isLoading, hasPermission } = useAuth()
  const router = useRouter()

  useEffect(() => {
    if (!isLoading) {
      // Not authenticated
      if (!user) {
        router.push(fallbackPath)
        return
      }

      // Check role permissions
      if (allowedRoles && !allowedRoles.includes(user.role)) {
        router.push('/unauthorized')
        return
      }

      // Check specific permissions
      if (requiredPermissions && !requiredPermissions.every(permission => hasPermission(permission))) {
        router.push('/unauthorized')
        return
      }
    }
  }, [user, isLoading, allowedRoles, requiredPermissions, hasPermission, router, fallbackPath])

  if (isLoading) {
    return <LoadingPage title="Authenticating..." />
  }

  if (!user) {
    return null
  }

  if (allowedRoles && !allowedRoles.includes(user.role)) {
    return null
  }

  if (requiredPermissions && !requiredPermissions.every(permission => hasPermission(permission))) {
    return null
  }

  return <>{children}</>
}

// Higher-order component for role-based access
export function withRoleAccess(
  WrappedComponent: React.ComponentType<any>,
  allowedRoles: ('student' | 'teacher' | 'admin' | 'parent')[]
) {
  return function RoleProtectedComponent(props: any) {
    return (
      <ProtectedRoute allowedRoles={allowedRoles}>
        <WrappedComponent {...props} />
      </ProtectedRoute>
    )
  }
}

// Specific role components
export const StudentOnly = ({ children }: { children: React.ReactNode }) => (
  <ProtectedRoute allowedRoles={['student']}>{children}</ProtectedRoute>
)

export const TeacherOnly = ({ children }: { children: React.ReactNode }) => (
  <ProtectedRoute allowedRoles={['teacher']}>{children}</ProtectedRoute>
)

export const AdminOnly = ({ children }: { children: React.ReactNode }) => (
  <ProtectedRoute allowedRoles={['admin']}>{children}</ProtectedRoute>
)

export const TeacherOrAdmin = ({ children }: { children: React.ReactNode }) => (
  <ProtectedRoute allowedRoles={['teacher', 'admin']}>{children}</ProtectedRoute>
)

export const ParentOnly = ({ children }: { children: React.ReactNode }) => (
  <ProtectedRoute allowedRoles={['parent']}>{children}</ProtectedRoute>
)
