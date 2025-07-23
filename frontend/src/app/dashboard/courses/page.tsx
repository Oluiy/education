'use client'

import { useState } from 'react'
import { motion } from 'framer-motion'
import {
  BookOpenIcon,
  ClockIcon,
  UserGroupIcon,
  ChartBarIcon,
  PlayIcon,
  PlusIcon,
  FunnelIcon,
  MagnifyingGlassIcon,
  StarIcon
} from '@heroicons/react/24/outline'

// Mock course data
const mockCourses = [
  {
    id: 1,
    title: 'Advanced Mathematics',
    instructor: 'Mr. Johnson',
    description: 'Dive deep into calculus, algebra, and advanced mathematical concepts.',
    progress: 78,
    duration: '12 weeks',
    students: 24,
    rating: 4.8,
    totalLessons: 45,
    completedLessons: 35,
    nextLesson: 'Derivatives and Applications',
    thumbnail: '/api/placeholder/300/200',
    category: 'Mathematics',
    difficulty: 'Advanced',
    isEnrolled: true,
    lastAccessed: '2 hours ago'
  },
  {
    id: 2,
    title: 'Physics Fundamentals',
    instructor: 'Dr. Smith',
    description: 'Explore the fundamental principles of physics through hands-on experiments.',
    progress: 65,
    duration: '10 weeks',
    students: 32,
    rating: 4.6,
    totalLessons: 38,
    completedLessons: 25,
    nextLesson: 'Motion and Energy',
    thumbnail: '/api/placeholder/300/200',
    category: 'Science',
    difficulty: 'Intermediate',
    isEnrolled: true,
    lastAccessed: '1 day ago'
  },
  {
    id: 3,
    title: 'English Literature',
    instructor: 'Ms. Brown',
    description: 'Analyze classic and contemporary literature from around the world.',
    progress: 92,
    duration: '8 weeks',
    students: 28,
    rating: 4.9,
    totalLessons: 32,
    completedLessons: 29,
    nextLesson: 'Modern Poetry Analysis',
    thumbnail: '/api/placeholder/300/200',
    category: 'Language',
    difficulty: 'Intermediate',
    isEnrolled: true,
    lastAccessed: '3 hours ago'
  },
  {
    id: 4,
    title: 'Computer Science Basics',
    instructor: 'Prof. Davis',
    description: 'Learn programming fundamentals and computer science concepts.',
    progress: 0,
    duration: '14 weeks',
    students: 156,
    rating: 4.7,
    totalLessons: 52,
    completedLessons: 0,
    nextLesson: 'Introduction to Programming',
    thumbnail: '/api/placeholder/300/200',
    category: 'Technology',
    difficulty: 'Beginner',
    isEnrolled: false,
    lastAccessed: null
  },
  {
    id: 5,
    title: 'Chemistry Lab',
    instructor: 'Dr. Wilson',
    description: 'Hands-on chemistry experiments and theoretical knowledge.',
    progress: 0,
    duration: '12 weeks',
    students: 89,
    rating: 4.5,
    totalLessons: 40,
    completedLessons: 0,
    nextLesson: 'Basic Chemical Reactions',
    thumbnail: '/api/placeholder/300/200',
    category: 'Science',
    difficulty: 'Intermediate',
    isEnrolled: false,
    lastAccessed: null
  }
]

const categories = ['All', 'Mathematics', 'Science', 'Language', 'Technology', 'Arts']
const difficulties = ['All', 'Beginner', 'Intermediate', 'Advanced']

