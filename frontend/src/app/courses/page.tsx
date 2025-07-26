// src/app/courses/page.tsx
'use client'

import { motion } from 'framer-motion'
import { CourseList } from '@/components/courses/CourseList'
import { useAuth } from '@/contexts/AuthContext'
import { withRoleAccess } from '@/components/RoleDashboards'
import {
  BookOpenIcon,
  AcademicCapIcon,
  SparklesIcon
} from '@heroicons/react/24/outline'

function CoursesPageContent() {
  const { user } = useAuth()

  return (
    <div className="space-y-8">
      {/* Hero Section */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="bg-gradient-to-r from-primary-600 to-secondary-600 rounded-2xl p-8 text-white"
      >
        <div className="max-w-3xl">
          <h1 className="text-3xl font-bold mb-4">
            Discover Amazing Courses
          </h1>
          <p className="text-primary-100 text-lg mb-6">
            Expand your knowledge with our comprehensive collection of courses taught by expert instructors.
          </p>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="flex items-center space-x-3">
              <BookOpenIcon className="w-8 h-8 text-primary-200" />
              <div>
                <p className="font-semibold">Expert-Led</p>
                <p className="text-primary-100 text-sm">Learn from industry professionals</p>
              </div>
            </div>
            <div className="flex items-center space-x-3">
              <AcademicCapIcon className="w-8 h-8 text-primary-200" />
              <div>
                <p className="font-semibold">Certified</p>
                <p className="text-primary-100 text-sm">Earn completion certificates</p>
              </div>
            </div>
            <div className="flex items-center space-x-3">
              <SparklesIcon className="w-8 h-8 text-primary-200" />
              <div>
                <p className="font-semibold">Interactive</p>
                <p className="text-primary-100 text-sm">Engaging learning experience</p>
              </div>
            </div>
          </div>
        </div>
      </motion.div>

      {/* Course List */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2 }}
      >
        <CourseList />
      </motion.div>
    </div>
  )
}

// Export protected version for students, or open version for others
export default function CoursesPage() {
  return <CoursesPageContent />
}
