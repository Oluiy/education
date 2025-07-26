'use client'

import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import {
  DocumentTextIcon,
  PhotoIcon,
  VideoCameraIcon,
  CloudArrowUpIcon,
  PlusIcon,
  EyeIcon,
  TrashIcon,
  ArrowDownTrayIcon,
  FolderIcon,
  MagnifyingGlassIcon
} from '@heroicons/react/24/outline'

interface Resource {
  id: string
  name: string
  type: 'document' | 'image' | 'video' | 'audio' | 'other'
  size: number
  course_id: string
  course_name: string
  uploaded_at: string
  download_count: number
  file_url: string
}

interface Course {
  id: string
  name: string
  code: string
}

export default function TeacherResourcesPage() {
  const [resources, setResources] = useState<Resource[]>([])
  const [courses, setCourses] = useState<Course[]>([])
  const [selectedCourse, setSelectedCourse] = useState<string>('all')
  const [searchTerm, setSearchTerm] = useState('')
  const [fileType, setFileType] = useState<string>('all')
  const [loading, setLoading] = useState(true)
  const [uploading, setUploading] = useState(false)
  const [dragOver, setDragOver] = useState(false)

  useEffect(() => {
    fetchResourcesData()
  }, [selectedCourse])

  const fetchResourcesData = async () => {
    try {
      // Mock data - replace with actual API calls
      const mockCourses: Course[] = [
        { id: '1', name: 'Advanced Mathematics', code: 'MATH301' },
        { id: '2', name: 'Physics Fundamentals', code: 'PHY101' },
        { id: '3', name: 'Chemistry Basics', code: 'CHEM100' },
        { id: '4', name: 'Biology Essentials', code: 'BIO150' }
      ]

      const mockResources: Resource[] = [
        {
          id: '1',
          name: 'Calculus Chapter 1 - Limits.pdf',
          type: 'document',
          size: 2450000,
          course_id: '1',
          course_name: 'Advanced Mathematics',
          uploaded_at: '2024-01-15T10:00:00Z',
          download_count: 45,
          file_url: '/resources/calculus-ch1.pdf'
        },
        {
          id: '2',
          name: 'Physics Laws Presentation.pptx',
          type: 'document',
          size: 8750000,
          course_id: '2',
          course_name: 'Physics Fundamentals',
          uploaded_at: '2024-01-14T14:30:00Z',
          download_count: 32,
          file_url: '/resources/physics-laws.pptx'
        },
        {
          id: '3',
          name: 'Chemical Reactions Video.mp4',
          type: 'video',
          size: 156000000,
          course_id: '3',
          course_name: 'Chemistry Basics',
          uploaded_at: '2024-01-13T09:15:00Z',
          download_count: 28,
          file_url: '/resources/chem-reactions.mp4'
        },
        {
          id: '4',
          name: 'Cell Structure Diagram.png',
          type: 'image',
          size: 1200000,
          course_id: '4',
          course_name: 'Biology Essentials',
          uploaded_at: '2024-01-12T16:45:00Z',
          download_count: 19,
          file_url: '/resources/cell-structure.png'
        }
      ]

      setCourses(mockCourses)
      setResources(mockResources)
      setLoading(false)
    } catch (error) {
      console.error('Error fetching resources:', error)
      setLoading(false)
    }
  }

  const handleFileUpload = async (files: FileList) => {
    if (!files.length || selectedCourse === 'all') return

    setUploading(true)
    try {
      // Mock upload - replace with actual API call
      const file = files[0]
      const newResource: Resource = {
        id: Date.now().toString(),
        name: file.name,
        type: getFileType(file.type),
        size: file.size,
        course_id: selectedCourse,
        course_name: courses.find(c => c.id === selectedCourse)?.name || '',
        uploaded_at: new Date().toISOString(),
        download_count: 0,
        file_url: URL.createObjectURL(file)
      }

      // Simulate upload delay
      await new Promise(resolve => setTimeout(resolve, 2000))

      setResources(prev => [newResource, ...prev])
      setUploading(false)
    } catch (error) {
      console.error('Error uploading file:', error)
      setUploading(false)
    }
  }

  const getFileType = (mimeType: string): 'document' | 'image' | 'video' | 'audio' | 'other' => {
    if (mimeType.startsWith('image/')) return 'image'
    if (mimeType.startsWith('video/')) return 'video'
    if (mimeType.startsWith('audio/')) return 'audio'
    if (mimeType.includes('pdf') || mimeType.includes('document') || mimeType.includes('text')) return 'document'
    return 'other'
  }

  const getFileIcon = (type: string) => {
    switch (type) {
      case 'document':
        return <DocumentTextIcon className="w-8 h-8 text-blue-600" />
      case 'image':
        return <PhotoIcon className="w-8 h-8 text-green-600" />
      case 'video':
        return <VideoCameraIcon className="w-8 h-8 text-purple-600" />
      default:
        return <DocumentTextIcon className="w-8 h-8 text-gray-600" />
    }
  }

  const formatFileSize = (bytes: number) => {
    const sizes = ['B', 'KB', 'MB', 'GB']
    if (bytes === 0) return '0 B'
    const i = Math.floor(Math.log(bytes) / Math.log(1024))
    return Math.round(bytes / Math.pow(1024, i) * 100) / 100 + ' ' + sizes[i]
  }

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric'
    })
  }

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault()
    setDragOver(true)
  }

  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault()
    setDragOver(false)
  }

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault()
    setDragOver(false)
    const files = e.dataTransfer.files
    if (files.length > 0) {
      handleFileUpload(files)
    }
  }

  const filteredResources = resources.filter(resource => {
    const matchesSearch = resource.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         resource.course_name.toLowerCase().includes(searchTerm.toLowerCase())
    const matchesCourse = selectedCourse === 'all' || resource.course_id === selectedCourse
    const matchesType = fileType === 'all' || resource.type === fileType
    return matchesSearch && matchesCourse && matchesType
  })

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="flex items-center justify-center h-64">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4 sm:py-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-2xl sm:text-3xl font-bold text-gray-900">Course Resources</h1>
          <p className="text-gray-600 mt-1">Upload and manage learning materials for your courses</p>
        </div>

        {/* Upload Section */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="bg-white rounded-xl shadow-soft border border-gray-200 p-6 mb-8"
        >
          <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between mb-6 gap-4">
            <h2 className="text-xl font-bold text-gray-900">Upload New Resource</h2>
            <select
              value={selectedCourse}
              onChange={(e) => setSelectedCourse(e.target.value)}
              className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
              required
            >
              <option value="all">Select Course</option>
              {courses.map((course) => (
                <option key={course.id} value={course.id}>
                  {course.name} ({course.code})
                </option>
              ))}
            </select>
          </div>

          <div
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
            onDrop={handleDrop}
            className={`border-2 border-dashed rounded-lg p-8 text-center transition-colors ${
              dragOver ? 'border-primary-400 bg-primary-50' : 'border-gray-300'
            }`}
          >
            {uploading ? (
              <div className="flex flex-col items-center">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mb-4"></div>
                <p className="text-gray-600">Uploading file...</p>
              </div>
            ) : (
              <div className="flex flex-col items-center">
                <CloudArrowUpIcon className="w-12 h-12 text-gray-400 mb-4" />
                <p className="text-lg font-medium text-gray-900 mb-2">
                  Drag and drop files here, or click to select
                </p>
                <p className="text-sm text-gray-600 mb-4">
                  Supports PDF, DOCX, PPTX, images, videos, and more
                </p>
                <input
                  type="file"
                  multiple
                  onChange={(e) => e.target.files && handleFileUpload(e.target.files)}
                  className="hidden"
                  id="file-upload"
                  disabled={selectedCourse === 'all'}
                />
                <label
                  htmlFor="file-upload"
                  className={`btn-primary cursor-pointer ${
                    selectedCourse === 'all' ? 'opacity-50 cursor-not-allowed' : ''
                  }`}
                >
                  <PlusIcon className="w-5 h-5 mr-2" />
                  Choose Files
                </label>
                {selectedCourse === 'all' && (
                  <p className="text-sm text-red-600 mt-2">Please select a course first</p>
                )}
              </div>
            )}
          </div>
        </motion.div>

        {/* Filters */}
        <div className="flex flex-col sm:flex-row gap-4 mb-6">
          <div className="relative flex-1">
            <MagnifyingGlassIcon className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
            <input
              type="text"
              placeholder="Search resources..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="pl-10 pr-4 py-2 w-full border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
            />
          </div>
          <select
            value={selectedCourse}
            onChange={(e) => setSelectedCourse(e.target.value)}
            className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
          >
            <option value="all">All Courses</option>
            {courses.map((course) => (
              <option key={course.id} value={course.id}>
                {course.name}
              </option>
            ))}
          </select>
          <select
            value={fileType}
            onChange={(e) => setFileType(e.target.value)}
            className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
          >
            <option value="all">All Types</option>
            <option value="document">Documents</option>
            <option value="image">Images</option>
            <option value="video">Videos</option>
            <option value="audio">Audio</option>
          </select>
        </div>

        {/* Resources List */}
        <div className="space-y-4">
          {filteredResources.map((resource, index) => (
            <motion.div
              key={resource.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.1 }}
              className="bg-white rounded-xl shadow-soft border border-gray-200 p-6 hover:shadow-strong transition-shadow duration-200"
            >
              <div className="flex flex-col sm:flex-row sm:items-center gap-4">
                <div className="flex items-center space-x-4 flex-1">
                  <div className="flex-shrink-0">
                    {getFileIcon(resource.type)}
                  </div>
                  <div className="min-w-0 flex-1">
                    <h3 className="text-lg font-semibold text-gray-900 truncate">{resource.name}</h3>
                    <div className="flex flex-wrap items-center gap-4 text-sm text-gray-500 mt-1">
                      <span className="flex items-center gap-1">
                        <FolderIcon className="w-4 h-4" />
                        {resource.course_name}
                      </span>
                      <span>{formatFileSize(resource.size)}</span>
                      <span>Uploaded {formatDate(resource.uploaded_at)}</span>
                      <span>{resource.download_count} downloads</span>
                    </div>
                  </div>
                </div>
                
                <div className="flex items-center gap-2">
                  <button className="flex items-center gap-1 px-3 py-1.5 text-sm bg-primary-100 text-primary-700 rounded-lg hover:bg-primary-200 transition-colors">
                    <EyeIcon className="w-4 h-4" />
                    <span className="hidden sm:inline">Preview</span>
                  </button>
                  <button className="flex items-center gap-1 px-3 py-1.5 text-sm bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors">
                    <ArrowDownTrayIcon className="w-4 h-4" />
                    <span className="hidden sm:inline">Download</span>
                  </button>
                  <button className="flex items-center gap-1 px-3 py-1.5 text-sm bg-red-100 text-red-700 rounded-lg hover:bg-red-200 transition-colors">
                    <TrashIcon className="w-4 h-4" />
                    <span className="hidden sm:inline">Delete</span>
                  </button>
                </div>
              </div>
            </motion.div>
          ))}
        </div>

        {filteredResources.length === 0 && (
          <div className="text-center py-12">
            <DocumentTextIcon className="w-12 h-12 sm:w-16 sm:h-16 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">No resources found</h3>
            <p className="text-gray-600 mb-4 text-sm sm:text-base">
              {searchTerm || selectedCourse !== 'all' || fileType !== 'all'
                ? 'Try adjusting your search or filter criteria'
                : 'Upload your first resource to get started'}
            </p>
          </div>
        )}
      </div>
    </div>
  )
}
