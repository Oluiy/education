'use client'

import { useState, useEffect } from 'react'
import { 
  DocumentTextIcon, 
  PhotoIcon, 
  FilmIcon,
  MusicalNoteIcon,
  ArchiveBoxIcon,
  CloudArrowUpIcon,
  ShareIcon,
  TrashIcon,
  EyeIcon,
  ArrowDownTrayIcon,
  MagnifyingGlassIcon,
  FunnelIcon,
  PlusIcon,
  FolderIcon,
  DocumentIcon
} from '@heroicons/react/24/outline'
import api from '@/lib/api'

interface FileItem {
  id: string
  filename: string
  original_filename: string
  file_type: string
  file_size: number
  description?: string
  tags: string[]
  created_at: string
  updated_at: string
  download_count: number
  is_shared: boolean
  shared_with_count: number
}

interface FileCollection {
  id: string
  name: string
  description: string
  file_count: number
  total_size: number
  created_at: string
}

interface StorageQuota {
  used_bytes: number
  total_bytes: number
  file_count: number
  max_files: number
}

const FileIcon = ({ fileType, className = "w-6 h-6" }: { fileType: string; className?: string }) => {
  switch (fileType.toLowerCase()) {
    case 'pdf':
    case 'doc':
    case 'docx':
    case 'txt':
      return <DocumentTextIcon className={className} />
    case 'jpg':
    case 'jpeg':
    case 'png':
    case 'gif':
    case 'webp':
      return <PhotoIcon className={className} />
    case 'mp4':
    case 'avi':
    case 'mov':
    case 'webm':
      return <FilmIcon className={className} />
    case 'mp3':
    case 'wav':
    case 'flac':
      return <MusicalNoteIcon className={className} />
    case 'zip':
    case 'rar':
    case '7z':
      return <ArchiveBoxIcon className={className} />
    default:
      return <DocumentIcon className={className} />
  }
}