export default function CoursesPage() {
  const [searchTerm, setSearchTerm] = useState('')
  const [selectedCategory, setSelectedCategory] = useState('All')
  const [selectedDifficulty, setSelectedDifficulty] = useState('All')
  const [viewMode, setViewMode] = useState<'enrolled' | 'all'>('enrolled')

  const filteredCourses = mockCourses.filter(course => {
    const matchesSearch = course.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         course.instructor.toLowerCase().includes(searchTerm.toLowerCase())
    const matchesCategory = selectedCategory === 'All' || course.category === selectedCategory
    const matchesDifficulty = selectedDifficulty === 'All' || course.difficulty === selectedDifficulty
    const matchesViewMode = viewMode === 'all' || course.isEnrolled

    return matchesSearch && matchesCategory && matchesDifficulty && matchesViewMode
  })

  const getDifficultyColor = (difficulty: string) => {
    switch (difficulty) {
      case 'Beginner':
        return 'bg-green-100 text-green-800'
      case 'Intermediate':
        return 'bg-yellow-100 text-yellow-800'
      case 'Advanced':
        return 'bg-red-100 text-red-800'
      default:
        return 'bg-gray-100 text-gray-800'
    }
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Main Content - Centralized */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="space-y-6">
          {/* Header */}
          <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="flex flex-col lg:flex-row lg:items-center lg:justify-between"
        >
          <div>
            <h1 className="text-2xl font-heading font-bold text-gray-900 mb-2">
              My Courses
            </h1>
            <p className="text-gray-600">
              Continue your learning journey with our comprehensive courses
            </p>
          </div>
          
          <div className="flex items-center space-x-4 mt-4 lg:mt-0">
            <div className="flex bg-gray-100 rounded-lg p-1">
              <button
                onClick={() => setViewMode('enrolled')}
                className={`px-4 py-2 text-sm font-medium rounded-md transition-colors ${
                  viewMode === 'enrolled'
                    ? 'bg-white text-gray-900 shadow-sm'
                    : 'text-gray-600 hover:text-gray-900'
                }`}
              >
                Enrolled ({mockCourses.filter(c => c.isEnrolled).length})
              </button>
              <button
                onClick={() => setViewMode('all')}
                className={`px-4 py-2 text-sm font-medium rounded-md transition-colors ${
                  viewMode === 'all'
                    ? 'bg-white text-gray-900 shadow-sm'
                    : 'text-gray-600 hover:text-gray-900'
                }`}
              >
                Browse All
              </button>
            </div>
          </div>
        </motion.div>

        {/* Search and Filters */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="flex flex-col lg:flex-row gap-4"
        >
          {/* Search */}
          <div className="relative flex-1">
            <MagnifyingGlassIcon className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
            <input
              type="text"
              placeholder="Search courses..."
              className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
            />
          </div>

          {/* Filters */}
          <div className="flex flex-wrap gap-4">
            <select
              className="px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
              value={selectedCategory}
              onChange={(e) => setSelectedCategory(e.target.value)}
            >
              {categories.map(category => (
                <option key={category} value={category}>{category}</option>
              ))}
            </select>

            <select
              className="px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
              value={selectedDifficulty}
              onChange={(e) => setSelectedDifficulty(e.target.value)}
            >
              {difficulties.map(difficulty => (
                <option key={difficulty} value={difficulty}>{difficulty}</option>
              ))}
            </select>
          </div>
        </motion.div>

        {/* Course Grid */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.2 }}
          className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6"
        >
          {filteredCourses.map((course, index) => (
            <motion.div
              key={course.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.1 }}
              className="card hover:shadow-medium transition-all duration-200 group"
            >
              {/* Course Image */}
              <div className="relative h-48 bg-gray-100 rounded-t-xl overflow-hidden">
                <div className="absolute inset-0 bg-gradient-to-br from-primary-500 to-secondary-500 opacity-80"></div>
                <div className="absolute inset-0 flex items-center justify-center">
                  <BookOpenIcon className="w-16 h-16 text-white opacity-80" />
                </div>
                
                {/* Course badges */}
                <div className="absolute top-4 left-4">
                  <span className={`px-2 py-1 text-xs font-medium rounded-full ${getDifficultyColor(course.difficulty)}`}>
                    {course.difficulty}
                  </span>
                </div>
                
                <div className="absolute top-4 right-4">
                  <div className="flex items-center space-x-1 text-white text-xs">
                    <StarIcon className="w-3 h-3 fill-current" />
                    <span>{course.rating}</span>
                  </div>
                </div>

                {/* Progress overlay for enrolled courses */}
                {course.isEnrolled && course.progress > 0 && (
                  <div className="absolute bottom-0 left-0 right-0 bg-black bg-opacity-50 text-white p-2">
                    <div className="flex items-center justify-between text-xs">
                      <span>{course.progress}% complete</span>
                      <span>{course.completedLessons}/{course.totalLessons} lessons</span>
                    </div>
                    <div className="w-full bg-gray-300 rounded-full h-1 mt-1">
                      <div 
                        className="bg-white h-1 rounded-full transition-all duration-300"
                        style={{ width: `${course.progress}%` }}
                      />
                    </div>
                  </div>
                )}
              </div>

              {/* Course Content */}
              <div className="card-body">
                <div className="mb-4">
                  <h3 className="font-heading font-semibold text-gray-900 mb-2 group-hover:text-primary-600 transition-colors">
                    {course.title}
                  </h3>
                  <p className="text-sm text-gray-600 mb-3 line-clamp-2">
                    {course.description}
                  </p>
                  
                  <div className="flex items-center text-xs text-gray-500 space-x-4">
                    <div className="flex items-center">
                      <UserGroupIcon className="w-4 h-4 mr-1" />
                      {course.students} students
                    </div>
                    <div className="flex items-center">
                      <ClockIcon className="w-4 h-4 mr-1" />
                      {course.duration}
                    </div>
                  </div>
                </div>

                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-gray-900">{course.instructor}</p>
                    {course.isEnrolled && course.lastAccessed && (
                      <p className="text-xs text-gray-500">Last accessed {course.lastAccessed}</p>
                    )}
                  </div>
                  
                  {course.isEnrolled ? (
                    <button className="btn-primary btn-sm">
                      <PlayIcon className="w-4 h-4 mr-1" />
                      Continue
                    </button>
                  ) : (
                    <button className="btn-secondary btn-sm group-hover:btn-primary">
                      <PlusIcon className="w-4 h-4 mr-1" />
                      Enroll
                    </button>
                  )}
                </div>

                {/* Next lesson for enrolled courses */}
                {course.isEnrolled && (
                  <div className="mt-4 pt-4 border-t border-gray-100">
                    <p className="text-xs text-gray-500 mb-1">Next lesson:</p>
                    <p className="text-sm font-medium text-gray-900">{course.nextLesson}</p>
                  </div>
                )}
              </div>
            </motion.div>
          ))}
        </motion.div>

        {/* Empty state */}
        {filteredCourses.length === 0 && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="text-center py-12"
          >
            <BookOpenIcon className="w-16 h-16 mx-auto text-gray-300 mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">No courses found</h3>
            <p className="text-gray-600 mb-6">
              Try adjusting your search criteria or browse all available courses.
            </p>
            {viewMode === 'enrolled' && (
              <button
                onClick={() => setViewMode('all')}
                className="btn-primary"
              >
                Browse All Courses
              </button>
            )}
          </motion.div>
        )}
        </div>
      </div>
    </div>
  )
}
