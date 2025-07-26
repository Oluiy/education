// src/app/courses/[id]/page.tsx
'use client'

import { useState } from 'react'
import { motion } from 'framer-motion'
import { useParams } from 'next/navigation'
import { useCourse, useEnrollInCourse, useUserEnrollments } from '@/hooks/useApi'
import { useAuth } from '@/contexts/AuthContext'
import { useToast } from '@/contexts/ToastContext'
import { LoadingPage } from '@/components/ui/Loading'
import {
  BookOpenIcon,
  ClockIcon,
  UserGroupIcon,
  StarIcon,
  PlayIcon,
  AcademicCapIcon,
  CheckIcon,
  LockClosedIcon
} from '@heroicons/react/24/outline'
import { StarIcon as StarSolidIcon } from '@heroicons/react/24/solid'

export default function CoursePage() {
  const params = useParams()
  const courseId = params.id as string
  const { user } = useAuth()
  const { success: showSuccess, error: showError } = useToast()
  
  const { data: course, isLoading: courseLoading } = useCourse(courseId)
  const { data: enrollments } = useUserEnrollments()
  const enrollMutation = useEnrollInCourse()

  const [activeTab, setActiveTab] = useState<'overview' | 'curriculum' | 'reviews'>('overview')

  if (courseLoading) {
    return <LoadingPage />
  }

  if (!course) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <h2 className="text-xl font-semibold text-gray-900 mb-2">Course not found</h2>
          <p className="text-gray-600">The course you're looking for doesn't exist.</p>
        </div>
      </div>
    )
  }

  const isEnrolled = enrollments?.some(e => e.courseId === courseId)
  const enrollment = enrollments?.find(e => e.courseId === courseId)

  const handleEnroll = async () => {
    if (!user) {
      showError('Please log in to enroll in courses')
      return
    }

    try {
      await enrollMutation.mutateAsync(courseId)
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
          <StarSolidIcon className="w-5 h-5 text-yellow-400" />
        ) : (
          <StarIcon className="w-5 h-5 text-gray-300" />
        )}
      </span>
    ))
  }

  const totalLessons = course.modules?.reduce((acc, module) => acc + module.lessons.length, 0) || 0
  const completedLessons = enrollment?.completedLessons.length || 0

  return (
    <div className="space-y-8">
      {/* Hero Section */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="bg-gradient-to-r from-primary-600 to-secondary-600 rounded-2xl overflow-hidden"
      >
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 p-8">
          <div className="text-white">
            <div className="flex items-center space-x-4 mb-4">
              <span className={`px-3 py-1 rounded-full text-sm font-medium ${difficultyColor[course.difficulty]} bg-white`}>
                {course.difficulty}
              </span>
              <div className="flex items-center space-x-1">
                {renderStars(course.rating)}
                <span className="ml-2 text-primary-100">({course.reviewCount} reviews)</span>
              </div>
            </div>

            <h1 className="text-3xl font-bold mb-4">{course.title}</h1>
            <p className="text-primary-100 text-lg mb-6">{course.description}</p>

            <div className="grid grid-cols-2 gap-4 mb-6">
              <div className="flex items-center space-x-2">
                <ClockIcon className="w-5 h-5 text-primary-200" />
                <span>{Math.round(course.duration / 60)} hours</span>
              </div>
              <div className="flex items-center space-x-2">
                <UserGroupIcon className="w-5 h-5 text-primary-200" />
                <span>{course.enrollmentCount} students</span>
              </div>
              <div className="flex items-center space-x-2">
                <BookOpenIcon className="w-5 h-5 text-primary-200" />
                <span>{totalLessons} lessons</span>
              </div>
              <div className="flex items-center space-x-2">
                <AcademicCapIcon className="w-5 h-5 text-primary-200" />
                <span>Certificate included</span>
              </div>
            </div>

            <div className="flex items-center space-x-4">
              <img
                src={course.instructor.avatar || '/api/placeholder/48/48'}
                alt={course.instructor.name}
                className="w-12 h-12 rounded-full border-2 border-primary-200"
              />
              <div>
                <p className="font-semibold">Instructor</p>
                <p className="text-primary-100">{course.instructor.name}</p>
              </div>
            </div>
          </div>

          <div className="lg:flex lg:items-center lg:justify-center">
            <img
              src={course.thumbnail || '/api/placeholder/500/300'}
              alt={course.title}
              className="w-full h-64 lg:h-80 object-cover rounded-xl"
            />
          </div>
        </div>
      </motion.div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Main Content */}
        <div className="lg:col-span-2 space-y-6">
          {/* Tabs */}
          <div className="border-b border-gray-200">
            <nav className="flex space-x-8">
              {[
                { id: 'overview', label: 'Overview' },
                { id: 'curriculum', label: 'Curriculum' },
                { id: 'reviews', label: 'Reviews' }
              ].map((tab) => (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id as any)}
                  className={`py-4 px-1 border-b-2 font-medium text-sm transition-colors ${
                    activeTab === tab.id
                      ? 'border-primary-500 text-primary-600'
                      : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                  }`}
                >
                  {tab.label}
                </button>
              ))}
            </nav>
          </div>

          {/* Tab Content */}
          <motion.div
            key={activeTab}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.3 }}
          >
            {activeTab === 'overview' && (
              <div className="space-y-6">
                <div>
                  <h3 className="text-lg font-semibold text-gray-900 mb-3">What you'll learn</h3>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                    {['Master advanced concepts', 'Build real-world projects', 'Get industry insights', 'Earn certification'].map((point, index) => (
                      <div key={index} className="flex items-start space-x-3">
                        <CheckIcon className="w-5 h-5 text-green-600 mt-0.5" />
                        <span className="text-gray-700">{point}</span>
                      </div>
                    ))}
                  </div>
                </div>

                <div>
                  <h3 className="text-lg font-semibold text-gray-900 mb-3">Course Tags</h3>
                  <div className="flex flex-wrap gap-2">
                    {course.tags?.map((tag, index) => (
                      <span
                        key={index}
                        className="px-3 py-1 bg-gray-100 text-gray-700 text-sm rounded-full"
                      >
                        {tag}
                      </span>
                    ))}
                  </div>
                </div>
              </div>
            )}

            {activeTab === 'curriculum' && (
              <div className="space-y-4">
                {course.modules?.map((module, moduleIndex) => (
                  <div key={module.id} className="border border-gray-200 rounded-lg overflow-hidden">
                    <div className="bg-gray-50 px-6 py-4">
                      <h4 className="font-semibold text-gray-900">
                        Module {moduleIndex + 1}: {module.title}
                      </h4>
                      <p className="text-gray-600 text-sm mt-1">{module.description}</p>
                    </div>
                    <div className="divide-y divide-gray-200">
                      {module.lessons.map((lesson, lessonIndex) => {
                        const isCompleted = enrollment?.completedLessons.includes(lesson.id)
                        const isLocked = !isEnrolled && lessonIndex > 0

                        return (
                          <div key={lesson.id} className="px-6 py-4 flex items-center justify-between">
                            <div className="flex items-center space-x-3">
                              <div className={`w-6 h-6 rounded-full flex items-center justify-center ${
                                isCompleted 
                                  ? 'bg-green-100 text-green-600' 
                                  : isLocked 
                                  ? 'bg-gray-100 text-gray-400'
                                  : 'bg-primary-100 text-primary-600'
                              }`}>
                                {isCompleted ? (
                                  <CheckIcon className="w-4 h-4" />
                                ) : isLocked ? (
                                  <LockClosedIcon className="w-4 h-4" />
                                ) : (
                                  <PlayIcon className="w-4 h-4" />
                                )}
                              </div>
                              <div>
                                <p className="font-medium text-gray-900">{lesson.title}</p>
                                <p className="text-gray-600 text-sm">{lesson.description}</p>
                              </div>
                            </div>
                            <div className="flex items-center space-x-4">
                              <span className="text-sm text-gray-500">
                                {Math.round(lesson.duration / 60)} min
                              </span>
                              <span className={`px-2 py-1 text-xs rounded-full ${
                                lesson.type === 'video' ? 'bg-blue-100 text-blue-800' :
                                lesson.type === 'quiz' ? 'bg-purple-100 text-purple-800' :
                                lesson.type === 'assignment' ? 'bg-orange-100 text-orange-800' :
                                'bg-gray-100 text-gray-800'
                              }`}>
                                {lesson.type}
                              </span>
                            </div>
                          </div>
                        )
                      })}
                    </div>
                  </div>
                ))}
              </div>
            )}

            {activeTab === 'reviews' && (
              <div className="space-y-6">
                <div className="text-center py-8">
                  <StarSolidIcon className="w-12 h-12 text-yellow-400 mx-auto mb-4" />
                  <h3 className="text-lg font-medium text-gray-900 mb-2">No reviews yet</h3>
                  <p className="text-gray-600">Be the first to review this course!</p>
                </div>
              </div>
            )}
          </motion.div>
        </div>

        {/* Sidebar */}
        <div className="space-y-6">
          {/* Enrollment Card */}
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.2 }}
            className="bg-white rounded-xl shadow-sm border border-gray-200 p-6"
          >
            <div className="text-center mb-6">
              <div className="text-3xl font-bold text-gray-900 mb-2">
                ${course.price}
              </div>
              <p className="text-gray-600">One-time payment</p>
            </div>

            {isEnrolled ? (
              <div className="space-y-4">
                <div className="flex items-center justify-center space-x-2 text-green-600 mb-4">
                  <AcademicCapIcon className="w-6 h-6" />
                  <span className="font-semibold">Enrolled</span>
                </div>
                
                <div>
                  <div className="flex justify-between text-sm text-gray-600 mb-2">
                    <span>Progress</span>
                    <span>{Math.round((completedLessons / totalLessons) * 100)}%</span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div 
                      className="bg-green-600 h-2 rounded-full transition-all duration-300"
                      style={{ width: `${(completedLessons / totalLessons) * 100}%` }}
                    />
                  </div>
                  <p className="text-xs text-gray-500 mt-1">
                    {completedLessons} of {totalLessons} lessons completed
                  </p>
                </div>

                <button className="w-full bg-primary-600 text-white py-3 rounded-lg font-semibold hover:bg-primary-700 transition-colors">
                  Continue Learning
                </button>
              </div>
            ) : (
              <div className="space-y-4">
                <button
                  onClick={handleEnroll}
                  disabled={enrollMutation.isPending || !user}
                  className="w-full bg-primary-600 text-white py-3 rounded-lg font-semibold hover:bg-primary-700 transition-colors disabled:opacity-50"
                >
                  {enrollMutation.isPending ? 'Enrolling...' : 'Enroll Now'}
                </button>
                
                {!user && (
                  <p className="text-center text-sm text-gray-600">
                    Please log in to enroll in this course
                  </p>
                )}
              </div>
            )}
          </motion.div>

          {/* Course Features */}
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.3 }}
            className="bg-white rounded-xl shadow-sm border border-gray-200 p-6"
          >
            <h3 className="font-semibold text-gray-900 mb-4">This course includes:</h3>
            <div className="space-y-3">
              {[
                { icon: ClockIcon, text: `${Math.round(course.duration / 60)} hours of content` },
                { icon: BookOpenIcon, text: `${totalLessons} lessons` },
                { icon: AcademicCapIcon, text: 'Certificate of completion' },
                { icon: UserGroupIcon, text: 'Lifetime access' }
              ].map((feature, index) => (
                <div key={index} className="flex items-center space-x-3">
                  <feature.icon className="w-5 h-5 text-primary-600" />
                  <span className="text-gray-700">{feature.text}</span>
                </div>
              ))}
            </div>
          </motion.div>
        </div>
      </div>
    </div>
  )
}
