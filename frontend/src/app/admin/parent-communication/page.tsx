'use client'

import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { useAuth } from '@/contexts/AuthContext'
import { useToast } from '@/contexts/ToastContext'
import {
  ChatBubbleLeftRightIcon,
  PhoneIcon,
  EnvelopeIcon,
  UserGroupIcon,
  PaperAirplaneIcon,
  ClockIcon,
  CheckIcon,
  ExclamationTriangleIcon,
  FunnelIcon,
  MagnifyingGlassIcon,
  PlusIcon,
  EllipsisVerticalIcon,
  DocumentTextIcon,
  BellIcon,
  CalendarIcon,
  AcademicCapIcon,
  InformationCircleIcon,
  XMarkIcon,
  TagIcon,
  ArrowPathIcon
} from '@heroicons/react/24/outline'
import {
  CheckIcon as CheckIconSolid,
  ChatBubbleLeftRightIcon as ChatIconSolid
} from '@heroicons/react/24/solid'

interface Contact {
  id: number
  name: string
  relationship: 'parent' | 'guardian'
  studentId: number
  studentName: string
  phone: string
  email: string
  whatsapp?: string
  preferredMethod: 'sms' | 'whatsapp' | 'email'
  isActive: boolean
  lastContact?: string
}

interface Message {
  id: number
  contactId: number
  type: 'sms' | 'whatsapp' | 'email'
  subject?: string
  content: string
  status: 'draft' | 'sending' | 'sent' | 'delivered' | 'read' | 'failed'
  sentAt?: string
  deliveredAt?: string
  readAt?: string
  priority: 'low' | 'normal' | 'high' | 'urgent'
  category: 'announcement' | 'reminder' | 'emergency' | 'academic' | 'administrative'
  templateId?: number
  scheduledFor?: string
}

interface Template {
  id: number
  name: string
  subject: string
  content: string
  type: 'sms' | 'whatsapp' | 'email'
  category: string
  variables: string[]
  isActive: boolean
  createdAt: string
}

interface Campaign {
  id: number
  name: string
  description: string
  type: 'sms' | 'whatsapp' | 'email'
  recipients: number[]
  templateId: number
  status: 'draft' | 'scheduled' | 'sending' | 'completed' | 'cancelled'
  scheduledFor?: string
  sentCount: number
  deliveredCount: number
  readCount: number
  failedCount: number
  createdAt: string
}

