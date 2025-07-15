'use client'

import { useState, useEffect, useRef } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import DashboardLayout from '@/components/layout/DashboardLayout'
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

  // WebSocket connection and state
  const [socket, setSocket] = useState<WebSocket | null>(null)
  const [connectionStatus, setConnectionStatus] = useState<'connecting' | 'connected' | 'disconnected' | 'error'>('connecting')
  const [typingUsers, setTypingUsers] = useState<string[]>([])

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

  // WebSocket connection
  useEffect(() => {
    const token = localStorage.getItem('auth_token')
    if (!token) return

    const wsUrl = `ws://localhost:8000/api/v1/sync/ws?token=${token}`
    const ws = new WebSocket(wsUrl)

    ws.onopen = () => {
      console.log('WebSocket connected')
      setConnectionStatus('connected')
    }

    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data)
        
        if (data.type === 'message') {
          setMessages(prev => [...prev, data.message])
          
          // Update conversation list
          setConversations(prev => prev.map(conv => 
            conv.id === data.message.conversation_id 
              ? { 
                  ...conv, 
                  last_message: data.message.content,
                  last_message_time: data.message.timestamp,
                  unread_count: conv.id === selectedConversation?.id ? conv.unread_count : conv.unread_count + 1
                }
              : conv
          ))
        } else if (data.type === 'typing') {
          // Handle typing indicators
          setTypingUsers(prev => 
            data.isTyping 
              ? [...prev.filter(u => u !== data.userId), data.userId]
              : prev.filter(u => u !== data.userId)
          )
        }
      } catch (error) {
        console.error('Error parsing WebSocket message:', error)
      }
    }

    ws.onclose = () => {
      console.log('WebSocket disconnected')
      setConnectionStatus('disconnected')
      
      // Attempt to reconnect after 3 seconds
      setTimeout(() => {
        setConnectionStatus('connecting')
        // Reconnection logic would go here
      }, 3000)
    }

    ws.onerror = (error) => {
      console.error('WebSocket error:', error)
      setConnectionStatus('error')
    }

    setSocket(ws)

    return () => {
      ws.close()
    }
  }, [])

  const fetchConversations = async () => {
    try {
      // Mock data for now - replace with actual API call
      const mockConversations: Conversation[] = [
        {
          id: '1',
          name: 'Mathematics Class',
          avatar: '/api/placeholder/40/40',
          last_message: 'Great question about derivatives!',
          last_message_time: '2024-01-15T10:30:00Z',
          unread_count: 2,
          is_online: true,
          type: 'class',
          participants: 25
        },
        {
          id: '2',
          name: 'Dr. Smith',
          avatar: '/api/placeholder/40/40',
          last_message: 'The assignment is due tomorrow',
          last_message_time: '2024-01-15T09:15:00Z',
          unread_count: 0,
          is_online: false,
          type: 'direct',
          participants: 2
        },
        {
          id: '3',
          name: 'Physics Study Group',
          avatar: '/api/placeholder/40/40',
          last_message: 'Let\'s meet at 3 PM',
          last_message_time: '2024-01-15T08:45:00Z',
          unread_count: 1,
          is_online: true,
          type: 'group',
          participants: 8
        },
        {
          id: '4',
          name: 'Prof. Johnson',
          avatar: '/api/placeholder/40/40',
          last_message: 'Your essay was excellent',
          last_message_time: '2024-01-14T16:20:00Z',
          unread_count: 0,
          is_online: true,
          type: 'direct',
          participants: 2
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
      // Mock data for now - replace with actual API call
      const mockMessages: Message[] = [
        {
          id: '1',
          sender_id: '2',
          sender_name: 'Dr. Smith',
          sender_avatar: '/api/placeholder/40/40',
          content: 'Good morning everyone! Today we\'ll be covering derivatives.',
          timestamp: '2024-01-15T09:00:00Z',
          type: 'text',
          read_by: ['1', '3', '4']
        },
        {
          id: '2',
          sender_id: '1',
          sender_name: 'You',
          sender_avatar: '/api/placeholder/40/40',
          content: 'What\'s the derivative of x²?',
          timestamp: '2024-01-15T09:15:00Z',
          type: 'text',
          read_by: ['2']
        },
        {
          id: '3',
          sender_id: '2',
          sender_name: 'Dr. Smith',
          sender_avatar: '/api/placeholder/40/40',
          content: 'Great question! The derivative of x² is 2x. This follows the power rule.',
          timestamp: '2024-01-15T09:16:00Z',
          type: 'text',
          read_by: ['1']
        },
        {
          id: '4',
          sender_id: '3',
          sender_name: 'Sarah',
          sender_avatar: '/api/placeholder/40/40',
          content: 'Could you explain the chain rule as well?',
          timestamp: '2024-01-15T09:20:00Z',
          type: 'text',
          read_by: []
        },
        {
          id: '5',
          sender_id: '2',
          sender_name: 'Dr. Smith',
          sender_avatar: '/api/placeholder/40/40',
          content: 'Of course! The chain rule states that if you have a composite function f(g(x)), then the derivative is f\'(g(x)) × g\'(x).',
          timestamp: '2024-01-15T09:25:00Z',
          type: 'text',
          read_by: []
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
    if (!newMessage.trim() || !selectedConversation || !socket) return

    const messageData = {
      type: 'send_message',
      conversation_id: selectedConversation.id,
      content: newMessage,
      message_type: 'text'
    }

    try {
      // Send message via WebSocket
      socket.send(JSON.stringify(messageData))
      
      // Add message locally (optimistic update)
      const message: Message = {
        id: Date.now().toString(),
        sender_id: '1',
        sender_name: 'You',
        sender_avatar: '/api/placeholder/40/40',
        content: newMessage,
        timestamp: new Date().toISOString(),
        type: 'text',
        read_by: []
      }

      setMessages(prev => [...prev, message])
      setNewMessage('')
      
      // Update conversation's last message
      setConversations(prev => prev.map(conv => 
        conv.id === selectedConversation.id 
          ? { 
              ...conv, 
              last_message: newMessage,
              last_message_time: new Date().toISOString()
            }
          : conv
      ))
    } catch (error) {
      console.error('Error sending message:', error)
    }
  }

  const formatTime = (timestamp: string) => {
    const date = new Date(timestamp)
    return date.toLocaleTimeString('en-US', { 
      hour: '2-digit', 
      minute: '2-digit',
      hour12: true 
    })
  }

  const formatDate = (timestamp: string) => {
    const date = new Date(timestamp)
    const today = new Date()
    const yesterday = new Date(today)
    yesterday.setDate(today.getDate() - 1)

    if (date.toDateString() === today.toDateString()) {
      return 'Today'
    } else if (date.toDateString() === yesterday.toDateString()) {
      return 'Yesterday'
    } else {
      return date.toLocaleDateString('en-US', { 
        month: 'short', 
        day: 'numeric' 
      })
    }
  }

  const filteredConversations = conversations.filter(conversation =>
    conversation.name.toLowerCase().includes(searchTerm.toLowerCase())
  )

  const selectedConversationData = selectedConversation

  if (loading) {
    return (
      <DashboardLayout userType="student">
        <div className="flex items-center justify-center h-64">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
        </div>
      </DashboardLayout>
    )
  }

  return (
    <DashboardLayout userType="student">
      <div className="h-[calc(100vh-4rem)] flex">
        {/* Conversations Sidebar */}
        <div className="w-80 bg-white border-r border-gray-200 flex flex-col">
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
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
              />
            </div>
          </div>

          {/* Connection Status */}
          <div className="flex items-center gap-2 mt-2">
            <div className={`w-2 h-2 rounded-full ${
              connectionStatus === 'connected' ? 'bg-green-500' :
              connectionStatus === 'connecting' ? 'bg-yellow-500' :
              connectionStatus === 'error' ? 'bg-red-500' : 'bg-gray-500'
            }`} />
            <span className="text-xs text-gray-500">
              {connectionStatus === 'connected' ? 'Connected' :
               connectionStatus === 'connecting' ? 'Connecting...' :
               connectionStatus === 'error' ? 'Connection Error' : 'Disconnected'}
            </span>
          </div>

          {/* Conversations List */}
          <div className="flex-1 overflow-y-auto">
            {filteredConversations.map((conversation) => (
              <button
                key={conversation.id}
                onClick={() => setSelectedConversation(conversation)}
                className={`w-full p-4 text-left hover:bg-gray-50 border-b border-gray-100 transition-colors ${
                  selectedConversation?.id === conversation.id ? 'bg-primary-50 border-primary-200' : ''
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
                      <p className="font-medium text-gray-900 truncate">{conversation.name}</p>
                      <span className="text-xs text-gray-500">{formatTime(conversation.last_message_time)}</span>
                    </div>
                    <p className="text-sm text-gray-600 truncate">{conversation.last_message}</p>
                    <div className="flex items-center justify-between mt-1">
                      <span className="text-xs text-gray-500">
                        {conversation.type === 'class' && `${conversation.participants} participants`}
                        {conversation.type === 'group' && `${conversation.participants} members`}
                      </span>
                      {conversation.unread_count > 0 && (
                        <span className="bg-primary-600 text-white text-xs px-2 py-1 rounded-full">
                          {conversation.unread_count}
                        </span>
                      )}
                    </div>
                  </div>
                </div>
              </button>
            ))}
          </div>
        </div>

        {/* Chat Area */}
        <div className="flex-1 flex flex-col">
          {selectedConversationData ? (
            <>
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
                        {selectedConversationData.is_online ? 'Online' : 'Offline'}
                        {selectedConversationData.type === 'class' && ` • ${selectedConversationData.participants} participants`}
                        {selectedConversationData.type === 'group' && ` • ${selectedConversationData.participants} members`}
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
                {messages.map((message) => (
                  <motion.div
                    key={message.id}
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    className={`flex ${message.sender_id === '1' ? 'justify-end' : 'justify-start'}`}
                  >
                    <div className={`max-w-xs lg:max-w-md ${message.sender_id === '1' ? 'order-2' : 'order-1'}`}>
                      <div className={`px-4 py-2 rounded-lg ${
                        message.sender_id === '1' 
                          ? 'bg-primary-600 text-white' 
                          : 'bg-gray-100 text-gray-900'
                      }`}>
                        {message.sender_id !== '1' && (
                          <p className="text-xs font-medium mb-1 text-primary-600">
                            {message.sender_name}
                          </p>
                        )}
                        <p className="text-sm">{message.content}</p>
                        <div className="flex items-center justify-between mt-2">
                          <span className={`text-xs ${
                            message.sender_id === '1' ? 'text-primary-100' : 'text-gray-500'
                          }`}>
                            {formatTime(message.timestamp)}
                          </span>
                          {message.sender_id === '1' && (
                            <div className="flex items-center">
                              {message.read_by.length > 0 ? (
                                <CheckCircleIcon className="w-4 h-4 text-primary-100" />
                              ) : (
                                <CheckIcon className="w-4 h-4 text-primary-200" />
                              )}
                            </div>
                          )}
                        </div>
                      </div>
                    </div>
                  </motion.div>
                ))}
                <div ref={messagesEndRef} />
              </div>

              {/* Message Input */}
              <div className="p-4 border-t border-gray-200 bg-white">
                <form onSubmit={handleSendMessage} className="flex items-center gap-2">
                  <button
                    type="button"
                    className="p-2 text-gray-500 hover:text-gray-700 hover:bg-gray-100 rounded-lg"
                  >
                    <PaperClipIcon className="w-5 h-5" />
                  </button>
                  <div className="flex-1 relative">
                    <input
                      type="text"
                      value={newMessage}
                      onChange={(e) => setNewMessage(e.target.value)}
                      placeholder="Type a message..."
                      className="w-full px-4 py-2 pr-12 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                    />
                    <button
                      type="button"
                      className="absolute right-2 top-1/2 -translate-y-1/2 p-1 text-gray-500 hover:text-gray-700 hover:bg-gray-100 rounded"
                    >
                      <FaceSmileIcon className="w-5 h-5" />
                    </button>
                  </div>
                  <button
                    type="submit"
                    disabled={!newMessage.trim()}
                    className="p-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                  >
                    <PaperAirplaneIcon className="w-5 h-5" />
                  </button>
                </form>
              </div>
            </>
          ) : (
            <div className="flex-1 flex items-center justify-center">
              <div className="text-center">
                <div className="w-16 h-16 bg-gray-200 rounded-full flex items-center justify-center mx-auto mb-4">
                  <UserIcon className="w-8 h-8 text-gray-500" />
                </div>
                <h3 className="text-lg font-medium text-gray-900 mb-2">No conversation selected</h3>
                <p className="text-gray-600">Choose a conversation to start messaging</p>
              </div>
            </div>
          )}
        </div>
      </div>
    </DashboardLayout>
  )
}
