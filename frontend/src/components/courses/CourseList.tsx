// src/components/courses/CourseList.tsx
'use client'

import { useState } from 'react'
import { motion } from 'framer-motion'
import { useCourses, useUserEnrollments } from '@/hooks/useApi'
import { CourseCard } from './CourseCard'
import { LoadingSpinner } from '@/components/ui/Loading'
import { SearchAndFilter } from '@/components/ui/SearchAndFilter'
import {
  FunnelIcon,
  AdjustmentsHorizontalIcon,
  Squares2X2Icon,
  ListBulletIcon
} from '@heroicons/react/24/outline'

interface CourseListProps {
  showEnrolled?: boolean
  category?: string
  teacherId?: string
}

export function CourseList({ showEnrolled = false, category, teacherId }: CourseListProps) {
  const [search, setSearch] = useState('')
  const [filters, setFilters] = useState({
    difficulty: '',
    category: category || '',
    sortBy: 'popularity'
  })
  const [viewMode, setViewMode] = useState<'grid' | 'list'>('grid')
  const [currentPage, setCurrentPage] = useState(1)

  const { data: coursesData, isLoading } = useCourses({
    search: search || undefined,
    difficulty: filters.difficulty || undefined,
    category: filters.category || undefined,
    page: currentPage,
    limit: 12
  })

  const { data: enrollments } = useUserEnrollments()
  
  const enrolledCourseIds = new Set(enrollments?.map(e => e.courseId) || [])

  const handleSearch = (value: string) => {
    setSearch(value)
    setCurrentPage(1)
  }

  const handleFilterChange = (newFilters: any) => {
    setFilters(prev => ({ ...prev, ...newFilters }))
    setCurrentPage(1)
  }

  const filterOptions = [
    {
      id: 'difficulty',
      label: 'Difficulty',
      type: 'select' as const,
      options: [
        { value: '', label: 'All Levels' },
        { value: 'beginner', label: 'Beginner' },
        { value: 'intermediate', label: 'Intermediate' },
        { value: 'advanced', label: 'Advanced' }
      ]
    },
    {
      id: 'category',
      label: 'Category',
      type: 'select' as const,
      options: [
        { value: '', label: 'All Categories' },
        { value: 'mathematics', label: 'Mathematics' },
        { value: 'science', label: 'Science' },
        { value: 'literature', label: 'Literature' },
        { value: 'history', label: 'History' },
        { value: 'arts', label: 'Arts' },
        { value: 'technology', label: 'Technology' }
      ]
    },
    {
      id: 'sortBy',
      label: 'Sort By',
      type: 'select' as const,
      options: [
        { value: 'popularity', label: 'Most Popular' },
        { value: 'rating', label: 'Highest Rated' },
        { value: 'newest', label: 'Newest' },
        { value: 'price_low', label: 'Price: Low to High' },
        { value: 'price_high', label: 'Price: High to Low' }
      ]
    }
  ]

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-12">
        <LoadingSpinner size="lg" />
      </div>
    )
  }

  const courses = showEnrolled 
    ? coursesData?.courses?.filter(course => enrolledCourseIds.has(course.id)) || []
    : coursesData?.courses || []

  return (
    <div className="space-y-6">
      {/* Search and Filters */}
      <div className="flex flex-col sm:flex-row gap-4">
        <div className="flex-1">
          <SearchAndFilter
            searchValue={search}
            onSearchChange={handleSearch}
            filters={filterOptions}
            activeFilters={filters}
            onFilterChange={handleFilterChange}
            onClearFilters={() => setFilters({ difficulty: '', category: '', sortBy: 'popularity' })}
            searchPlaceholder="Search courses..."
          />
        </div>

        {/* View Mode Toggle */}
        <div className="flex items-center space-x-2">
          <button
            onClick={() => setViewMode('grid')}
            className={`p-2 rounded-lg transition-colors ${
              viewMode === 'grid' 
                ? 'bg-primary-100 text-primary-600' 
                : 'text-gray-400 hover:text-gray-600'
            }`}
          >
            <Squares2X2Icon className="w-5 h-5" />
          </button>
          <button
            onClick={() => setViewMode('list')}
            className={`p-2 rounded-lg transition-colors ${
              viewMode === 'list' 
                ? 'bg-primary-100 text-primary-600' 
                : 'text-gray-400 hover:text-gray-600'
            }`}
          >
            <ListBulletIcon className="w-5 h-5" />
          </button>
        </div>
      </div>

      {/* Results Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-xl font-semibold text-gray-900">
            {showEnrolled ? 'My Courses' : 'All Courses'}
          </h2>
          <p className="text-gray-600 text-sm">
            {courses.length} course{courses.length !== 1 ? 's' : ''} found
          </p>
        </div>
      </div>

      {/* Course Grid/List */}
      {courses.length > 0 ? (
        <div
          className={
            viewMode === 'grid'
              ? 'grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6'
              : 'space-y-4'
          }
        >
          {courses.map((course, index) => (
            <motion.div
              key={course.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.1 }}
            >
              <CourseCard
                course={course}
                enrolled={enrolledCourseIds.has(course.id)}
                showEnrollButton={!showEnrolled}
                className={viewMode === 'list' ? 'flex' : ''}
              />
            </motion.div>
          ))}
        </div>
      ) : (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="text-center py-12"
        >
          <div className="w-24 h-24 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
            <FunnelIcon className="w-12 h-12 text-gray-400" />
          </div>
          <h3 className="text-lg font-medium text-gray-900 mb-2">No courses found</h3>
          <p className="text-gray-600 mb-4">Try adjusting your search or filter criteria</p>
          <button
            onClick={() => {
              setSearch('')
              setFilters({ difficulty: '', category: '', sortBy: 'popularity' })
            }}
            className="text-primary-600 hover:text-primary-700 font-medium"
          >
            Clear all filters
          </button>
        </motion.div>
      )}

      {/* Pagination */}
      {coursesData && coursesData.total > coursesData.limit && (
        <div className="flex items-center justify-center space-x-2 pt-8">
          <button
            onClick={() => setCurrentPage(prev => Math.max(1, prev - 1))}
            disabled={currentPage === 1}
            className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            Previous
          </button>
          
          {Array.from({ length: Math.ceil(coursesData.total / coursesData.limit) }, (_, i) => i + 1)
            .slice(Math.max(0, currentPage - 3), currentPage + 2)
            .map(pageNum => (
              <button
                key={pageNum}
                onClick={() => setCurrentPage(pageNum)}
                className={`px-4 py-2 text-sm font-medium rounded-md ${
                  pageNum === currentPage
                    ? 'bg-primary-600 text-white'
                    : 'text-gray-700 bg-white border border-gray-300 hover:bg-gray-50'
                }`}
              >
                {pageNum}
              </button>
            ))}
          
          <button
            onClick={() => setCurrentPage(prev => Math.min(Math.ceil(coursesData.total / coursesData.limit), prev + 1))}
            disabled={currentPage >= Math.ceil(coursesData.total / coursesData.limit)}
            className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            Next
          </button>
        </div>
      )}
    </div>
  )
}
