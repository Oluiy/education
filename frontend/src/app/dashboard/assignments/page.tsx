'use client'

import { useState } from 'react'
import { motion } from 'framer-motion'
import {
  DocumentTextIcon,
  CalendarIcon,
  ClockIcon,
  CheckCircleIcon,
  ExclamationTriangleIcon,
  FunnelIcon,
  MagnifyingGlassIcon,
  BookOpenIcon,
  UserIcon,
  PaperClipIcon,
  ArrowUpIcon
} from '@heroicons/react/24/outline'

interface Assignment {
  id: number
  title: string
  course: string
  instructor: string
  description: string
  dueDate: string
  submittedDate: string | null
  status: string
  priority: string
  points: number
  estimatedTime: string
  type: string
  attachments: string[]
  instructions?: string
  grade?: number
  feedback?: string
}

// Mock assignment data
const mockAssignments: Assignment[] = [
  {
    id: 1,
    title: 'Chemistry Lab Safety Quiz',
    course: 'Chemistry Lab',
    instructor: 'Dr. Wilson',
    description: 'Safety protocol quiz - must score 100% to access lab equipment.',
    dueDate: '2024-03-20',
    submittedDate: null,
    status: 'overdue',
    priority: 'high',
    points: 10,
    estimatedTime: '20 minutes',
    type: 'quiz',
    attachments: ['safety_manual.pdf'],
    instructions: 'Must achieve 100% to pass. Unlimited attempts allowed.'
  },
  {
    id: 2,
    title: 'Calculus Problem Set #5',
    course: 'Advanced Mathematics',
    instructor: 'Mr. Johnson', 
    description: 'Solve differential equations and integration problems.',
    dueDate: '2024-01-18',
    submittedDate: null,
    status: 'pending',
    priority: 'high',
    points: 25,
    estimatedTime: '2 hours',
    type: 'homework',
    attachments: [],
    instructions: 'Follow the lab report template. Include introduction, methodology, results, and conclusion.'
  },
  {
    id: 3,
    title: 'Shakespeare Essay',
    course: 'English Literature',
    instructor: 'Ms. Brown',
    description: 'Analyze the theme of betrayal in Hamlet. 1500-2000 words.',
    dueDate: '2024-03-30',
    submittedDate: null,
    status: 'pending',
    priority: 'medium',
    points: 50,
    estimatedTime: '4 hours',
    type: 'essay',
    attachments: ['essay_guidelines.pdf'],
    instructions: 'Use MLA format. Include at least 5 scholarly sources. Submit through the online portal.'
  },
  {
    id: 4,
    title: 'Trigonometry Quiz',
    course: 'Advanced Mathematics',
    instructor: 'Mr. Johnson',
    description: 'Online quiz covering sine, cosine, and tangent functions.',
    dueDate: '2024-03-22',
    submittedDate: '2024-03-21',
    status: 'submitted',
    priority: 'low',
    points: 15,
    estimatedTime: '45 minutes',
    type: 'quiz',
    attachments: [],
    instructions: 'Complete within 45 minutes. One attempt only.',
    grade: 14,
    feedback: 'Excellent work! Minor error on question 7.'
  }
]

const statusColors = {
  pending: 'bg-yellow-100 text-yellow-800',
  submitted: 'bg-green-100 text-green-800',
  overdue: 'bg-red-100 text-red-800',
  graded: 'bg-blue-100 text-blue-800'
}

const priorityColors = {
  low: 'bg-gray-100 text-gray-800',
  medium: 'bg-yellow-100 text-yellow-800',
  high: 'bg-red-100 text-red-800'
}

const typeIcons = {
  homework: DocumentTextIcon,
  lab: BookOpenIcon,
  essay: DocumentTextIcon,
  quiz: CheckCircleIcon,
  project: FunnelIcon
}