const formatFileSize = (bytes: number): string => {
  if (bytes === 0) return '0 Bytes'
  const k = 1024
  const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

const formatDate = (dateString: string): string => {
  const date = new Date(dateString)
  return date.toLocaleDateString() + ' ' + date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
}

export default function FilesPage() {
  const [files, setFiles] = useState<FileItem[]>([])
  const [collections, setCollections] = useState<FileCollection[]>([])
  const [storageQuota, setStorageQuota] = useState<StorageQuota | null>(null)
  const [loading, setLoading] = useState(true)
  const [uploadProgress, setUploadProgress] = useState(0)
  const [isUploading, setIsUploading] = useState(false)

  // Filters and search
  const [searchTerm, setSearchTerm] = useState('')
  const [selectedFileType, setSelectedFileType] = useState('')
  const [selectedTags, setSelectedTags] = useState<string[]>([])
  const [currentPage, setCurrentPage] = useState(1)
  const [showFilters, setShowFilters] = useState(false)

  // Modals
  const [showUploadModal, setShowUploadModal] = useState(false)
  const [showShareModal, setShowShareModal] = useState(false)
  const [showCollectionModal, setShowCollectionModal] = useState(false)
  const [selectedFile, setSelectedFile] = useState<FileItem | null>(null)
  const [selectedFiles, setSelectedFiles] = useState<string[]>([])

  // Load data
  useEffect(() => {
    loadFiles()
    loadCollections()
    loadStorageQuota()
  }, [currentPage, searchTerm, selectedFileType, selectedTags])

  const loadFiles = async () => {
    try {
      setLoading(true)
      const response = await api.fileAPI.getFiles({
        page: currentPage,
        limit: 20,
        search: searchTerm || undefined,
        file_type: selectedFileType || undefined,
        tags: selectedTags.length > 0 ? selectedTags : undefined,
      })
      const data = await response.json()
      setFiles(data.files || [])
    } catch (error) {
      console.error('Error loading files:', error)
    } finally {
      setLoading(false)
    }
  }

  const loadCollections = async () => {
    try {
      const response = await api.fileAPI.getCollections()
      const data = await response.json()
      setCollections(data.collections || [])
    } catch (error) {
      console.error('Error loading collections:', error)
    }
  }

  const loadStorageQuota = async () => {
    try {
      const response = await api.fileAPI.getStorageQuota()
      const data = await response.json()
      setStorageQuota(data)
    } catch (error) {
      console.error('Error loading storage quota:', error)
    }
  }

  const handleFileUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0]
    if (!file) return

    try {
      setIsUploading(true)
      setUploadProgress(0)
      
      const result = await api.fileAPI.uploadFile(file, {
        description: 'Uploaded via dashboard',
        tags: ['dashboard-upload']
      })
      
      setUploadProgress(100)
      setTimeout(() => {
        setIsUploading(false)
        setUploadProgress(0)
        loadFiles()
        loadStorageQuota()
      }, 1000)
      
    } catch (error) {
      console.error('Error uploading file:', error)
      setIsUploading(false)
      setUploadProgress(0)
    }
  }

  const handleDownload = async (file: FileItem) => {
    try {
      const blob = await api.fileAPI.downloadFile(file.id)
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = file.original_filename
      document.body.appendChild(a)
      a.click()
      window.URL.revokeObjectURL(url)
      document.body.removeChild(a)
    } catch (error) {
      console.error('Error downloading file:', error)
    }
  }

  const handleDelete = async (fileId: string) => {
    if (!confirm('Are you sure you want to delete this file?')) return

    try {
      await api.fileAPI.deleteFile(fileId)
      loadFiles()
      loadStorageQuota()
    } catch (error) {
      console.error('Error deleting file:', error)
    }
  }

  const toggleFileSelection = (fileId: string) => {
    setSelectedFiles(prev => 
      prev.includes(fileId) 
        ? prev.filter(id => id !== fileId)
        : [...prev, fileId]
    )
  }

  const fileTypes = ['pdf', 'doc', 'docx', 'txt', 'jpg', 'jpeg', 'png', 'gif', 'mp4', 'avi', 'mov', 'mp3', 'wav', 'zip', 'rar']
  const allTags = Array.from(new Set(files.flatMap(file => file.tags)))

  const storageUsagePercentage = storageQuota ? (storageQuota.used_bytes / storageQuota.total_bytes) * 100 : 0

  return (
    <div className="p-6 max-w-7xl mx-auto">
      {/* Header */}
      <div className="flex justify-between items-center mb-6">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">File Management</h1>
          <p className="text-gray-600 mt-1">Upload, organize, and share your files</p>
        </div>
        <div className="flex gap-3">
          <button
            onClick={() => setShowCollectionModal(true)}
            className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
          >
            <FolderIcon className="w-5 h-5" />
            New Collection
          </button>
          <label className="flex items-center gap-2 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors cursor-pointer">
            <CloudArrowUpIcon className="w-5 h-5" />
            Upload File
            <input
              type="file"
              className="hidden"
              onChange={handleFileUpload}
              disabled={isUploading}
            />
          </label>
        </div>
      </div>

      {/* Storage Quota */}
      {storageQuota && (
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4 mb-6">
          <div className="flex items-center justify-between mb-2">
            <h3 className="text-sm font-medium text-gray-700">Storage Usage</h3>
            <span className="text-sm text-gray-500">
              {formatFileSize(storageQuota.used_bytes)} / {formatFileSize(storageQuota.total_bytes)}
            </span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div 
              className="bg-blue-600 h-2 rounded-full transition-all duration-300"
              style={{ width: `${storageUsagePercentage}%` }}
            />
          </div>
          <div className="flex justify-between text-sm text-gray-500 mt-1">
            <span>{storageQuota.file_count} files</span>
            <span>{storageUsagePercentage.toFixed(1)}% used</span>
          </div>
        </div>
      )}

      {/* Upload Progress */}
      {isUploading && (
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4 mb-6">
          <div className="flex items-center justify-between mb-2">
            <h3 className="text-sm font-medium text-gray-700">Uploading...</h3>
            <span className="text-sm text-gray-500">{uploadProgress}%</span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div 
              className="bg-green-600 h-2 rounded-full transition-all duration-300"
              style={{ width: `${uploadProgress}%` }}
            />
          </div>
        </div>
      )}

      {/* Collections */}
      {collections.length > 0 && (
        <div className="mb-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-3">Collections</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {collections.map((collection) => (
              <div key={collection.id} className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
                <div className="flex items-center gap-3 mb-2">
                  <FolderIcon className="w-6 h-6 text-blue-600" />
                  <h3 className="font-medium text-gray-900">{collection.name}</h3>
                </div>
                <p className="text-sm text-gray-600 mb-2">{collection.description}</p>
                <div className="flex items-center justify-between text-sm text-gray-500">
                  <span>{collection.file_count} files</span>
                  <span>{formatFileSize(collection.total_size)}</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Search and Filters */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4 mb-6">
        <div className="flex flex-col md:flex-row gap-4">
          <div className="flex-1 relative">
            <MagnifyingGlassIcon className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
            <input
              type="text"
              placeholder="Search files..."
              className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
            />
          </div>
          <button
            onClick={() => setShowFilters(!showFilters)}
            className="flex items-center gap-2 px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50"
          >
            <FunnelIcon className="w-5 h-5" />
            Filters
          </button>
        </div>

        {showFilters && (
          <div className="mt-4 pt-4 border-t border-gray-200">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">File Type</label>
                <select
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  value={selectedFileType}
                  onChange={(e) => setSelectedFileType(e.target.value)}
                >
                  <option value="">All Types</option>
                  {fileTypes.map(type => (
                    <option key={type} value={type}>{type.toUpperCase()}</option>
                  ))}
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Tags</label>
                <div className="flex flex-wrap gap-2">
                  {allTags.map(tag => (
                    <button
                      key={tag}
                      onClick={() => setSelectedTags(prev => 
                        prev.includes(tag) 
                          ? prev.filter(t => t !== tag)
                          : [...prev, tag]
                      )}
                      className={`px-3 py-1 rounded-full text-sm ${
                        selectedTags.includes(tag)
                          ? 'bg-blue-600 text-white'
                          : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                      }`}
                    >
                      {tag}
                    </button>
                  ))}
                </div>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Files Grid */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200">
        <div className="p-4 border-b border-gray-200">
          <div className="flex items-center justify-between">
            <h2 className="text-lg font-semibold text-gray-900">Files</h2>
            {selectedFiles.length > 0 && (
              <div className="flex items-center gap-2">
                <span className="text-sm text-gray-500">{selectedFiles.length} selected</span>
                <button
                  onClick={() => setSelectedFiles([])}
                  className="text-sm text-blue-600 hover:text-blue-700"
                >
                  Clear
                </button>
              </div>
            )}
          </div>
        </div>

        {loading ? (
          <div className="p-8 text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
            <p className="text-gray-500 mt-2">Loading files...</p>
          </div>
        ) : files.length === 0 ? (
          <div className="p-8 text-center">
            <DocumentIcon className="w-12 h-12 text-gray-400 mx-auto mb-4" />
            <p className="text-gray-500">No files found</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4 p-4">
            {files.map((file) => (
              <div
                key={file.id}
                className={`relative bg-gray-50 rounded-lg border-2 transition-all duration-200 ${
                  selectedFiles.includes(file.id)
                    ? 'border-blue-500 bg-blue-50'
                    : 'border-gray-200 hover:border-gray-300'
                }`}
              >
                <div className="p-4">
                  <div className="flex items-center justify-between mb-3">
                    <FileIcon fileType={file.file_type} className="w-8 h-8 text-gray-600" />
                    <input
                      type="checkbox"
                      checked={selectedFiles.includes(file.id)}
                      onChange={() => toggleFileSelection(file.id)}
                      className="h-4 w-4 text-blue-600 rounded border-gray-300 focus:ring-blue-500"
                    />
                  </div>
                  
                  <h3 className="font-medium text-gray-900 mb-1 truncate" title={file.original_filename}>
                    {file.original_filename}
                  </h3>
                  
                  <p className="text-sm text-gray-500 mb-2">
                    {formatFileSize(file.file_size)}
                  </p>
                  
                  {file.description && (
                    <p className="text-xs text-gray-600 mb-2 truncate">{file.description}</p>
                  )}
                  
                  <div className="flex flex-wrap gap-1 mb-3">
                    {file.tags.slice(0, 2).map(tag => (
                      <span key={tag} className="px-2 py-1 bg-gray-200 text-gray-700 text-xs rounded">
                        {tag}
                      </span>
                    ))}
                    {file.tags.length > 2 && (
                      <span className="px-2 py-1 bg-gray-200 text-gray-700 text-xs rounded">
                        +{file.tags.length - 2}
                      </span>
                    )}
                  </div>
                  
                  <div className="flex items-center justify-between text-xs text-gray-500 mb-3">
                    <span>{formatDate(file.created_at)}</span>
                    <div className="flex items-center gap-2">
                      <EyeIcon className="w-4 h-4" />
                      <span>{file.download_count}</span>
                    </div>
                  </div>
                  
                  <div className="flex items-center gap-2">
                    <button
                      onClick={() => handleDownload(file)}
                      className="flex-1 flex items-center justify-center gap-1 px-2 py-1 bg-blue-600 text-white rounded text-sm hover:bg-blue-700 transition-colors"
                    >
                      <ArrowDownTrayIcon className="w-4 h-4" />
                      Download
                    </button>
                    <button
                      onClick={() => {
                        setSelectedFile(file)
                        setShowShareModal(true)
                      }}
                      className="p-1 text-gray-600 hover:text-blue-600 transition-colors"
                    >
                      <ShareIcon className="w-4 h-4" />
                    </button>
                    <button
                      onClick={() => handleDelete(file.id)}
                      className="p-1 text-gray-600 hover:text-red-600 transition-colors"
                    >
                      <TrashIcon className="w-4 h-4" />
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Pagination */}
      <div className="flex justify-center mt-6">
        <div className="flex gap-2">
          <button
            onClick={() => setCurrentPage(prev => Math.max(1, prev - 1))}
            disabled={currentPage === 1}
            className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            Previous
          </button>
          <span className="px-4 py-2 bg-gray-100 border border-gray-300 rounded-lg">
            Page {currentPage}
          </span>
          <button
            onClick={() => setCurrentPage(prev => prev + 1)}
            className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50"
          >
            Next
          </button>
        </div>
      </div>
    </div>
  )
}
