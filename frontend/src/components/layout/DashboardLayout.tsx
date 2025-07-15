'use client'

import { useState, ReactNode } from 'react'
import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { motion, AnimatePresence } from 'framer-motion'
import {
  HomeIcon,
  BookOpenIcon,
  UserGroupIcon,
  ChatBubbleLeftRightIcon,
  ChartBarIcon,
  CogIcon,
  BellIcon,
  MagnifyingGlassIcon,
  Bars3Icon,
  XMarkIcon,
  ChevronDownIcon
} from '@heroicons/react/24/outline'

interface DashboardLayoutProps {
  children: ReactNode
  userType: 'student' | 'teacher' | 'parent' | 'admin'
}

export default function DashboardLayout({ children, userType = 'student' }: DashboardLayoutProps) {
  const [sidebarOpen, setSidebarOpen] = useState(false)
  const [profileDropdownOpen, setProfileDropdownOpen] = useState(false)
  const pathname = usePathname()

  // Navigation items based on user type
  const getNavigation = () => {
    const baseNav = [
      { name: 'Dashboard', href: '/dashboard', icon: HomeIcon },
    ]

    const userNavigation = {
      student: [
        ...baseNav,
        { name: 'My Courses', href: '/dashboard/courses', icon: BookOpenIcon },
        { name: 'Assignments', href: '/dashboard/assignments', icon: BookOpenIcon },
        { name: 'Messages', href: '/dashboard/messages', icon: ChatBubbleLeftRightIcon },
        { name: 'Progress', href: '/dashboard/progress', icon: ChartBarIcon },
      ],
      teacher: [
        ...baseNav,
        { name: 'My Classes', href: '/dashboard/classes', icon: UserGroupIcon },
        { name: 'Create Content', href: '/dashboard/create', icon: BookOpenIcon },
        { name: 'Messages', href: '/dashboard/messages', icon: ChatBubbleLeftRightIcon },
        { name: 'Analytics', href: '/dashboard/analytics', icon: ChartBarIcon },
      ],
      parent: [
        ...baseNav,
        { name: 'My Children', href: '/dashboard/children', icon: UserGroupIcon },
        { name: 'Messages', href: '/dashboard/messages', icon: ChatBubbleLeftRightIcon },
        { name: 'Reports', href: '/dashboard/reports', icon: ChartBarIcon },
      ],
      admin: [
        ...baseNav,
        { name: 'Schools', href: '/dashboard/schools', icon: UserGroupIcon },
        { name: 'Users', href: '/dashboard/users', icon: UserGroupIcon },
        { name: 'Content', href: '/dashboard/content', icon: BookOpenIcon },
        { name: 'Analytics', href: '/dashboard/analytics', icon: ChartBarIcon },
        { name: 'Settings', href: '/dashboard/settings', icon: CogIcon },
      ]
    }

    return userNavigation[userType] || baseNav
  }

  const navigation = getNavigation()

  const userInfo = {
    name: 'John Doe',
    email: 'john@example.com',
    avatar: '/api/placeholder/40/40',
    role: userType.charAt(0).toUpperCase() + userType.slice(1)
  }

  return (
    <div className="h-screen flex bg-gray-50">
      {/* Mobile sidebar overlay */}
      <AnimatePresence>
        {sidebarOpen && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 z-40 lg:hidden"
          >
            <div 
              className="absolute inset-0 bg-gray-600 opacity-75"
              onClick={() => setSidebarOpen(false)}
            />
          </motion.div>
        )}
      </AnimatePresence>

      {/* Sidebar */}
      <motion.div
        initial={false}
        animate={{
          x: sidebarOpen ? 0 : -256
        }}
        className="fixed inset-y-0 left-0 z-50 w-64 bg-white shadow-strong lg:translate-x-0 lg:static lg:inset-0"
      >
        <div className="flex items-center justify-between h-16 px-6 border-b border-gray-200">
          <Link href="/dashboard" className="flex items-center space-x-3">
            <div className="w-10 h-10 bg-gradient-to-br from-primary-500 to-secondary-500 rounded-xl flex items-center justify-center">
              <span className="text-white font-bold text-lg">EN</span>
            </div>
            <span className="text-xl font-heading font-bold text-gray-900">EduNerve</span>
          </Link>
          
          <button
            onClick={() => setSidebarOpen(false)}
            className="lg:hidden p-2 text-gray-400 hover:text-gray-500"
          >
            <XMarkIcon className="w-6 h-6" />
          </button>
        </div>

        <nav className="flex-1 px-4 py-6 space-y-2">
          {navigation.map((item) => {
            const isActive = pathname === item.href
            return (
              <Link
                key={item.name}
                href={item.href}
                className={`flex items-center px-4 py-3 text-sm font-medium rounded-lg transition-colors duration-200 ${
                  isActive
                    ? 'bg-primary-100 text-primary-900 border-r-2 border-primary-500'
                    : 'text-gray-700 hover:bg-gray-100'
                }`}
              >
                <item.icon className="w-5 h-5 mr-3" />
                {item.name}
              </Link>
            )
          })}
        </nav>

        {/* User info at bottom */}
        <div className="border-t border-gray-200 p-4">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 bg-gray-200 rounded-full flex items-center justify-center">
              <span className="text-sm font-medium text-gray-600">
                {userInfo.name.split(' ').map(n => n[0]).join('')}
              </span>
            </div>
            <div className="flex-1 min-w-0">
              <p className="text-sm font-medium text-gray-900 truncate">
                {userInfo.name}
              </p>
              <p className="text-xs text-gray-500 truncate">
                {userInfo.role}
              </p>
            </div>
          </div>
        </div>
      </motion.div>

      {/* Main content */}
      <div className="flex-1 flex flex-col overflow-hidden min-w-0">
        {/* Top header */}
        <header className="bg-white border-b border-gray-200 px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <button
                onClick={() => setSidebarOpen(true)}
                className="lg:hidden p-2 text-gray-400 hover:text-gray-500"
              >
                <Bars3Icon className="w-6 h-6" />
              </button>
              
              {/* Search */}
              <div className="relative hidden sm:block">
                <MagnifyingGlassIcon className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
                <input
                  type="text"
                  placeholder="Search..."
                  className="pl-10 pr-4 py-2 w-64 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                />
              </div>
            </div>

            <div className="flex items-center space-x-4">
              {/* Notifications */}
              <button className="relative p-2 text-gray-400 hover:text-gray-500">
                <BellIcon className="w-6 h-6" />
                <span className="absolute top-1 right-1 w-2 h-2 bg-red-500 rounded-full"></span>
              </button>

              {/* Profile dropdown */}
              <div className="relative">
                <button
                  onClick={() => setProfileDropdownOpen(!profileDropdownOpen)}
                  className="flex items-center space-x-3 p-2 text-sm rounded-lg hover:bg-gray-100"
                >
                  <div className="w-8 h-8 bg-gray-200 rounded-full flex items-center justify-center">
                    <span className="text-xs font-medium text-gray-600">
                      {userInfo.name.split(' ').map(n => n[0]).join('')}
                    </span>
                  </div>
                  <span className="hidden md:block font-medium text-gray-700">
                    {userInfo.name}
                  </span>
                  <ChevronDownIcon className="w-4 h-4 text-gray-400" />
                </button>

                <AnimatePresence>
                  {profileDropdownOpen && (
                    <motion.div
                      initial={{ opacity: 0, scale: 0.95 }}
                      animate={{ opacity: 1, scale: 1 }}
                      exit={{ opacity: 0, scale: 0.95 }}
                      className="absolute right-0 mt-2 w-48 bg-white rounded-lg shadow-strong border border-gray-200 py-1 z-10"
                    >
                      <Link
                        href="/dashboard/profile"
                        className="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                      >
                        Your Profile
                      </Link>
                      <Link
                        href="/dashboard/settings"
                        className="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                      >
                        Settings
                      </Link>
                      <hr className="my-1" />
                      <button
                        className="block w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                        onClick={() => {
                          // Handle sign out
                          console.log('Sign out')
                        }}
                      >
                        Sign out
                      </button>
                    </motion.div>
                  )}
                </AnimatePresence>
              </div>
            </div>
          </div>
        </header>

        {/* Page content */}
        <main className="flex-1 overflow-auto bg-gray-50">
          <div className="w-full h-full">
            {children}
          </div>
        </main>
      </div>
    </div>
  )
}
