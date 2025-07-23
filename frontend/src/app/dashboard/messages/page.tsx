'use client'

import { useState, useEffect, useRef } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import {
  PaperAirplaneIcon,
  UserIcon,
  MagnifyingGlassIcon,
  PhoneIcon,
  VideoCameraIcon,
  EllipsisVerticalIcon,
  PlusIcon,
  FaceSmileIcon,
  PaperClipIcon
} from '@heroicons/react/24/outline'
import {
  CheckIcon,
  CheckCircleIcon
} from '@heroicons/react/24/solid'

interface Message {
  id: string
  sender_id: string
  sender_name: string
  sender_avatar: string
  content: string
  timestamp: string
  type: 'text' | 'image' | 'file'
  file_url?: string
  read_by: string[]
}

interface Conversation {
  id: string
  name: string
  avatar: string
  last_message: string
  last_message_time: string
  unread_count: number
  is_online: boolean
  type: 'direct' | 'group' | 'class'
  participants: number
}

export default function MessagesPage() {
  const [conversations, setConversations] = useState<Conversation[]>([])
  const [selectedConversation, setSelectedConversation] = useState<Conversation | null>(null)
  const [messages, setMessages] = useState<Message[]>([])
  const [newMessage, setNewMessage] = useState('')
  const [loading, setLoading] = useState(true)
  const [searchTerm, setSearchTerm] = useState('')
  const messagesEndRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    fetchConversations()
  }, [])

  useEffect(() => {
    if (selectedConversation) {
      fetchMessages(selectedConversation.id)
    }
  }, [selectedConversation])

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const fetchConversations = async () => {
    try {
      // Mock data for now
      const mockConversations: Conversation[] = [
        {
          id: '1',
          name: 'Study Group - Math',
          avatar: '/api/placeholder/40/40',
          last_message: 'Can someone help with question 5?',
          last_message_time: '2024-01-15T10:30:00Z',
          unread_count: 2,
          is_online: true,
          type: 'group',
          participants: 5
        },
        {
          id: '2',
          name: 'Dr. Smith',
          avatar: '/api/placeholder/40/40',
          last_message: 'Your assignment has been graded',
          last_message_time: '2024-01-15T09:15:00Z',
          unread_count: 1,
          is_online: false,
          type: 'direct',
          participants: 2
        },
        {
          id: '3',
          name: 'Physics Class',
          avatar: '/api/placeholder/40/40',
          last_message: 'Lab results are now available',
          last_message_time: '2024-01-14T16:45:00Z',
          unread_count: 0,
          is_online: true,
          type: 'class',
          participants: 25
        }
      ]
      setConversations(mockConversations)
      setLoading(false)
      
      // Select first conversation by default
      if (mockConversations.length > 0) {
        setSelectedConversation(mockConversations[0])
      }
    } catch (error) {
      console.error('Error fetching conversations:', error)
      setLoading(false)
    }
  }

  const fetchMessages = async (conversationId: string) => {
    try {
      // Mock messages
      const mockMessages: Message[] = [
        {
          id: '1',
          sender_id: '2',
          sender_name: 'John Doe',
          sender_avatar: '/api/placeholder/32/32',
          content: 'Hey everyone! Did you finish the math homework?',
          timestamp: '2024-01-15T08:30:00Z',
          type: 'text',
          read_by: ['1', '3']
        },
        {
          id: '2',
          sender_id: '1',
          sender_name: 'You',
          sender_avatar: '/api/placeholder/32/32',
          content: 'Yes, I finished it last night. Question 5 was tricky though.',
          timestamp: '2024-01-15T08:32:00Z',
          type: 'text',
          read_by: ['2', '3']
        },
        {
          id: '3',
          sender_id: '3',
          sender_name: 'Sarah Wilson',
          sender_avatar: '/api/placeholder/32/32',
          content: 'Can someone help with question 5? I\'m stuck!',
          timestamp: '2024-01-15T10:30:00Z',
          type: 'text',
          read_by: ['1']
        }
      ]
      setMessages(mockMessages)
    } catch (error) {
      console.error('Error fetching messages:', error)
    }
  }

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  const handleSendMessage = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!newMessage.trim() || !selectedConversation) return

    const newMsg: Message = {
      id: Date.now().toString(),
      sender_id: '1',
      sender_name: 'You',
      sender_avatar: '/api/placeholder/32/32',
      content: newMessage.trim(),
      timestamp: new Date().toISOString(),
      type: 'text',
      read_by: []
    }

    setMessages(prev => [...prev, newMsg])
    setNewMessage('')
  }

  const formatTime = (timestamp: string) => {
    const date = new Date(timestamp)
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
  }

  const formatLastMessageTime = (timestamp: string) => {
    const date = new Date(timestamp)
    const now = new Date()
    const diffMs = now.getTime() - date.getTime()
    const diffMins = Math.floor(diffMs / 60000)
    const diffHours = Math.floor(diffMs / 3600000)
    const diffDays = Math.floor(diffMs / 86400000)

    if (diffMins < 1) return 'Just now'
    if (diffMins < 60) return `${diffMins}m ago`
    if (diffHours < 24) return `${diffHours}h ago`
    if (diffDays < 7) return `${diffDays}d ago`
    return date.toLocaleDateString()
  }

  const filteredConversations = conversations.filter(conversation =>
    conversation.name.toLowerCase().includes(searchTerm.toLowerCase())
  )

  const selectedConversationData = selectedConversation

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
      {/* Main Content - Centralized */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="h-[calc(100vh-8rem)] flex bg-white rounded-lg shadow-sm border border-gray-200">
          {/* Conversations Sidebar */}
          <div className="w-80 bg-white border-r border-gray-200 flex flex-col rounded-l-lg">
            {/* Header */}
            <div className="p-4 border-b border-gray-200">
              <div className="flex items-center justify-between mb-4">
                <h1 className="text-xl font-semibold text-gray-900">Messages</h1>
                <button className="p-2 text-gray-500 hover:text-gray-700 hover:bg-gray-100 rounded-lg">
                  <PlusIcon className="w-5 h-5" />
                </button>
              </div>
              
              {/* Search */}
              <div className="relative">
                <MagnifyingGlassIcon className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
                <input
                  type="text"
                  placeholder="Search conversations..."
                  className="w-full pl-9 pr-4 py-2 text-sm border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                />
              </div>
            </div>

            {/* Conversations List */}
            <div className="flex-1 overflow-y-auto">
              {filteredConversations.map((conversation) => (
                <div
                  key={conversation.id}
                  onClick={() => setSelectedConversation(conversation)}
                  className={`p-4 border-b border-gray-100 cursor-pointer transition-colors ${
                    selectedConversation?.id === conversation.id
                      ? 'bg-primary-50 border-primary-200'
                      : 'hover:bg-gray-50'
                  }`}
                >
                  <div className="flex items-center gap-3">
                    <div className="relative">
                      <div className="w-12 h-12 bg-gray-200 rounded-full flex items-center justify-center">
                        <UserIcon className="w-6 h-6 text-gray-500" />
                      </div>
                      {conversation.is_online && (
                        <div className="absolute -bottom-1 -right-1 w-4 h-4 bg-green-500 rounded-full border-2 border-white"></div>
                      )}
                    </div>
                    
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center justify-between">
                        <h3 className="font-medium text-gray-900 truncate">{conversation.name}</h3>
                        <span className="text-xs text-gray-500">{formatLastMessageTime(conversation.last_message_time)}</span>
                      </div>
                      <div className="flex items-center justify-between mt-1">
                        <p className="text-sm text-gray-600 truncate">{conversation.last_message}</p>
                        {conversation.unread_count > 0 && (
                          <span className="ml-2 px-2 py-1 bg-primary-600 text-white text-xs rounded-full min-w-[20px] text-center">
                            {conversation.unread_count}
                          </span>
                        )}
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Chat Area */}
          {selectedConversationData ? (
            <div className="flex-1 flex flex-col">
              {/* Chat Header */}
              <div className="p-4 border-b border-gray-200 bg-white">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <div className="relative">
                      <div className="w-10 h-10 bg-gray-200 rounded-full flex items-center justify-center">
                        <UserIcon className="w-5 h-5 text-gray-500" />
                      </div>
                      {selectedConversationData.is_online && (
                        <div className="absolute -bottom-1 -right-1 w-3 h-3 bg-green-500 rounded-full border-2 border-white"></div>
                      )}
                    </div>
                    <div>
                      <h2 className="font-semibold text-gray-900">{selectedConversationData.name}</h2>
                      <p className="text-sm text-gray-500">
                        {selectedConversationData.type === 'group' 
                          ? `${selectedConversationData.participants} members`
                          : selectedConversationData.is_online ? 'Online' : 'Offline'
                        }
                      </p>
                    </div>
                  </div>
                  
                  <div className="flex items-center gap-2">
                    <button className="p-2 text-gray-500 hover:text-gray-700 hover:bg-gray-100 rounded-lg">
                      <PhoneIcon className="w-5 h-5" />
                    </button>
                    <button className="p-2 text-gray-500 hover:text-gray-700 hover:bg-gray-100 rounded-lg">
                      <VideoCameraIcon className="w-5 h-5" />
                    </button>
                    <button className="p-2 text-gray-500 hover:text-gray-700 hover:bg-gray-100 rounded-lg">
                      <EllipsisVerticalIcon className="w-5 h-5" />
                    </button>
                  </div>
                </div>
              </div>

              {/* Messages */}
              <div className="flex-1 overflow-y-auto p-4 space-y-4">
                <AnimatePresence>
                  {messages.map((message) => (
                    <motion.div
                      key={message.id}
                      initial={{ opacity: 0, y: 10 }}
                      animate={{ opacity: 1, y: 0 }}
                      className={`flex ${message.sender_id === '1' ? 'justify-end' : 'justify-start'}`}
                    >
                      <div className={`flex items-end gap-2 max-w-xs lg:max-w-md ${
                        message.sender_id === '1' ? 'flex-row-reverse' : 'flex-row'
                      }`}>
                        {message.sender_id !== '1' && (
                          <div className="w-8 h-8 bg-gray-200 rounded-full flex items-center justify-center flex-shrink-0">
                            <UserIcon className="w-4 h-4 text-gray-500" />
                          </div>
                        )}
                        
                        <div className={`px-4 py-2 rounded-2xl ${
                          message.sender_id === '1' 
                            ? 'bg-primary-600 text-white' 
                            : 'bg-gray-100 text-gray-900'
                        }`}>
                          <p className="text-sm">{message.content}</p>
                          <div className={`flex items-center justify-end gap-1 mt-1 ${
                            message.sender_id === '1' ? 'text-primary-200' : 'text-gray-500'
                          }`}>
                            <span className="text-xs">{formatTime(message.timestamp)}</span>
                            {message.sender_id === '1' && (
                              <CheckCircleIcon className="w-3 h-3" />
                            )}
                          </div>
                        </div>
                      </div>
                    </motion.div>
                  ))}
                </AnimatePresence>
                <div ref={messagesEndRef} />
              </div>

              {/* Message Input */}
              <div className="p-4 border-t border-gray-200 bg-white">
                <form onSubmit={handleSendMessage} className="flex items-center gap-3">
                  <button
                    type="button"
                    className="p-2 text-gray-500 hover:text-gray-700 hover:bg-gray-100 rounded-lg"
                  >
                    <PaperClipIcon className="w-5 h-5" />
                  </button>
                  
                  <div className="flex-1 relative">
                    <input
                      type="text"
                      placeholder="Type a message..."
                      className="w-full px-4 py-2 pr-12 border border-gray-300 rounded-full focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                      value={newMessage}
                      onChange={(e) => setNewMessage(e.target.value)}
                    />
                    <button
                      type="button"
                      className="absolute right-3 top-1/2 -translate-y-1/2 p-1 text-gray-400 hover:text-gray-600"
                    >
                      <FaceSmileIcon className="w-5 h-5" />
                    </button>
                  </div>
                  
                  <button
                    type="submit"
                    disabled={!newMessage.trim()}
                    className="p-2 bg-primary-600 text-white rounded-full hover:bg-primary-700 disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    <PaperAirplaneIcon className="w-5 h-5" />
                  </button>
                </form>
              </div>
            </div>
          ) : (
            <div className="flex-1 flex items-center justify-center bg-gray-50">
              <div className="text-center">
                <UserIcon className="w-16 h-16 mx-auto text-gray-300 mb-4" />
                <h3 className="text-lg font-medium text-gray-900 mb-2">No conversation selected</h3>
                <p className="text-gray-600">Choose a conversation from the sidebar to start messaging.</p>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
