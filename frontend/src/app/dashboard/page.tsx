'use client'

import { useAuth } from '@/contexts/AuthContext'
import { StudentDashboard, TeacherDashboard, AdminDashboard } from '@/components/RoleDashboards'
import { LoadingPage } from '@/components/ui/Loading'

export default function DashboardPage() {
  const { user, isLoading } = useAuth()

  if (isLoading) {
    return <LoadingPage />
  }

  if (!user) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <h1 className="text-xl font-semibold text-gray-900 mb-2">Access Denied</h1>
          <p className="text-gray-600">Please log in to access the dashboard</p>
        </div>
      </div>
    )
  }

  // Render role-specific dashboard
  switch (user.role) {
    case 'student':
      return <StudentDashboard />
    case 'teacher':
      return <TeacherDashboard />
    case 'admin':
      return <AdminDashboard />
    default:
      return (
        <div className="min-h-screen bg-gray-50 flex items-center justify-center">
          <div className="text-center">
            <h1 className="text-xl font-semibold text-gray-900 mb-2">Invalid Role</h1>
            <p className="text-gray-600">Your user role is not recognized</p>
          </div>
        </div>
      )
  }
}
