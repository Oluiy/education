'use client'

import { useState } from 'react'
import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { useAuth } from '@/contexts/AuthContext'
import { ProtectedRoute } from '@/components/auth/ProtectedRoute'
import {
  HomeIcon,
  BookOpenIcon,
  AcademicCapIcon,
  ChatBubbleLeftRightIcon,
  ChartBarIcon,
  CogIcon,
  Bars3Icon,
  XMarkIcon,
  BellIcon,
  UserCircleIcon,
  MagnifyingGlassIcon,
  ChevronLeftIcon,
  ChevronRightIcon,
  UsersIcon,
  ClipboardDocumentListIcon,
  PresentationChartBarIcon,
  ArrowRightOnRectangleIcon
} from '@heroicons/react/24/outline'

// Role-based navigation items
const getNavigationItems = (userRole: string) => {
  const baseItems = [
    { name: 'Dashboard', href: '/dashboard', icon: HomeIcon, roles: ['student', 'teacher', 'admin'] },
  ]

  const studentItems = [
    { name: 'My Courses', href: '/dashboard/courses', icon: BookOpenIcon, roles: ['student'] },
    { name: 'Assignments', href: '/dashboard/assignments', icon: AcademicCapIcon, roles: ['student'] },
    { name: 'Quizzes', href: '/dashboard/quizzes', icon: ClipboardDocumentListIcon, roles: ['student'] },
    { name: 'Progress', href: '/dashboard/progress', icon: ChartBarIcon, roles: ['student'] },
    { name: 'Messages', href: '/dashboard/messages', icon: ChatBubbleLeftRightIcon, roles: ['student'] },
  ]

  const teacherItems = [
    { name: 'My Courses', href: '/dashboard/courses', icon: BookOpenIcon, roles: ['teacher'] },
    { name: 'Students', href: '/dashboard/students', icon: UsersIcon, roles: ['teacher'] },
    { name: 'Assignments', href: '/dashboard/assignments', icon: AcademicCapIcon, roles: ['teacher'] },
    { name: 'Quizzes', href: '/dashboard/quizzes', icon: ClipboardDocumentListIcon, roles: ['teacher'] },
    { name: 'Analytics', href: '/dashboard/analytics', icon: PresentationChartBarIcon, roles: ['teacher'] },
    { name: 'Messages', href: '/dashboard/messages', icon: ChatBubbleLeftRightIcon, roles: ['teacher'] },
  ]

  const adminItems = [
    { name: 'Users', href: '/dashboard/users', icon: UsersIcon, roles: ['admin'] },
    { name: 'Courses', href: '/dashboard/courses', icon: BookOpenIcon, roles: ['admin'] },
    { name: 'Analytics', href: '/dashboard/analytics', icon: PresentationChartBarIcon, roles: ['admin'] },
    { name: 'Settings', href: '/dashboard/settings', icon: CogIcon, roles: ['admin'] },
  ]

  const allItems = [...baseItems, ...studentItems, ...teacherItems, ...adminItems]
  
  return allItems.filter(item => item.roles.includes(userRole))
}

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode
}) {
  const [sidebarOpen, setSidebarOpen] = useState(false)
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false)
  const pathname = usePathname()
  const { user, logout } = useAuth()

  const navigation = getNavigationItems(user?.role || 'student')

  const getUserInitials = (name: string) => {
    return name
      .split(' ')
      .map(part => part[0])
      .join('')
      .toUpperCase()
      .slice(0, 2)
  }

  return (
    <ProtectedRoute>
      <div className="min-h-screen bg-slate-50">
        {/* Mobile sidebar backdrop */}
        {sidebarOpen && (
          <div 
            className="fixed inset-0 bg-slate-600 bg-opacity-75 z-40 md:hidden"
            onClick={() => setSidebarOpen(false)}
          />
        )}

        {/* Mobile sidebar */}
        <div className={`fixed inset-y-0 left-0 z-50 w-64 bg-white shadow-xl transform transition-transform duration-300 ease-in-out md:hidden ${
          sidebarOpen ? 'translate-x-0' : '-translate-x-full'
        }`}>
          <div className="flex items-center justify-between h-16 px-6 border-b border-slate-200">
            <Link href="/dashboard" className="flex items-center space-x-3">
              <div className="w-8 h-8 bg-gradient-to-br from-slate-700 to-teal-600 rounded-lg flex items-center justify-center">
                <span className="text-white font-bold text-sm">EP</span>
              </div>
              <h1 className="text-lg font-semibold text-slate-900">EduPlatform</h1>
            </Link>
            <button
              onClick={() => setSidebarOpen(false)}
              className="text-slate-400 hover:text-slate-600 transition-colors"
            >
              <XMarkIcon className="w-6 h-6" />
            </button>
          </div>
        
          <nav className="flex-1 px-4 py-6 space-y-2 overflow-y-auto">
            {navigation.map((item) => {
              const isActive = pathname === item.href
              return (
                <Link
                  key={item.name}
                  href={item.href}
                  className={`flex items-center px-3 py-3 text-sm font-medium rounded-lg transition-colors duration-200 ${
                    isActive
                      ? 'bg-teal-50 text-teal-700 border-r-2 border-teal-600'
                      : 'text-slate-700 hover:bg-slate-100'
                  }`}
                  onClick={() => setSidebarOpen(false)}
                >
                  <item.icon className="w-5 h-5 mr-3 flex-shrink-0" />
                  {item.name}
                </Link>
              )
            })}
          </nav>

          {/* User info at bottom */}
          <div className="border-t border-slate-200 p-4">
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 bg-slate-200 rounded-full flex items-center justify-center">
                <span className="text-sm font-medium text-slate-600">
                  {user?.name ? getUserInitials(user.name) : 'U'}
                </span>
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium text-slate-900 truncate">{user?.name || 'User'}</p>
                <p className="text-xs text-slate-500 truncate capitalize">{user?.role || 'student'}</p>
              </div>
            </div>
            <button
              onClick={logout}
              className="mt-3 w-full flex items-center px-3 py-2 text-sm font-medium text-slate-700 hover:bg-slate-100 rounded-lg transition-colors"
            >
              <ArrowRightOnRectangleIcon className="w-5 h-5 mr-3" />
              Sign Out
            </button>
          </div>
        </div>

        {/* Desktop sidebar */}
        <div className={`hidden md:flex md:flex-col md:fixed md:inset-y-0 transition-all duration-300 ease-in-out ${
          sidebarCollapsed ? 'md:w-16' : 'md:w-64'
        }`}>
          <div className="flex-1 flex flex-col min-h-0 bg-white border-r border-slate-200">
            <div className="flex items-center justify-between h-16 px-4 border-b border-slate-200">
              {!sidebarCollapsed && (
                <Link href="/dashboard" className="flex items-center space-x-3">
                  <div className="w-8 h-8 bg-gradient-to-br from-slate-700 to-teal-600 rounded-lg flex items-center justify-center">
                    <span className="text-white font-bold text-sm">EP</span>
                  </div>
                  <span className="text-xl font-bold text-slate-900">EduPlatform</span>
                </Link>
              )}
              {sidebarCollapsed && (
                <div className="w-8 h-8 bg-gradient-to-br from-slate-700 to-teal-600 rounded-lg flex items-center justify-center mx-auto">
                  <span className="text-white font-bold text-sm">EP</span>
                </div>
              )}
              <button
                onClick={() => setSidebarCollapsed(!sidebarCollapsed)}
                className="p-1 text-slate-400 hover:text-slate-500"
              >
                {sidebarCollapsed ? (
                  <ChevronRightIcon className="w-4 h-4" />
                ) : (
                  <ChevronLeftIcon className="w-4 h-4" />
                )}
              </button>
            </div>
            
            <nav className="flex-1 px-4 py-6 space-y-2">
              {navigation.map((item) => {
                const isActive = pathname === item.href
                return (
                  <Link
                    key={item.name}
                    href={item.href}
                    className={`flex items-center px-3 py-2 text-sm font-medium rounded-lg transition-colors duration-200 group ${
                      isActive
                        ? 'bg-teal-50 text-teal-700 border-r-2 border-teal-600'
                        : 'text-slate-700 hover:bg-slate-100'
                    }`}
                    title={sidebarCollapsed ? item.name : undefined}
                  >
                    <item.icon className="w-5 h-5 flex-shrink-0" />
                    {!sidebarCollapsed && <span className="ml-3">{item.name}</span>}
                    {sidebarCollapsed && (
                      <div className="absolute left-16 bg-slate-900 text-white text-xs rounded py-1 px-2 opacity-0 group-hover:opacity-100 transition-opacity duration-200 pointer-events-none z-50">
                        {item.name}
                      </div>
                    )}
                  </Link>
                )
              })}
            </nav>

            {/* User info at bottom */}
            <div className="border-t border-slate-200 p-4">
              <div className="flex items-center space-x-3">
                <div className="w-10 h-10 bg-slate-200 rounded-full flex items-center justify-center flex-shrink-0">
                  <span className="text-sm font-medium text-slate-600">
                    {user?.name ? getUserInitials(user.name) : 'U'}
                  </span>
                </div>
                {!sidebarCollapsed && (
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium text-slate-900 truncate">{user?.name || 'User'}</p>
                    <p className="text-xs text-slate-500 truncate capitalize">{user?.role || 'student'}</p>
                  </div>
                )}
              </div>
              {!sidebarCollapsed && (
                <button
                  onClick={logout}
                  className="mt-3 w-full flex items-center px-3 py-2 text-sm font-medium text-slate-700 hover:bg-slate-100 rounded-lg transition-colors"
                >
                  <ArrowRightOnRectangleIcon className="w-5 h-5 mr-3" />
                  Sign Out
                </button>
              )}
            </div>
          </div>
        </div>

        {/* Main content */}
        <div className={`flex flex-col flex-1 transition-all duration-300 ease-in-out ${
          sidebarCollapsed ? 'md:pl-16' : 'md:pl-64'
        }`}>
          {/* Header */}
          <header className="bg-white border-b border-slate-200 px-4 sm:px-6 lg:px-8">
            <div className="flex items-center justify-between h-16">
              <div className="flex items-center space-x-4">
                {/* Mobile menu button */}
                <button
                  onClick={() => setSidebarOpen(true)}
                  className="md:hidden p-2 text-slate-400 hover:text-slate-500"
                >
                  <Bars3Icon className="w-6 h-6" />
                </button>
                
                {/* Search bar */}
                <div className="relative">
                  <MagnifyingGlassIcon className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
                  <input
                    type="text"
                    placeholder="Search courses, assignments..."
                    className="pl-10 pr-4 py-2 w-64 lg:w-96 border border-slate-300 rounded-lg focus:ring-2 focus:ring-teal-500 focus:border-transparent text-sm"
                  />
                </div>
              </div>

              <div className="flex items-center space-x-4">
                {/* Notification button */}
                <button className="relative p-2 text-slate-400 hover:text-slate-500">
                  <BellIcon className="w-6 h-6" />
                  <span className="absolute top-1 right-1 w-2 h-2 bg-red-500 rounded-full"></span>
                </button>

                {/* Profile */}
                <div className="flex items-center space-x-3">
                  <div className="w-8 h-8 bg-slate-200 rounded-full flex items-center justify-center">
                    <span className="text-xs font-medium text-slate-600">
                      {user?.name ? getUserInitials(user.name) : 'U'}
                    </span>
                  </div>
                  <div className="hidden sm:block">
                    <span className="text-sm font-medium text-slate-700">{user?.name || 'User'}</span>
                    <p className="text-xs text-slate-500 capitalize">{user?.role || 'student'}</p>
                  </div>
                </div>
              </div>
            </div>
          </header>

          {/* Main content area */}
          <main className="flex-1 bg-slate-50">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
              {children}
            </div>
          </main>
        </div>
      </div>
    </ProtectedRoute>
  )
}