export default function AssignmentsPage() {
  const [searchTerm, setSearchTerm] = useState('')
  const [statusFilter, setStatusFilter] = useState('all')
  const [priorityFilter, setPriorityFilter] = useState('all')
  const [sortBy, setSortBy] = useState('dueDate')

  const filteredAssignments = mockAssignments
    .filter(assignment => {
      const matchesSearch = assignment.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
                           assignment.course.toLowerCase().includes(searchTerm.toLowerCase())
      const matchesStatus = statusFilter === 'all' || assignment.status === statusFilter
      const matchesPriority = priorityFilter === 'all' || assignment.priority === priorityFilter
      
      return matchesSearch && matchesStatus && matchesPriority
    })
    .sort((a, b) => {
      if (sortBy === 'dueDate') {
        return new Date(a.dueDate).getTime() - new Date(b.dueDate).getTime()
      } else if (sortBy === 'priority') {
        const priorityOrder = { high: 3, medium: 2, low: 1 }
        return priorityOrder[b.priority as keyof typeof priorityOrder] - priorityOrder[a.priority as keyof typeof priorityOrder]
      }
      return 0
    })

  const formatDate = (dateString: string) => {
    const date = new Date(dateString)
    const today = new Date()
    const diffTime = date.getTime() - today.getTime()
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24))
    
    if (diffDays === 0) return 'Due today'
    if (diffDays === 1) return 'Due tomorrow'
    if (diffDays < 0) return `Overdue by ${Math.abs(diffDays)} days`
    return `Due in ${diffDays} days`
  }

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'submitted':
        return <CheckCircleIcon className="w-5 h-5 text-green-600" />
      case 'overdue':
        return <ExclamationTriangleIcon className="w-5 h-5 text-red-600" />
      default:
        return <ClockIcon className="w-5 h-5 text-yellow-600" />
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
              Assignments
            </h1>
            <p className="text-gray-600">
              Track and manage your assignments and deadlines
            </p>
          </div>
          
          <div className="flex items-center space-x-4 mt-4 lg:mt-0">
            <div className="flex items-center space-x-2 text-sm text-gray-600">
              <div className="flex items-center">
                <div className="w-3 h-3 bg-red-500 rounded-full mr-2"></div>
                {mockAssignments.filter(a => a.status === 'overdue').length} Overdue
              </div>
              <div className="flex items-center">
                <div className="w-3 h-3 bg-yellow-500 rounded-full mr-2"></div>
                {mockAssignments.filter(a => a.status === 'pending').length} Pending
              </div>
              <div className="flex items-center">
                <div className="w-3 h-3 bg-green-500 rounded-full mr-2"></div>
                {mockAssignments.filter(a => a.status === 'submitted').length} Submitted
              </div>
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
              placeholder="Search assignments..."
              className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
            />
          </div>

          {/* Filters */}
          <div className="flex flex-wrap gap-4">
            <select
              className="px-8 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
            >
              <option value="all">All Status</option>
              <option value="pending">Pending</option>
              <option value="submitted">Submitted</option>
              <option value="overdue">Overdue</option>
              <option value="graded">Graded</option>
            </select>

            <select
              className="px-8 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
              value={priorityFilter}
              onChange={(e) => setPriorityFilter(e.target.value)}
            >
              <option value="all">All Priority</option>
              <option value="high">High Priority</option>
              <option value="medium">Medium Priority</option>
              <option value="low">Low Priority</option>
            </select>

            <select
              className="px-8 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
              value={sortBy}
              onChange={(e) => setSortBy(e.target.value)}
            >
              <option value="dueDate">Sort by Due Date</option>
              <option value="priority">Sort by Priority</option>
            </select>
          </div>
        </motion.div>

        {/* Assignments List */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.2 }}
          className="space-y-4"
        >
          {filteredAssignments.map((assignment, index) => {
            const TypeIcon = typeIcons[assignment.type as keyof typeof typeIcons] || DocumentTextIcon
            
            return (
              <motion.div
                key={assignment.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.1 }}
                className="card hover:shadow-medium transition-all duration-200"
              >
                <div className="card-body">
                  <div className="flex flex-col lg:flex-row lg:items-start lg:justify-between">
                    {/* Main Content */}
                    <div className="flex-1">
                      <div className="flex items-start space-x-4">
                        <div className="flex-shrink-0">
                          <div className="w-12 h-12 bg-primary-100 rounded-lg flex items-center justify-center">
                            <TypeIcon className="w-6 h-6 text-primary-600" />
                          </div>
                        </div>
                        
                        <div className="flex-1 min-w-0">
                          <div className="flex items-center space-x-3 mb-2">
                            <h3 className="font-heading font-semibold text-gray-900">
                              {assignment.title}
                            </h3>
                            {getStatusIcon(assignment.status)}
                          </div>
                          
                          <div className="flex flex-wrap items-center gap-2 mb-3">
                            <span className={`px-2 py-1 text-xs font-medium rounded-full ${statusColors[assignment.status as keyof typeof statusColors]}`}>
                              {assignment.status.charAt(0).toUpperCase() + assignment.status.slice(1)}
                            </span>
                            <span className={`px-2 py-1 text-xs font-medium rounded-full ${priorityColors[assignment.priority as keyof typeof priorityColors]}`}>
                              {assignment.priority.charAt(0).toUpperCase() + assignment.priority.slice(1)} Priority
                            </span>
                            <span className="px-2 py-1 text-xs bg-gray-100 text-gray-800 rounded-full">
                              {assignment.type.charAt(0).toUpperCase() + assignment.type.slice(1)}
                            </span>
                          </div>
                          
                          <p className="text-gray-600 mb-3 line-clamp-2">
                            {assignment.description}
                          </p>
                          
                          <div className="flex flex-wrap items-center gap-4 text-sm text-gray-500">
                            <div className="flex items-center">
                              <BookOpenIcon className="w-4 h-4 mr-1" />
                              {assignment.course}
                            </div>
                            <div className="flex items-center">
                              <UserIcon className="w-4 h-4 mr-1" />
                              {assignment.instructor}
                            </div>
                            <div className="flex items-center">
                              <ClockIcon className="w-4 h-4 mr-1" />
                              {assignment.estimatedTime}
                            </div>
                            <div className="flex items-center">
                              <ArrowUpIcon className="w-4 h-4 mr-1" />
                              {assignment.points} points
                            </div>
                          </div>
                        </div>
                      </div>
                    </div>

                    {/* Right Side - Due Date and Actions */}
                    <div className="mt-4 lg:mt-0 lg:ml-6 flex-shrink-0">
                      <div className="text-right">
                        <div className="flex items-center justify-end mb-2">
                          <CalendarIcon className="w-4 h-4 mr-1 text-gray-400" />
                          <span className="text-sm text-gray-600">
                            {formatDate(assignment.dueDate)}
                          </span>
                        </div>
                        
                        <p className="text-xs text-gray-500 mb-4">
                          Due: {new Date(assignment.dueDate).toLocaleDateString()}
                        </p>
                        
                        {assignment.status === 'submitted' && assignment.grade !== undefined ? (
                          <div className="text-center p-3 bg-green-50 rounded-lg">
                            <p className="text-sm font-medium text-green-800">
                              Grade: {assignment.grade}/{assignment.points}
                            </p>
                            {assignment.feedback && (
                              <p className="text-xs text-green-600 mt-1">
                                {assignment.feedback}
                              </p>
                            )}
                          </div>
                        ) : assignment.status === 'overdue' ? (
                          <button className="btn-secondary btn-sm w-full bg-red-50 text-red-700 hover:bg-red-100">
                            Submit Late
                          </button>
                        ) : assignment.status === 'submitted' ? (
                          <div className="text-center p-2 bg-green-50 rounded-lg">
                            <p className="text-sm text-green-800">Submitted</p>
                            <p className="text-xs text-green-600">
                              {assignment.submittedDate && new Date(assignment.submittedDate).toLocaleDateString()}
                            </p>
                          </div>
                        ) : (
                          <button className="btn-primary btn-sm w-full">
                            Start Assignment
                          </button>
                        )}
                      </div>
                    </div>
                  </div>

                  {/* Instructions and Attachments */}
                  {(assignment.instructions || assignment.attachments.length > 0) && (
                    <div className="mt-4 pt-4 border-t border-gray-100">
                      {assignment.instructions && (
                        <div className="mb-3">
                          <h4 className="text-sm font-medium text-gray-900 mb-1">Instructions:</h4>
                          <p className="text-sm text-gray-600">{assignment.instructions}</p>
                        </div>
                      )}
                      
                      {assignment.attachments.length > 0 && (
                        <div>
                          <h4 className="text-sm font-medium text-gray-900 mb-2">Attachments:</h4>
                          <div className="flex flex-wrap gap-2">
                            {assignment.attachments.map((attachment, idx) => (
                              <span
                                key={idx}
                                className="inline-flex items-center px-3 py-1 rounded-md text-sm bg-gray-100 text-gray-800 hover:bg-gray-200 cursor-pointer"
                              >
                                <DocumentTextIcon className="w-4 h-4 mr-1" />
                                {attachment}
                              </span>
                            ))}
                          </div>
                        </div>
                      )}
                    </div>
                  )}
                </div>
              </motion.div>
            )
          })}
        </motion.div>

        {/* Empty state */}
        {filteredAssignments.length === 0 && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="text-center py-12"
          >
            <DocumentTextIcon className="w-16 h-16 mx-auto text-gray-300 mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">No assignments found</h3>
            <p className="text-gray-600">
              Try adjusting your search criteria or filters.
            </p>
          </motion.div>
        )}
        </div>
      </div>
    </div>
  )
}
