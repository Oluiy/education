'use client'

import { useState, useEffect, useRef } from 'react'
import { motion } from 'framer-motion'
import { useAuth } from '@/contexts/AuthContext'
import { useToast } from '@/contexts/ToastContext'
import {
  PlayIcon,
  PauseIcon,
  BookmarkIcon,
  ChatBubbleLeftIcon,
  AcademicCapIcon,
  DocumentTextIcon,
  VideoCameraIcon,
  MicrophoneIcon,
  PhotoIcon,
  FolderIcon,
  MagnifyingGlassIcon,
  AdjustmentsHorizontalIcon,
  ShareIcon,
  HeartIcon,
  EyeIcon,
  ClockIcon,
  StarIcon,
  PlusIcon,
  XMarkIcon,
  ForwardIcon,
  BackwardIcon,
  SpeakerWaveIcon,
  SpeakerXMarkIcon
} from '@heroicons/react/24/outline'
import {
  PlayIcon as PlayIconSolid,
  PauseIcon as PauseIconSolid,
  BookmarkIcon as BookmarkIconSolid,
  HeartIcon as HeartIconSolid,
  StarIcon as StarIconSolid
} from '@heroicons/react/24/solid'

interface MediaContent {
  id: number
  title: string
  description: string
  type: 'video' | 'audio' | 'document' | 'image'
  url: string
  thumbnail?: string
  duration?: number
  size: number
  subjectId: number
  subjectName: string
  teacherId: number
  teacherName: string
  uploadDate: string
  tags: string[]
  isBookmarked: boolean
  isLiked: boolean
  rating: number
  views: number
  downloadCount: number
}

interface Bookmark {
  id: number
  contentId: number
  timestamp: number
  note: string
  createdAt: string
}

interface Note {
  id: number
  contentId: number
  timestamp: number
  content: string
  createdAt: string
  updatedAt: string
}

interface PlayerState {
  isPlaying: boolean
  currentTime: number
  duration: number
  volume: number
  isMuted: boolean
  playbackRate: number
}

