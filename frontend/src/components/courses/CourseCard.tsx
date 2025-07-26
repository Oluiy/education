// src/components/courses/CourseCard.tsx
'use client'

import { motion } from 'framer-motion'
import Link from 'next/link'
import { Course } from '@/api/courses'
import { useEnrollInCourse } from '@/hooks/useApi'
import { useAuth } from '@/contexts/AuthContext'
import { useToast } from '@/contexts/ToastContext'
import {
  BookOpenIcon,
  ClockIcon,
  UserGroupIcon,
  StarIcon,
  PlayIcon,
  AcademicCapIcon
} from '@heroicons/react/24/outline'
import { StarIcon as StarSolidIcon } from '@heroicons/react/24/solid'

interface CourseCardProps {
  course: Course
  enrolled?: boolean
  showEnrollButton?: boolean
  className?: string
}

export function CourseCard({ course, enrolled = false, showEnrollButton = true, className = '' }: CourseCardProps) {
  const { user } = useAuth()
  const { success: showSuccess, error: showError } = useToast()
  const enrollMutation = useEnrollInCourse()

  const handleEnroll = async (e: React.MouseEvent) => {
    e.preventDefault()
    e.stopPropagation()
    
    if (!user) {
      showError('Please log in to enroll in courses')
      return
    }

    try {
      await enrollMutation.mutateAsync(course.id)
      showSuccess('Successfully enrolled in course!')
    } catch (error) {
      showError('Failed to enroll in course')
    }
  }

  const difficultyColor = {
    beginner: 'bg-green-100 text-green-800',
    intermediate: 'bg-yellow-100 text-yellow-800',
    advanced: 'bg-red-100 text-red-800'
  }

  const renderStars = (rating: number) => {
    return Array.from({ length: 5 }, (_, i) => (
      <span key={i}>
        {i < Math.floor(rating) ? (
          <StarSolidIcon className="w-4 h-4 text-yellow-400" />
        ) : (
          <StarIcon className="w-4 h-4 text-gray-300" />
        )}
      </span>
    ))
  }

  return (
    <motion.div
      whileHover={{ y: -4 }}
      transition={{ duration: 0.2 }}
      className={`bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden hover:shadow-lg transition-shadow ${className}`}
    >
      <Link href={`/courses/${course.id}`}>
        <div className="relative">
          <img
            src={course.thumbnail || '/api/placeholder/400/200'}
            alt={course.title}
            className="w-full h-48 object-cover"
          />
          <div className="absolute top-4 left-4">
            <span className={`px-2 py-1 rounded-full text-xs font-medium ${difficultyColor[course.difficulty]}`}>
              {course.difficulty}
            </span>
          </div>
          <div className="absolute top-4 right-4">
            <div className="bg-white/90 backdrop-blur-sm rounded-lg px-2 py-1 flex items-center space-x-1">
              <StarSolidIcon className="w-4 h-4 text-yellow-400" />
              <span className="text-sm font-medium">{course.rating.toFixed(1)}</span>
            </div>
          </div>
        </div>

        <div className="p-6">
          <div className="flex items-start justify-between mb-3">
            <h3 className="text-lg font-semibold text-gray-900 line-clamp-2">{course.title}</h3>
          </div>

          <p className="text-gray-600 text-sm mb-4 line-clamp-2">{course.description}</p>

          <div className="flex items-center space-x-4 mb-4 text-sm text-gray-500">
            <div className="flex items-center space-x-1">
              <ClockIcon className="w-4 h-4" />
              <span>{Math.round(course.duration / 60)}h</span>
            </div>
            <div className="flex items-center space-x-1">
              <UserGroupIcon className="w-4 h-4" />
              <span>{course.enrollmentCount}</span>
            </div>
            <div className="flex items-center space-x-1">
              <BookOpenIcon className="w-4 h-4" />
              <span>{course.modules?.length || 0} modules</span>
            </div>
          </div>

          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center space-x-2">
              <img
                src={course.instructor.avatar || '/api/placeholder/32/32'}
                alt={course.instructor.name}
                className="w-8 h-8 rounded-full"
              />
              <span className="text-sm text-gray-600">{course.instructor.name}</span>
            </div>
            <div className="flex items-center space-x-1">
              {renderStars(course.rating)}
              <span className="text-xs text-gray-500 ml-1">({course.reviewCount})</span>
            </div>
          </div>

          <div className="flex items-center justify-between">
            <div className="flex items-baseline space-x-2">
              <span className="text-2xl font-bold text-gray-900">
                ${course.price}
              </span>
              <span className="text-sm text-gray-500">{course.currency}</span>
            </div>

            {showEnrollButton && !enrolled && user?.role === 'student' && (
              <button
                onClick={handleEnroll}
                disabled={enrollMutation.isPending}
                className="bg-primary-600 text-white px-4 py-2 rounded-lg text-sm font-medium hover:bg-primary-700 transition-colors disabled:opacity-50"
              >
                {enrollMutation.isPending ? 'Enrolling...' : 'Enroll Now'}
              </button>
            )}

            {enrolled && (
              <div className="flex items-center space-x-2">
                <AcademicCapIcon className="w-5 h-5 text-green-600" />
                <span className="text-sm font-medium text-green-600">Enrolled</span>
              </div>
            )}

            {user?.role === 'teacher' && (
              <button className="bg-secondary-600 text-white px-4 py-2 rounded-lg text-sm font-medium hover:bg-secondary-700 transition-colors">
                <PlayIcon className="w-4 h-4 mr-1 inline" />
                Edit
              </button>
            )}
          </div>
        </div>
      </Link>
    </motion.div>
  )
}