export default function ParentCommunication() {
  const { user } = useAuth()
  const { success, error } = useToast()
  const [activeTab, setActiveTab] = useState('messages')
  const [isLoading, setIsLoading] = useState(true)
  const [contacts, setContacts] = useState<Contact[]>([])
  const [messages, setMessages] = useState<Message[]>([])
  const [templates, setTemplates] = useState<Template[]>([])
  const [campaigns, setCampaigns] = useState<Campaign[]>([])
  const [selectedContacts, setSelectedContacts] = useState<number[]>([])
  const [searchTerm, setSearchTerm] = useState('')
  const [filterType, setFilterType] = useState('all')
  const [filterStatus, setFilterStatus] = useState('all')
  const [showComposeModal, setShowComposeModal] = useState(false)
  const [showTemplateModal, setShowTemplateModal] = useState(false)
  const [composeData, setComposeData] = useState({
    type: 'sms' as 'sms' | 'whatsapp' | 'email',
    subject: '',
    content: '',
    priority: 'normal' as 'low' | 'normal' | 'high' | 'urgent',
    category: 'announcement' as 'announcement' | 'reminder' | 'emergency' | 'academic' | 'administrative',
    scheduledFor: '',
    templateId: ''
  })

  // Load communication data
  useEffect(() => {
    const loadData = async () => {
      try {
        setIsLoading(true)
        
        // Mock data - replace with actual API calls
        setContacts([
          {
            id: 1,
            name: 'John Smith',
            relationship: 'parent',
            studentId: 1,
            studentName: 'Alice Smith',
            phone: '+234-801-234-5678',
            email: 'john.smith@email.com',
            whatsapp: '+234-801-234-5678',
            preferredMethod: 'whatsapp',
            isActive: true,
            lastContact: '2024-01-15'
          },
          {
            id: 2,
            name: 'Mary Johnson',
            relationship: 'parent',
            studentId: 2,
            studentName: 'David Johnson',
            phone: '+234-802-345-6789',
            email: 'mary.johnson@email.com',
            preferredMethod: 'email',
            isActive: true,
            lastContact: '2024-01-14'
          },
          {
            id: 3,
            name: 'Robert Brown',
            relationship: 'guardian',
            studentId: 3,
            studentName: 'Sarah Brown',
            phone: '+234-803-456-7890',
            email: 'robert.brown@email.com',
            whatsapp: '+234-803-456-7890',
            preferredMethod: 'sms',
            isActive: true,
            lastContact: '2024-01-13'
          }
        ])

        setMessages([
          {
            id: 1,
            contactId: 1,
            type: 'whatsapp',
            subject: 'School Fee Reminder',
            content: 'Dear parent, this is to remind you that your child\'s school fee is due on January 30th.',
            status: 'delivered',
            sentAt: '2024-01-15T10:30:00Z',
            deliveredAt: '2024-01-15T10:31:00Z',
            priority: 'normal',
            category: 'reminder',
            templateId: 1
          },
          {
            id: 2,
            contactId: 2,
            type: 'email',
            subject: 'Parent-Teacher Conference',
            content: 'We would like to invite you to attend the upcoming parent-teacher conference.',
            status: 'read',
            sentAt: '2024-01-14T14:00:00Z',
            deliveredAt: '2024-01-14T14:01:00Z',
            readAt: '2024-01-14T16:30:00Z',
            priority: 'normal',
            category: 'announcement',
            templateId: 2
          }
        ])

        setTemplates([
          {
            id: 1,
            name: 'Fee Reminder',
            subject: 'School Fee Reminder',
            content: 'Dear {{parent_name}}, this is to remind you that {{student_name}}\'s school fee is due on {{due_date}}.',
            type: 'sms',
            category: 'reminder',
            variables: ['parent_name', 'student_name', 'due_date'],
            isActive: true,
            createdAt: '2024-01-10'
          },
          {
            id: 2,
            name: 'Academic Performance',
            subject: 'Academic Performance Update',
            content: 'Dear {{parent_name}}, we would like to update you on {{student_name}}\'s academic performance.',
            type: 'email',
            category: 'academic',
            variables: ['parent_name', 'student_name'],
            isActive: true,
            createdAt: '2024-01-10'
          }
        ])

        setCampaigns([
          {
            id: 1,
            name: 'Term Fee Reminders',
            description: 'Reminder campaign for first term fee payments',
            type: 'whatsapp',
            recipients: [1, 2, 3],
            templateId: 1,
            status: 'completed',
            scheduledFor: '2024-01-15T09:00:00Z',
            sentCount: 3,
            deliveredCount: 3,
            readCount: 2,
            failedCount: 0,
            createdAt: '2024-01-14'
          }
        ])

      } catch (err) {
        console.error('Failed to load communication data:', err)
        error('Failed to load communication data')
      } finally {
        setIsLoading(false)
      }
    }

    loadData()
  }, [error])

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'sent':
      case 'delivered':
      case 'read':
        return 'text-green-600 bg-green-100'
      case 'sending':
        return 'text-blue-600 bg-blue-100'
      case 'draft':
        return 'text-gray-600 bg-gray-100'
      case 'failed':
        return 'text-red-600 bg-red-100'
      default:
        return 'text-gray-600 bg-gray-100'
    }
  }

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'urgent':
        return 'text-red-600 bg-red-100'
      case 'high':
        return 'text-orange-600 bg-orange-100'
      case 'normal':
        return 'text-blue-600 bg-blue-100'
      case 'low':
        return 'text-gray-600 bg-gray-100'
      default:
        return 'text-gray-600 bg-gray-100'
    }
  }

  const getTypeIcon = (type: string) => {
    switch (type) {
      case 'sms':
        return PhoneIcon
      case 'whatsapp':
        return ChatBubbleLeftRightIcon
      case 'email':
        return EnvelopeIcon
      default:
        return PhoneIcon
    }
  }

  const sendMessage = async () => {
    try {
      if (!composeData.content.trim() || selectedContacts.length === 0) {
        error('Please fill in all required fields and select recipients')
        return
      }

      // Create new message
      const newMessage: Message = {
        id: Date.now(),
        contactId: selectedContacts[0], // For demo, use first selected contact
        type: composeData.type,
        subject: composeData.subject,
        content: composeData.content,
        status: 'sending',
        priority: composeData.priority,
        category: composeData.category,
        sentAt: new Date().toISOString()
      }

      setMessages(prev => [newMessage, ...prev])
      setShowComposeModal(false)
      setComposeData({
        type: 'sms',
        subject: '',
        content: '',
        priority: 'normal',
        category: 'announcement',
        scheduledFor: '',
        templateId: ''
      })
      setSelectedContacts([])

      success(`Message sent to ${selectedContacts.length} recipient(s)`)

      // Simulate status updates
      setTimeout(() => {
        setMessages(prev => prev.map(msg => 
          msg.id === newMessage.id ? { ...msg, status: 'delivered', deliveredAt: new Date().toISOString() } : msg
        ))
      }, 2000)

    } catch (err) {
      error('Failed to send message')
    }
  }

  const renderMessages = () => (
    <div className="space-y-6">
      {/* Header and Actions */}
      <div className="bg-white rounded-lg shadow p-6">
        <div className="flex flex-col sm:flex-row gap-4 justify-between items-start sm:items-center">
          <div>
            <h3 className="text-lg font-semibold">Messages</h3>
            <p className="text-gray-600">Send and manage communications with parents</p>
          </div>
          <button
            onClick={() => setShowComposeModal(true)}
            className="flex items-center px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
          >
            <PlusIcon className="w-4 h-4 mr-2" />
            Compose Message
          </button>
        </div>
      </div>

      {/* Filters */}
      <div className="bg-white rounded-lg shadow p-6">
        <div className="flex flex-col sm:flex-row gap-4">
          <div className="flex-1">
            <div className="relative">
              <MagnifyingGlassIcon className="w-5 h-5 absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" />
              <input
                type="text"
                placeholder="Search messages..."
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
              <option value="sms">SMS</option>
              <option value="whatsapp">WhatsApp</option>
              <option value="email">Email</option>
            </select>
            <select
              value={filterStatus}
              onChange={(e) => setFilterStatus(e.target.value)}
              className="px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            >
              <option value="all">All Status</option>
              <option value="draft">Draft</option>
              <option value="sent">Sent</option>
              <option value="delivered">Delivered</option>
              <option value="read">Read</option>
              <option value="failed">Failed</option>
            </select>
          </div>
        </div>
      </div>

      {/* Messages List */}
      <div className="bg-white rounded-lg shadow overflow-hidden">
        <div className="p-6 border-b border-gray-200">
          <h4 className="font-semibold">Recent Messages</h4>
        </div>
        <div className="divide-y divide-gray-200">
          {messages.map((message) => {
            const contact = contacts.find(c => c.id === message.contactId)
            const TypeIcon = getTypeIcon(message.type)
            
            return (
              <div key={message.id} className="p-6 hover:bg-gray-50">
                <div className="flex items-start justify-between">
                  <div className="flex items-start space-x-4">
                    <div className={`p-2 rounded-lg ${
                      message.type === 'sms' ? 'bg-green-100' :
                      message.type === 'whatsapp' ? 'bg-green-100' :
                      'bg-blue-100'
                    }`}>
                      <TypeIcon className={`w-5 h-5 ${
                        message.type === 'sms' ? 'text-green-600' :
                        message.type === 'whatsapp' ? 'text-green-600' :
                        'text-blue-600'
                      }`} />
                    </div>
                    <div className="flex-1">
                      <div className="flex items-center space-x-3 mb-1">
                        <h4 className="font-medium">{contact?.name}</h4>
                        <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${getStatusColor(message.status)}`}>
                          {message.status}
                        </span>
                        <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${getPriorityColor(message.priority)}`}>
                          {message.priority}
                        </span>
                      </div>
                      {message.subject && (
                        <p className="font-medium text-gray-900 mb-1">{message.subject}</p>
                      )}
                      <p className="text-gray-600 mb-2 line-clamp-2">{message.content}</p>
                      <div className="flex items-center space-x-4 text-sm text-gray-500">
                        <span>{contact?.studentName}</span>
                        <span>•</span>
                        <span>{message.category}</span>
                        <span>•</span>
                        <span>{message.sentAt ? new Date(message.sentAt).toLocaleDateString() : 'Not sent'}</span>
                      </div>
                    </div>
                  </div>
                  <div className="flex items-center space-x-2">
                    {message.status === 'read' && <CheckIconSolid className="w-5 h-5 text-green-600" />}
                    {message.status === 'delivered' && <CheckIcon className="w-5 h-5 text-blue-600" />}
                    {message.status === 'failed' && <ExclamationTriangleIcon className="w-5 h-5 text-red-600" />}
                    <button className="text-gray-400 hover:text-gray-600">
                      <EllipsisVerticalIcon className="w-5 h-5" />
                    </button>
                  </div>
                </div>
              </div>
            )
          })}
        </div>
      </div>
    </div>
  )

  const renderContacts = () => (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-white rounded-lg shadow p-6">
        <div className="flex justify-between items-center">
          <div>
            <h3 className="text-lg font-semibold">Parent Contacts</h3>
            <p className="text-gray-600">Manage parent and guardian contact information</p>
          </div>
          <button className="flex items-center px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700">
            <PlusIcon className="w-4 h-4 mr-2" />
            Add Contact
          </button>
        </div>
      </div>

      {/* Contacts Table */}
      <div className="bg-white rounded-lg shadow overflow-hidden">
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  <input type="checkbox" className="rounded" />
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Contact
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Student
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Contact Info
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Preferred Method
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Last Contact
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {contacts.map((contact) => (
                <tr key={contact.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4 whitespace-nowrap">
                    <input
                      type="checkbox"
                      checked={selectedContacts.includes(contact.id)}
                      onChange={(e) => {
                        if (e.target.checked) {
                          setSelectedContacts(prev => [...prev, contact.id])
                        } else {
                          setSelectedContacts(prev => prev.filter(id => id !== contact.id))
                        }
                      }}
                      className="rounded"
                    />
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div>
                      <div className="text-sm font-medium text-gray-900">{contact.name}</div>
                      <div className="text-sm text-gray-500 capitalize">{contact.relationship}</div>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm text-gray-900">{contact.studentName}</div>
                  </td>
                  <td className="px-6 py-4">
                    <div className="text-sm text-gray-900">
                      <div className="flex items-center mb-1">
                        <PhoneIcon className="w-4 h-4 mr-2 text-gray-400" />
                        {contact.phone}
                      </div>
                      <div className="flex items-center mb-1">
                        <EnvelopeIcon className="w-4 h-4 mr-2 text-gray-400" />
                        {contact.email}
                      </div>
                      {contact.whatsapp && (
                        <div className="flex items-center">
                          <ChatBubbleLeftRightIcon className="w-4 h-4 mr-2 text-gray-400" />
                          {contact.whatsapp}
                        </div>
                      )}
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                      contact.preferredMethod === 'sms' ? 'bg-green-100 text-green-800' :
                      contact.preferredMethod === 'whatsapp' ? 'bg-green-100 text-green-800' :
                      'bg-blue-100 text-blue-800'
                    }`}>
                      {contact.preferredMethod.toUpperCase()}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {contact.lastContact ? new Date(contact.lastContact).toLocaleDateString() : 'Never'}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                    <div className="flex space-x-2">
                      <button className="text-blue-600 hover:text-blue-900">Edit</button>
                      <button
                        onClick={() => {
                          setSelectedContacts([contact.id])
                          setShowComposeModal(true)
                        }}
                        className="text-green-600 hover:text-green-900"
                      >
                        Message
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Bulk Actions */}
      {selectedContacts.length > 0 && (
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
          <div className="flex items-center justify-between">
            <p className="text-blue-800">
              {selectedContacts.length} contact(s) selected
            </p>
            <div className="flex space-x-2">
              <button
                onClick={() => setShowComposeModal(true)}
                className="flex items-center px-3 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
              >
                <PaperAirplaneIcon className="w-4 h-4 mr-2" />
                Send Message
              </button>
              <button
                onClick={() => setSelectedContacts([])}
                className="px-3 py-2 text-blue-700 bg-blue-100 rounded-md hover:bg-blue-200"
              >
                Clear Selection
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )

  const renderTemplates = () => (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-white rounded-lg shadow p-6">
        <div className="flex justify-between items-center">
          <div>
            <h3 className="text-lg font-semibold">Message Templates</h3>
            <p className="text-gray-600">Create and manage reusable message templates</p>
          </div>
          <button
            onClick={() => setShowTemplateModal(true)}
            className="flex items-center px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
          >
            <PlusIcon className="w-4 h-4 mr-2" />
            New Template
          </button>
        </div>
      </div>

      {/* Templates Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {templates.map((template) => {
          const TypeIcon = getTypeIcon(template.type)
          return (
            <motion.div
              key={template.id}
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              className="bg-white rounded-lg shadow p-6"
            >
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center">
                  <div className={`p-2 rounded-lg mr-3 ${
                    template.type === 'sms' ? 'bg-green-100' :
                    template.type === 'whatsapp' ? 'bg-green-100' :
                    'bg-blue-100'
                  }`}>
                    <TypeIcon className={`w-5 h-5 ${
                      template.type === 'sms' ? 'text-green-600' :
                      template.type === 'whatsapp' ? 'text-green-600' :
                      'text-blue-600'
                    }`} />
                  </div>
                  <div>
                    <h4 className="font-semibold">{template.name}</h4>
                    <p className="text-sm text-gray-600 capitalize">{template.category}</p>
                  </div>
                </div>
                <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                  template.isActive ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'
                }`}>
                  {template.isActive ? 'Active' : 'Inactive'}
                </span>
              </div>
              
              {template.subject && (
                <p className="font-medium text-gray-900 mb-2">{template.subject}</p>
              )}
              <p className="text-gray-600 text-sm mb-4 line-clamp-3">{template.content}</p>
              
              {template.variables.length > 0 && (
                <div className="mb-4">
                  <p className="text-xs text-gray-500 mb-2">Variables:</p>
                  <div className="flex flex-wrap gap-1">
                    {template.variables.map((variable) => (
                      <span
                        key={variable}
                        className="inline-flex items-center px-2 py-1 text-xs bg-gray-100 text-gray-700 rounded"
                      >
                        <TagIcon className="w-3 h-3 mr-1" />
                        {variable}
                      </span>
                    ))}
                  </div>
                </div>
              )}
              
              <div className="flex space-x-2">
                <button
                  onClick={() => {
                    setComposeData(prev => ({
                      ...prev,
                      type: template.type,
                      subject: template.subject,
                      content: template.content,
                      templateId: template.id.toString()
                    }))
                    setShowComposeModal(true)
                  }}
                  className="flex-1 px-3 py-2 text-sm bg-blue-100 text-blue-700 rounded-md hover:bg-blue-200"
                >
                  Use Template
                </button>
                <button className="flex-1 px-3 py-2 text-sm bg-gray-100 text-gray-700 rounded-md hover:bg-gray-200">
                  Edit
                </button>
              </div>
            </motion.div>
          )
        })}
      </div>
    </div>
  )

  const renderCampaigns = () => (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-white rounded-lg shadow p-6">
        <div className="flex justify-between items-center">
          <div>
            <h3 className="text-lg font-semibold">Message Campaigns</h3>
            <p className="text-gray-600">Create and manage bulk messaging campaigns</p>
          </div>
          <button className="flex items-center px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700">
            <PlusIcon className="w-4 h-4 mr-2" />
            New Campaign
          </button>
        </div>
      </div>

      {/* Campaigns List */}
      <div className="bg-white rounded-lg shadow overflow-hidden">
        <div className="p-6 border-b border-gray-200">
          <h4 className="font-semibold">Recent Campaigns</h4>
        </div>
        <div className="divide-y divide-gray-200">
          {campaigns.map((campaign) => {
            const TypeIcon = getTypeIcon(campaign.type)
            const deliveryRate = campaign.sentCount > 0 ? (campaign.deliveredCount / campaign.sentCount) * 100 : 0
            const readRate = campaign.deliveredCount > 0 ? (campaign.readCount / campaign.deliveredCount) * 100 : 0
            
            return (
              <div key={campaign.id} className="p-6">
                <div className="flex items-start justify-between mb-4">
                  <div className="flex items-start space-x-4">
                    <div className={`p-2 rounded-lg ${
                      campaign.type === 'sms' ? 'bg-green-100' :
                      campaign.type === 'whatsapp' ? 'bg-green-100' :
                      'bg-blue-100'
                    }`}>
                      <TypeIcon className={`w-5 h-5 ${
                        campaign.type === 'sms' ? 'text-green-600' :
                        campaign.type === 'whatsapp' ? 'text-green-600' :
                        'text-blue-600'
                      }`} />
                    </div>
                    <div>
                      <h4 className="font-semibold text-gray-900">{campaign.name}</h4>
                      <p className="text-gray-600 mb-2">{campaign.description}</p>
                      <div className="flex items-center space-x-4 text-sm text-gray-500">
                        <span>{campaign.recipients.length} recipients</span>
                        <span>•</span>
                        <span>{new Date(campaign.createdAt).toLocaleDateString()}</span>
                        {campaign.scheduledFor && (
                          <>
                            <span>•</span>
                            <span>Scheduled: {new Date(campaign.scheduledFor).toLocaleString()}</span>
                          </>
                        )}
                      </div>
                    </div>
                  </div>
                  <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${getStatusColor(campaign.status)}`}>
                    {campaign.status}
                  </span>
                </div>
                
                {/* Campaign Stats */}
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                  <div className="text-center p-3 bg-gray-50 rounded-lg">
                    <p className="text-2xl font-bold text-blue-600">{campaign.sentCount}</p>
                    <p className="text-sm text-gray-600">Sent</p>
                  </div>
                  <div className="text-center p-3 bg-gray-50 rounded-lg">
                    <p className="text-2xl font-bold text-green-600">{campaign.deliveredCount}</p>
                    <p className="text-sm text-gray-600">Delivered</p>
                    <p className="text-xs text-gray-500">{deliveryRate.toFixed(1)}%</p>
                  </div>
                  <div className="text-center p-3 bg-gray-50 rounded-lg">
                    <p className="text-2xl font-bold text-purple-600">{campaign.readCount}</p>
                    <p className="text-sm text-gray-600">Read</p>
                    <p className="text-xs text-gray-500">{readRate.toFixed(1)}%</p>
                  </div>
                  <div className="text-center p-3 bg-gray-50 rounded-lg">
                    <p className="text-2xl font-bold text-red-600">{campaign.failedCount}</p>
                    <p className="text-sm text-gray-600">Failed</p>
                  </div>
                </div>
              </div>
            )
          })}
        </div>
      </div>
    </div>
  )

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading communication data...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 py-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Parent Communication</h1>
          <p className="text-gray-600 mt-2">Send messages and manage communication with parents and guardians</p>
        </div>

        {/* Navigation Tabs */}
        <div className="border-b border-gray-200 mb-8">
          <nav className="-mb-px flex space-x-8">
            {[
              { id: 'messages', name: 'Messages', icon: ChatBubbleLeftRightIcon },
              { id: 'contacts', name: 'Contacts', icon: UserGroupIcon },
              { id: 'templates', name: 'Templates', icon: DocumentTextIcon },
              { id: 'campaigns', name: 'Campaigns', icon: BellIcon },
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
          {activeTab === 'messages' && renderMessages()}
          {activeTab === 'contacts' && renderContacts()}
          {activeTab === 'templates' && renderTemplates()}
          {activeTab === 'campaigns' && renderCampaigns()}
        </motion.div>

        {/* Compose Message Modal */}
        {showComposeModal && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
            <div className="bg-white rounded-lg p-6 w-full max-w-2xl max-h-[90vh] overflow-y-auto">
              <div className="flex justify-between items-center mb-6">
                <h3 className="text-lg font-semibold">Compose Message</h3>
                <button
                  onClick={() => setShowComposeModal(false)}
                  className="text-gray-400 hover:text-gray-600"
                >
                  <XMarkIcon className="w-6 h-6" />
                </button>
              </div>

              <div className="space-y-4">
                {/* Recipients */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Recipients ({selectedContacts.length} selected)
                  </label>
                  <div className="text-sm text-gray-600">
                    {selectedContacts.length === 0 
                      ? 'No recipients selected' 
                      : `${selectedContacts.length} recipient(s) selected`
                    }
                  </div>
                </div>

                {/* Message Type */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Message Type</label>
                  <select
                    value={composeData.type}
                    onChange={(e) => setComposeData(prev => ({ ...prev, type: e.target.value as any }))}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  >
                    <option value="sms">SMS</option>
                    <option value="whatsapp">WhatsApp</option>
                    <option value="email">Email</option>
                  </select>
                </div>

                {/* Subject (for email) */}
                {composeData.type === 'email' && (
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">Subject</label>
                    <input
                      type="text"
                      value={composeData.subject}
                      onChange={(e) => setComposeData(prev => ({ ...prev, subject: e.target.value }))}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                      placeholder="Message subject"
                    />
                  </div>
                )}

                {/* Message Content */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Message</label>
                  <textarea
                    value={composeData.content}
                    onChange={(e) => setComposeData(prev => ({ ...prev, content: e.target.value }))}
                    rows={6}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                    placeholder="Type your message here..."
                  />
                  <p className="text-sm text-gray-500 mt-1">
                    {composeData.content.length} characters
                    {composeData.type === 'sms' && composeData.content.length > 160 && 
                      ` (${Math.ceil(composeData.content.length / 160)} SMS segments)`
                    }
                  </p>
                </div>

                {/* Priority and Category */}
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">Priority</label>
                    <select
                      value={composeData.priority}
                      onChange={(e) => setComposeData(prev => ({ ...prev, priority: e.target.value as any }))}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                    >
                      <option value="low">Low</option>
                      <option value="normal">Normal</option>
                      <option value="high">High</option>
                      <option value="urgent">Urgent</option>
                    </select>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">Category</label>
                    <select
                      value={composeData.category}
                      onChange={(e) => setComposeData(prev => ({ ...prev, category: e.target.value as any }))}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                    >
                      <option value="announcement">Announcement</option>
                      <option value="reminder">Reminder</option>
                      <option value="emergency">Emergency</option>
                      <option value="academic">Academic</option>
                      <option value="administrative">Administrative</option>
                    </select>
                  </div>
                </div>

                {/* Schedule (optional) */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Schedule for later (optional)
                  </label>
                  <input
                    type="datetime-local"
                    value={composeData.scheduledFor}
                    onChange={(e) => setComposeData(prev => ({ ...prev, scheduledFor: e.target.value }))}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  />
                </div>
              </div>

              <div className="flex justify-end space-x-3 mt-6 pt-6 border-t border-gray-200">
                <button
                  onClick={() => setShowComposeModal(false)}
                  className="px-4 py-2 text-gray-700 bg-gray-100 rounded-md hover:bg-gray-200"
                >
                  Cancel
                </button>
                <button
                  onClick={sendMessage}
                  disabled={!composeData.content.trim() || selectedContacts.length === 0}
                  className="flex items-center px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  <PaperAirplaneIcon className="w-4 h-4 mr-2" />
                  {composeData.scheduledFor ? 'Schedule Message' : 'Send Message'}
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