export default function ContentViewer() {
  const { user } = useAuth()
  const { success, error } = useToast()
  const videoRef = useRef<HTMLVideoElement>(null)
  const audioRef = useRef<HTMLAudioElement>(null)
  
  const [activeTab, setActiveTab] = useState('library')
  const [isLoading, setIsLoading] = useState(true)
  const [mediaContent, setMediaContent] = useState<MediaContent[]>([])
  const [filteredContent, setFilteredContent] = useState<MediaContent[]>([])
  const [selectedContent, setSelectedContent] = useState<MediaContent | null>(null)
  const [bookmarks, setBookmarks] = useState<Bookmark[]>([])
  const [notes, setNotes] = useState<Note[]>([])
  const [searchTerm, setSearchTerm] = useState('')
  const [filterType, setFilterType] = useState('all')
  const [filterSubject, setFilterSubject] = useState('all')
  const [sortBy, setSortBy] = useState('recent')
  const [playerState, setPlayerState] = useState<PlayerState>({
    isPlaying: false,
    currentTime: 0,
    duration: 0,
    volume: 1,
    isMuted: false,
    playbackRate: 1
  })
  const [newNote, setNewNote] = useState('')
  const [showNoteModal, setShowNoteModal] = useState(false)
  const [currentNoteTimestamp, setCurrentNoteTimestamp] = useState(0)

  // Load content library
  useEffect(() => {
    const loadContent = async () => {
      try {
        setIsLoading(true)
        
        // Mock data - replace with actual API calls
        const content: MediaContent[] = [
          {
            id: 1,
            title: 'Introduction to Calculus',
            description: 'Basic concepts of differential and integral calculus',
            type: 'video',
            url: '/videos/calculus-intro.mp4',
            thumbnail: '/thumbnails/calculus.jpg',
            duration: 3600,
            size: 156780000,
            subjectId: 1,
            subjectName: 'Mathematics',
            teacherId: 1,
            teacherName: 'Dr. Johnson',
            uploadDate: '2024-01-15',
            tags: ['calculus', 'mathematics', 'differentiation', 'integration'],
            isBookmarked: true,
            isLiked: false,
            rating: 4.8,
            views: 245,
            downloadCount: 56
          },
          {
            id: 2,
            title: 'Photosynthesis Process',
            description: 'How plants convert sunlight into energy',
            type: 'video',
            url: '/videos/photosynthesis.mp4',
            thumbnail: '/thumbnails/biology.jpg',
            duration: 2400,
            size: 98540000,
            subjectId: 2,
            subjectName: 'Biology',
            teacherId: 2,
            teacherName: 'Prof. Smith',
            uploadDate: '2024-01-14',
            tags: ['biology', 'plants', 'photosynthesis', 'energy'],
            isBookmarked: false,
            isLiked: true,
            rating: 4.6,
            views: 189,
            downloadCount: 32
          },
          {
            id: 3,
            title: 'Shakespeare Sonnets Analysis',
            description: 'Deep dive into Shakespearean poetry structure',
            type: 'audio',
            url: '/audio/shakespeare-analysis.mp3',
            duration: 1800,
            size: 25600000,
            subjectId: 3,
            subjectName: 'English Literature',
            teacherId: 3,
            teacherName: 'Ms. Brown',
            uploadDate: '2024-01-13',
            tags: ['literature', 'shakespeare', 'poetry', 'analysis'],
            isBookmarked: true,
            isLiked: true,
            rating: 4.9,
            views: 156,
            downloadCount: 78
          }
        ]

        setMediaContent(content)
        setFilteredContent(content)

        // Mock bookmarks and notes
        setBookmarks([
          {
            id: 1,
            contentId: 1,
            timestamp: 900,
            note: 'Important derivative rules explanation',
            createdAt: '2024-01-16'
          }
        ])

        setNotes([
          {
            id: 1,
            contentId: 1,
            timestamp: 1200,
            content: 'Remember: d/dx(x^n) = nx^(n-1)',
            createdAt: '2024-01-16',
            updatedAt: '2024-01-16'
          }
        ])

      } catch (err) {
        console.error('Failed to load content:', err)
        error('Failed to load media content')
      } finally {
        setIsLoading(false)
      }
    }

    loadContent()
  }, [error])

  // Filter and search content
  useEffect(() => {
    let filtered = mediaContent

    // Apply search filter
    if (searchTerm) {
      filtered = filtered.filter(content =>
        content.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
        content.description.toLowerCase().includes(searchTerm.toLowerCase()) ||
        content.tags.some(tag => tag.toLowerCase().includes(searchTerm.toLowerCase())) ||
        content.teacherName.toLowerCase().includes(searchTerm.toLowerCase()) ||
        content.subjectName.toLowerCase().includes(searchTerm.toLowerCase())
      )
    }

    // Apply type filter
    if (filterType !== 'all') {
      filtered = filtered.filter(content => content.type === filterType)
    }

    // Apply subject filter
    if (filterSubject !== 'all') {
      filtered = filtered.filter(content => content.subjectName === filterSubject)
    }

    // Apply sorting
    switch (sortBy) {
      case 'recent':
        filtered.sort((a, b) => new Date(b.uploadDate).getTime() - new Date(a.uploadDate).getTime())
        break
      case 'title':
        filtered.sort((a, b) => a.title.localeCompare(b.title))
        break
      case 'rating':
        filtered.sort((a, b) => b.rating - a.rating)
        break
      case 'views':
        filtered.sort((a, b) => b.views - a.views)
        break
    }

    setFilteredContent(filtered)
  }, [mediaContent, searchTerm, filterType, filterSubject, sortBy])

  const formatDuration = (seconds: number) => {
    const hours = Math.floor(seconds / 3600)
    const minutes = Math.floor((seconds % 3600) / 60)
    const secs = seconds % 60

    if (hours > 0) {
      return `${hours}:${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`
    }
    return `${minutes}:${secs.toString().padStart(2, '0')}`
  }

  const formatFileSize = (bytes: number) => {
    const sizes = ['Bytes', 'KB', 'MB', 'GB']
    if (bytes === 0) return '0 Bytes'
    const i = Math.floor(Math.log(bytes) / Math.log(1024))
    return Math.round(bytes / Math.pow(1024, i) * 100) / 100 + ' ' + sizes[i]
  }

  const toggleBookmark = async (contentId: number) => {
    try {
      const content = mediaContent.find(c => c.id === contentId)
      if (!content) return

      const updatedContent = mediaContent.map(c =>
        c.id === contentId ? { ...c, isBookmarked: !c.isBookmarked } : c
      )
      setMediaContent(updatedContent)

      if (content.isBookmarked) {
        success('Bookmark removed')
      } else {
        success('Bookmark added')
      }
    } catch (err) {
      error('Failed to toggle bookmark')
    }
  }

  const toggleLike = async (contentId: number) => {
    try {
      const content = mediaContent.find(c => c.id === contentId)
      if (!content) return

      const updatedContent = mediaContent.map(c =>
        c.id === contentId ? { ...c, isLiked: !c.isLiked } : c
      )
      setMediaContent(updatedContent)

      if (content.isLiked) {
        success('Like removed')
      } else {
        success('Content liked')
      }
    } catch (err) {
      error('Failed to toggle like')
    }
  }

  const playContent = (content: MediaContent) => {
    setSelectedContent(content)
    setPlayerState(prev => ({ ...prev, isPlaying: true }))
  }

  const togglePlayPause = () => {
    if (selectedContent?.type === 'video' && videoRef.current) {
      if (playerState.isPlaying) {
        videoRef.current.pause()
      } else {
        videoRef.current.play()
      }
    } else if (selectedContent?.type === 'audio' && audioRef.current) {
      if (playerState.isPlaying) {
        audioRef.current.pause()
      } else {
        audioRef.current.play()
      }
    }
    setPlayerState(prev => ({ ...prev, isPlaying: !prev.isPlaying }))
  }

  const addBookmark = () => {
    if (!selectedContent) return

    const timestamp = Math.floor(playerState.currentTime)
    const newBookmark: Bookmark = {
      id: Date.now(),
      contentId: selectedContent.id,
      timestamp,
      note: `Bookmark at ${formatDuration(timestamp)}`,
      createdAt: new Date().toISOString()
    }

    setBookmarks(prev => [...prev, newBookmark])
    success('Bookmark added')
  }

  const addNote = () => {
    if (!selectedContent || !newNote.trim()) return

    const note: Note = {
      id: Date.now(),
      contentId: selectedContent.id,
      timestamp: currentNoteTimestamp,
      content: newNote,
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString()
    }

    setNotes(prev => [...prev, note])
    setNewNote('')
    setShowNoteModal(false)
    success('Note added')
  }

  const getTypeIcon = (type: string) => {
    switch (type) {
      case 'video':
        return VideoCameraIcon
      case 'audio':
        return MicrophoneIcon
      case 'document':
        return DocumentTextIcon
      case 'image':
        return PhotoIcon
      default:
        return DocumentTextIcon
    }
  }

  const renderLibrary = () => (
    <div className="space-y-6">
      {/* Search and Filters */}
      <div className="bg-white rounded-lg shadow p-6">
        <div className="flex flex-col lg:flex-row gap-4">
          <div className="flex-1">
            <div className="relative">
              <MagnifyingGlassIcon className="w-5 h-5 absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" />
              <input
                type="text"
                placeholder="Search content..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              />
            </div>
          </div>
          <div className="flex gap-3">
            <select
              value={filterType}
              onChange={(e) => setFilterType(e.target.value)}
              className="px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            >
              <option value="all">All Types</option>
              <option value="video">Videos</option>
              <option value="audio">Audio</option>
              <option value="document">Documents</option>
              <option value="image">Images</option>
            </select>
            <select
              value={filterSubject}
              onChange={(e) => setFilterSubject(e.target.value)}
              className="px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            >
              <option value="all">All Subjects</option>
              <option value="Mathematics">Mathematics</option>
              <option value="Biology">Biology</option>
              <option value="English Literature">English Literature</option>
            </select>
            <select
              value={sortBy}
              onChange={(e) => setSortBy(e.target.value)}
              className="px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            >
              <option value="recent">Most Recent</option>
              <option value="title">Title</option>
              <option value="rating">Highest Rated</option>
              <option value="views">Most Viewed</option>
            </select>
          </div>
        </div>
      </div>

      {/* Content Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
        {filteredContent.map((content) => {
          const TypeIcon = getTypeIcon(content.type)
          return (
            <motion.div
              key={content.id}
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              className="bg-white rounded-lg shadow overflow-hidden hover:shadow-lg transition-shadow"
            >
              {/* Thumbnail */}
              <div className="relative h-48 bg-gray-200">
                {content.thumbnail ? (
                  <img
                    src={content.thumbnail}
                    alt={content.title}
                    className="w-full h-full object-cover"
                  />
                ) : (
                  <div className="w-full h-full flex items-center justify-center">
                    <TypeIcon className="w-16 h-16 text-gray-400" />
                  </div>
                )}
                
                {/* Duration overlay */}
                {content.duration && (
                  <div className="absolute bottom-2 right-2 bg-black bg-opacity-75 text-white text-xs px-2 py-1 rounded">
                    {formatDuration(content.duration)}
                  </div>
                )}
                
                {/* Play button overlay */}
                <div className="absolute inset-0 flex items-center justify-center opacity-0 hover:opacity-100 transition-opacity bg-black bg-opacity-50">
                  <button
                    onClick={() => playContent(content)}
                    className="bg-blue-600 text-white p-3 rounded-full hover:bg-blue-700"
                  >
                    <PlayIcon className="w-6 h-6" />
                  </button>
                </div>
              </div>

              {/* Content Info */}
              <div className="p-4">
                <div className="flex items-start justify-between mb-2">
                  <h3 className="font-semibold text-gray-900 line-clamp-2">{content.title}</h3>
                  <div className="flex space-x-1 ml-2">
                    <button
                      onClick={() => toggleBookmark(content.id)}
                      className="text-gray-400 hover:text-blue-600"
                    >
                      {content.isBookmarked ? (
                        <BookmarkIconSolid className="w-5 h-5 text-blue-600" />
                      ) : (
                        <BookmarkIcon className="w-5 h-5" />
                      )}
                    </button>
                    <button
                      onClick={() => toggleLike(content.id)}
                      className="text-gray-400 hover:text-red-600"
                    >
                      {content.isLiked ? (
                        <HeartIconSolid className="w-5 h-5 text-red-600" />
                      ) : (
                        <HeartIcon className="w-5 h-5" />
                      )}
                    </button>
                  </div>
                </div>
                
                <p className="text-sm text-gray-600 mb-3 line-clamp-2">{content.description}</p>
                
                <div className="flex items-center justify-between text-sm text-gray-500 mb-3">
                  <span>{content.teacherName}</span>
                  <span>{content.subjectName}</span>
                </div>
                
                <div className="flex items-center justify-between text-xs text-gray-400">
                  <div className="flex items-center space-x-2">
                    <div className="flex items-center">
                      <StarIcon className="w-4 h-4 text-yellow-400 mr-1" />
                      <span>{content.rating}</span>
                    </div>
                    <div className="flex items-center">
                      <EyeIcon className="w-4 h-4 mr-1" />
                      <span>{content.views}</span>
                    </div>
                  </div>
                  <span>{formatFileSize(content.size)}</span>
                </div>
              </div>
            </motion.div>
          )
        })}
      </div>
    </div>
  )

  const renderPlayer = () => {
    if (!selectedContent) {
      return (
        <div className="flex items-center justify-center h-96 bg-gray-100 rounded-lg">
          <div className="text-center">
            <VideoCameraIcon className="w-16 h-16 text-gray-400 mx-auto mb-4" />
            <p className="text-gray-600">Select content to start viewing</p>
          </div>
        </div>
      )
    }

    return (
      <div className="space-y-6">
        {/* Player Container */}
        <div className="bg-white rounded-lg shadow overflow-hidden">
          {/* Video/Audio Player */}
          <div className="relative">
            {selectedContent.type === 'video' ? (
              <video
                ref={videoRef}
                src={selectedContent.url}
                className="w-full h-96 object-contain bg-black"
                onTimeUpdate={(e) => {
                  const target = e.target as HTMLVideoElement
                  setPlayerState(prev => ({
                    ...prev,
                    currentTime: target.currentTime,
                    duration: target.duration
                  }))
                }}
                onLoadedMetadata={(e) => {
                  const target = e.target as HTMLVideoElement
                  setPlayerState(prev => ({ ...prev, duration: target.duration }))
                }}
              />
            ) : selectedContent.type === 'audio' ? (
              <div className="h-96 bg-gradient-to-br from-blue-900 to-purple-900 flex items-center justify-center">
                <audio
                  ref={audioRef}
                  src={selectedContent.url}
                  onTimeUpdate={(e) => {
                    const target = e.target as HTMLAudioElement
                    setPlayerState(prev => ({
                      ...prev,
                      currentTime: target.currentTime,
                      duration: target.duration
                    }))
                  }}
                  onLoadedMetadata={(e) => {
                    const target = e.target as HTMLAudioElement
                    setPlayerState(prev => ({ ...prev, duration: target.duration }))
                  }}
                />
                <div className="text-center text-white">
                  <MicrophoneIcon className="w-24 h-24 mx-auto mb-4" />
                  <h3 className="text-xl font-semibold">{selectedContent.title}</h3>
                  <p className="text-blue-200">{selectedContent.teacherName}</p>
                </div>
              </div>
            ) : (
              <div className="h-96 bg-gray-100 flex items-center justify-center">
                <p className="text-gray-600">Content type not supported in player</p>
              </div>
            )}

            {/* Player Controls Overlay */}
            <div className="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-black to-transparent p-4">
              <div className="flex items-center space-x-4 text-white">
                <button
                  onClick={togglePlayPause}
                  className="p-2 bg-blue-600 rounded-full hover:bg-blue-700"
                >
                  {playerState.isPlaying ? (
                    <PauseIconSolid className="w-6 h-6" />
                  ) : (
                    <PlayIconSolid className="w-6 h-6" />
                  )}
                </button>
                
                <button onClick={addBookmark} className="p-2 hover:bg-white hover:bg-opacity-20 rounded">
                  <BookmarkIcon className="w-5 h-5" />
                </button>
                
                <button
                  onClick={() => {
                    setCurrentNoteTimestamp(Math.floor(playerState.currentTime))
                    setShowNoteModal(true)
                  }}
                  className="p-2 hover:bg-white hover:bg-opacity-20 rounded"
                >
                  <ChatBubbleLeftIcon className="w-5 h-5" />
                </button>
                
                <div className="flex-1">
                  <div className="text-sm mb-1">
                    {formatDuration(Math.floor(playerState.currentTime))} / {formatDuration(Math.floor(playerState.duration))}
                  </div>
                  <div className="w-full bg-gray-600 rounded-full h-2">
                    <div
                      className="bg-blue-600 h-2 rounded-full"
                      style={{
                        width: `${(playerState.currentTime / playerState.duration) * 100}%`
                      }}
                    />
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Content Info */}
          <div className="p-6">
            <div className="flex justify-between items-start mb-4">
              <div>
                <h2 className="text-2xl font-bold text-gray-900">{selectedContent.title}</h2>
                <p className="text-gray-600 mt-2">{selectedContent.description}</p>
              </div>
              <div className="flex space-x-2">
                <button
                  onClick={() => toggleBookmark(selectedContent.id)}
                  className="p-2 text-gray-400 hover:text-blue-600"
                >
                  {selectedContent.isBookmarked ? (
                    <BookmarkIconSolid className="w-6 h-6 text-blue-600" />
                  ) : (
                    <BookmarkIcon className="w-6 h-6" />
                  )}
                </button>
                <button
                  onClick={() => toggleLike(selectedContent.id)}
                  className="p-2 text-gray-400 hover:text-red-600"
                >
                  {selectedContent.isLiked ? (
                    <HeartIconSolid className="w-6 h-6 text-red-600" />
                  ) : (
                    <HeartIcon className="w-6 h-6" />
                  )}
                </button>
                <button className="p-2 text-gray-400 hover:text-blue-600">
                  <ShareIcon className="w-6 h-6" />
                </button>
              </div>
            </div>
            
            <div className="flex items-center justify-between text-sm text-gray-600">
              <div className="flex items-center space-x-4">
                <span>{selectedContent.teacherName}</span>
                <span>{selectedContent.subjectName}</span>
                <div className="flex items-center">
                  <StarIcon className="w-4 h-4 text-yellow-400 mr-1" />
                  <span>{selectedContent.rating}</span>
                </div>
              </div>
              <div className="flex items-center space-x-4">
                <div className="flex items-center">
                  <EyeIcon className="w-4 h-4 mr-1" />
                  <span>{selectedContent.views} views</span>
                </div>
                <span>{formatFileSize(selectedContent.size)}</span>
              </div>
            </div>
          </div>
        </div>

        {/* Bookmarks and Notes */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Bookmarks */}
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-semibold mb-4">Bookmarks</h3>
            <div className="space-y-3">
              {bookmarks
                .filter(bookmark => bookmark.contentId === selectedContent.id)
                .map((bookmark) => (
                  <div key={bookmark.id} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                    <div>
                      <p className="font-medium">{formatDuration(bookmark.timestamp)}</p>
                      <p className="text-sm text-gray-600">{bookmark.note}</p>
                    </div>
                    <button
                      onClick={() => {
                        // Jump to bookmark timestamp
                        if (selectedContent.type === 'video' && videoRef.current) {
                          videoRef.current.currentTime = bookmark.timestamp
                        } else if (selectedContent.type === 'audio' && audioRef.current) {
                          audioRef.current.currentTime = bookmark.timestamp
                        }
                      }}
                      className="text-blue-600 hover:text-blue-800"
                    >
                      <PlayIcon className="w-4 h-4" />
                    </button>
                  </div>
                ))}
              {bookmarks.filter(b => b.contentId === selectedContent.id).length === 0 && (
                <p className="text-gray-500 text-center py-4">No bookmarks yet</p>
              )}
            </div>
          </div>

          {/* Notes */}
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-semibold mb-4">Notes</h3>
            <div className="space-y-3">
              {notes
                .filter(note => note.contentId === selectedContent.id)
                .map((note) => (
                  <div key={note.id} className="p-3 bg-gray-50 rounded-lg">
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-sm font-medium text-blue-600">
                        {formatDuration(note.timestamp)}
                      </span>
                      <span className="text-xs text-gray-500">
                        {new Date(note.createdAt).toLocaleDateString()}
                      </span>
                    </div>
                    <p className="text-sm text-gray-700">{note.content}</p>
                  </div>
                ))}
              {notes.filter(n => n.contentId === selectedContent.id).length === 0 && (
                <p className="text-gray-500 text-center py-4">No notes yet</p>
              )}
            </div>
          </div>
        </div>
      </div>
    )
  }

  const renderBookmarks = () => (
    <div className="space-y-6">
      <div className="bg-white rounded-lg shadow">
        <div className="p-6 border-b border-gray-200">
          <h3 className="text-lg font-semibold">My Bookmarks</h3>
        </div>
        <div className="p-6">
          <div className="space-y-4">
            {bookmarks.map((bookmark) => {
              const content = mediaContent.find(c => c.id === bookmark.contentId)
              if (!content) return null
              
              return (
                <div key={bookmark.id} className="flex items-center justify-between p-4 border border-gray-200 rounded-lg">
                  <div className="flex items-center">
                    <div className="w-16 h-16 bg-gray-200 rounded-lg flex items-center justify-center mr-4">
                      {content.thumbnail ? (
                        <img src={content.thumbnail} alt={content.title} className="w-full h-full object-cover rounded-lg" />
                      ) : (
                        <VideoCameraIcon className="w-8 h-8 text-gray-400" />
                      )}
                    </div>
                    <div>
                      <h4 className="font-medium">{content.title}</h4>
                      <p className="text-sm text-gray-600">{bookmark.note}</p>
                      <p className="text-xs text-gray-500">
                        At {formatDuration(bookmark.timestamp)} • {new Date(bookmark.createdAt).toLocaleDateString()}
                      </p>
                    </div>
                  </div>
                  <button
                    onClick={() => {
                      playContent(content)
                      // Jump to bookmark timestamp after a brief delay
                      setTimeout(() => {
                        if (content.type === 'video' && videoRef.current) {
                          videoRef.current.currentTime = bookmark.timestamp
                        } else if (content.type === 'audio' && audioRef.current) {
                          audioRef.current.currentTime = bookmark.timestamp
                        }
                      }, 100)
                    }}
                    className="flex items-center px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
                  >
                    <PlayIcon className="w-4 h-4 mr-2" />
                    Play
                  </button>
                </div>
              )
            })}
            {bookmarks.length === 0 && (
              <div className="text-center py-8">
                <BookmarkIcon className="w-16 h-16 text-gray-300 mx-auto mb-4" />
                <p className="text-gray-500">No bookmarks yet</p>
                <p className="text-sm text-gray-400">Start watching content and add bookmarks at important moments</p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  )

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading content...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 py-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Content Viewer</h1>
          <p className="text-gray-600 mt-2">Watch videos, listen to audio, and manage your learning materials</p>
        </div>

        {/* Navigation Tabs */}
        <div className="border-b border-gray-200 mb-8">
          <nav className="-mb-px flex space-x-8">
            {[
              { id: 'library', name: 'Library', icon: FolderIcon },
              { id: 'player', name: 'Player', icon: PlayIcon },
              { id: 'bookmarks', name: 'Bookmarks', icon: BookmarkIcon },
            ].map((tab) => {
              const Icon = tab.icon
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`flex items-center py-2 px-1 border-b-2 font-medium text-sm ${
                    activeTab === tab.id
                      ? 'border-blue-500 text-blue-600'
                      : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                  }`}
                >
                  <Icon className="w-5 h-5 mr-2" />
                  {tab.name}
                </button>
              )
            })}
          </nav>
        </div>

        {/* Tab Content */}
        <motion.div
          key={activeTab}
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.2 }}
        >
          {activeTab === 'library' && renderLibrary()}
          {activeTab === 'player' && renderPlayer()}
          {activeTab === 'bookmarks' && renderBookmarks()}
        </motion.div>

        {/* Note Modal */}
        {showNoteModal && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
            <div className="bg-white rounded-lg p-6 w-full max-w-md">
              <div className="flex justify-between items-center mb-4">
                <h3 className="text-lg font-semibold">Add Note</h3>
                <button
                  onClick={() => setShowNoteModal(false)}
                  className="text-gray-400 hover:text-gray-600"
                >
                  <XMarkIcon className="w-6 h-6" />
                </button>
              </div>
              <div className="mb-4">
                <p className="text-sm text-gray-600 mb-2">
                  Timestamp: {formatDuration(currentNoteTimestamp)}
                </p>
                <textarea
                  value={newNote}
                  onChange={(e) => setNewNote(e.target.value)}
                  placeholder="Add your note..."
                  className="w-full h-32 px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                />
              </div>
              <div className="flex justify-end space-x-3">
                <button
                  onClick={() => setShowNoteModal(false)}
                  className="px-4 py-2 text-gray-700 bg-gray-100 rounded-md hover:bg-gray-200"
                >
                  Cancel
                </button>
                <button
                  onClick={addNote}
                  disabled={!newNote.trim()}
                  className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  Add Note
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
