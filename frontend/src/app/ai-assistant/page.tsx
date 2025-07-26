'use client'

import { useState, useRef, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { useAuth } from '@/contexts/AuthContext'
import { useToast } from '@/contexts/ToastContext'
import {
  ChatBubbleLeftRightIcon,
  PaperAirplaneIcon,
  SparklesIcon,
  AcademicCapIcon,
  BookOpenIcon,
  LightBulbIcon,
  ClipboardDocumentListIcon,
  PhotoIcon,
  MicrophoneIcon,
  StopIcon,
  DocumentTextIcon,
  TrashIcon,
  ArrowPathIcon
} from '@heroicons/react/24/outline'
import { CheckCircleIcon, ExclamationCircleIcon } from '@heroicons/react/24/solid'

interface Message {
  id: string
  role: 'user' | 'assistant'
  content: string
  timestamp: Date
  type?: 'text' | 'image' | 'voice'
  metadata?: {
    subject?: string
    topic?: string
    difficulty?: string
    questionType?: string
  }
}

interface StudySession {
  id: string
  title: string
  subject: string
  messages: Message[]
  createdAt: Date
  lastActivity: Date
}

const SUBJECT_PROMPTS = {
  'Mathematics': [
    'Explain quadratic equations with examples',
    'Help me solve calculus problems',
    'What are the properties of triangles?',
    'Teach me about probability and statistics'
  ],
  'Physics': [
    'Explain Newton\'s laws of motion',
    'Help me understand electromagnetic waves',
    'What is quantum physics?',
    'Explain thermodynamics concepts'
  ],
  'Chemistry': [
    'Explain atomic structure',
    'Help me balance chemical equations',
    'What are organic compounds?',
    'Teach me about chemical reactions'
  ],
  'Biology': [
    'Explain photosynthesis process',
    'Help me understand genetics',
    'What is cellular respiration?',
    'Teach me about evolution'
  ],
  'English': [
    'Help me improve my essay writing',
    'Explain literary devices',
    'What makes good grammar?',
    'Help me with vocabulary building'
  ],
  'General': [
    'Help me create a study schedule',
    'What are effective study techniques?',
    'How can I improve my memory?',
    'Give me exam preparation tips'
  ]
}

const QUICK_ACTIONS = [
  {
    icon: BookOpenIcon,
    label: 'Explain Concept',
    prompt: 'Can you explain this concept in simple terms:'
  },
  {
    icon: ClipboardDocumentListIcon,
    label: 'Practice Questions',
    prompt: 'Generate practice questions for:'
  },
  {
    icon: LightBulbIcon,
    label: 'Study Tips',
    prompt: 'Give me study tips for:'
  },
  {
    icon: DocumentTextIcon,
    label: 'Summarize Topic',
    prompt: 'Provide a summary of:'
  }
]

export default function AIStudyAssistant() {
  const [messages, setMessages] = useState<Message[]>([])
  const [input, setInput] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [selectedSubject, setSelectedSubject] = useState('General')
  const [sessions, setSessions] = useState<StudySession[]>([])
  const [currentSession, setCurrentSession] = useState<string | null>(null)
  const [isRecording, setIsRecording] = useState(false)
  const [showImageUpload, setShowImageUpload] = useState(false)
  
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const fileInputRef = useRef<HTMLInputElement>(null)
  const { user } = useAuth()
  const { success: showSuccess, error: showError } = useToast()

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  useEffect(() => {
    // Initialize with welcome message
    if (messages.length === 0) {
      const welcomeMessage: Message = {
        id: Date.now().toString(),
        role: 'assistant',
        content: `Hello! I'm your AI Study Assistant. I'm here to help you with your studies across all subjects. You can:

• Ask me to explain concepts in simple terms
• Request practice questions and exercises  
• Get study tips and techniques
• Upload images of problems for help
• Start voice conversations

What would you like to learn about today?`,
        timestamp: new Date(),
        type: 'text'
      }
      setMessages([welcomeMessage])
    }
  }, [])

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  const sendMessage = async (content: string, type: 'text' | 'image' | 'voice' = 'text') => {
    if (!content.trim() && type === 'text') return

    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content,
      timestamp: new Date(),
      type,
      metadata: {
        subject: selectedSubject
      }
    }

    setMessages(prev => [...prev, userMessage])
    setInput('')
    setIsLoading(true)

    try {
      // Simulate AI response
      const response = await simulateAIResponse(content, selectedSubject, type)
      
      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: response,
        timestamp: new Date(),
        type: 'text',
        metadata: {
          subject: selectedSubject
        }
      }

      setMessages(prev => [...prev, assistantMessage])
    } catch (error) {
      console.error('Error sending message:', error)
      showError('Failed to get response. Please try again.')
    } finally {
      setIsLoading(false)
    }
  }

  const simulateAIResponse = async (userInput: string, subject: string, type: string): Promise<string> => {
    // Simulate AI processing delay
    await new Promise(resolve => setTimeout(resolve, 1500))

    const lowerInput = userInput.toLowerCase()

    // Response patterns based on input type and content
    if (type === 'image') {
      return `I can see the image you've uploaded. Based on what I observe, this appears to be a ${subject} problem. Let me help you solve it step by step:

1. **Identify the problem type**: This looks like a [specific problem type]
2. **Key concepts involved**: [relevant concepts]
3. **Solution approach**: 
   - Start by [step 1]
   - Then [step 2]
   - Finally [step 3]

Would you like me to explain any of these steps in more detail?`
    }

    if (type === 'voice') {
      return `I heard your voice message about ${subject}. Let me help you with that:

[Response based on voice input analysis]

Feel free to ask follow-up questions or request clarification on any part!`
    }

    // Text-based responses
    if (lowerInput.includes('explain') || lowerInput.includes('what is')) {
      return generateExplanationResponse(userInput, subject)
    }

    if (lowerInput.includes('practice') || lowerInput.includes('questions') || lowerInput.includes('exercise')) {
      return generatePracticeQuestions(subject)
    }

    if (lowerInput.includes('study tips') || lowerInput.includes('how to study')) {
      return generateStudyTips(subject)
    }

    if (lowerInput.includes('solve') || lowerInput.includes('help me with')) {
      return generateProblemSolvingHelp(userInput, subject)
    }

    // Default response
    return `I understand you're asking about ${subject}. Let me help you with that:

${generateDefaultResponse(userInput, subject)}

Is there a specific aspect you'd like me to focus on or explain in more detail?`
  }

  const generateExplanationResponse = (input: string, subject: string): string => {
    const explanations = {
      'Mathematics': `Great question about mathematics! Let me break this down for you:

**Core Concept**: [Key mathematical principle]

**Step-by-step explanation**:
1. First, understand that [basic principle]
2. Then, apply the formula: [relevant formula]
3. Finally, solve using [method]

**Example**: Let's say we have [practical example]
- Given: [known values]
- Find: [unknown values]
- Solution: [step by step solution]

**Visual representation**: [ASCII diagram or description]

Would you like me to provide more examples or explain any specific part in detail?`,

      'Physics': `Excellent physics question! Here's a comprehensive explanation:

**Physical Principle**: [Core physics concept]

**Real-world application**: You can observe this in [everyday example]

**Mathematical relationship**: 
- Formula: [relevant equation]
- Units: [SI units]
- Variables: [variable definitions]

**Key insights**:
• [Important point 1]
• [Important point 2]
• [Important point 3]

**Common misconceptions**: 
- Many students think [misconception], but actually [correct understanding]

Would you like me to work through a specific problem or explain the derivation of the formula?`,

      'Chemistry': `Great chemistry question! Let me explain this clearly:

**Chemical concept**: [Core principle]

**Molecular level**: At the atomic/molecular level, [molecular explanation]

**Chemical equation**: [Relevant equation with balanced formula]

**Step-by-step process**:
1. [Step 1 with explanation]
2. [Step 2 with explanation]
3. [Step 3 with explanation]

**Important factors**:
- Temperature: [effect]
- Pressure: [effect]
- Catalysts: [effect]

**Laboratory application**: In the lab, you would [practical application]

Would you like me to explain the mechanism in more detail or provide practice problems?`
    }

    return explanations[subject as keyof typeof explanations] || explanations['Mathematics']
  }

  const generatePracticeQuestions = (subject: string): string => {
    const questions = {
      'Mathematics': `Here are some practice questions for mathematics:

**Beginner Level**:
1. Solve for x: 2x + 5 = 13
2. Find the area of a circle with radius 7 cm
3. What is 15% of 240?

**Intermediate Level**:
4. Factor the quadratic: x² + 5x + 6
5. Find the derivative of f(x) = 3x² + 2x - 1
6. Solve the system: 2x + y = 7, x - y = 2

**Advanced Level**:
7. Integrate ∫(2x + 3)dx from 0 to 5
8. Find the limit of (sin x)/x as x approaches 0
9. Prove that the sum of angles in a triangle is 180°

**Word Problems**:
10. A train travels 300 km in 4 hours. What's its average speed?

Try solving these and let me know if you need help with any specific question!`,

      'Physics': `Here are practice questions for physics:

**Mechanics**:
1. A ball is thrown upward with initial velocity 20 m/s. How high does it go?
2. Calculate the force needed to accelerate a 5 kg object at 3 m/s²
3. A car accelerates from 0 to 60 km/h in 8 seconds. Find the acceleration.

**Electricity & Magnetism**:
4. Calculate current in a circuit with 12V battery and 4Ω resistance
5. Find the magnetic field around a straight current-carrying wire
6. What's the capacitance of a parallel plate capacitor?

**Waves & Optics**:
7. Calculate the frequency of light with wavelength 500 nm
8. Find the focal length of a convex lens with given parameters
9. Explain interference patterns in Young's double-slit experiment

**Thermodynamics**:
10. Calculate efficiency of a heat engine with given temperatures

Work through these step by step and ask if you need detailed solutions!`
    }

    return questions[subject as keyof typeof questions] || questions['Mathematics']
  }

  const generateStudyTips = (subject: string): string => {
    return `Here are effective study tips for ${subject}:

**📚 Active Learning Strategies**:
• Use the Feynman Technique - explain concepts in simple terms
• Create mind maps to visualize connections
• Practice spaced repetition for better retention
• Teach concepts to others or explain to yourself aloud

**⏰ Time Management**:
• Use the Pomodoro Technique (25 min study, 5 min break)
• Schedule regular review sessions
• Break complex topics into smaller chunks
• Set specific, measurable goals for each study session

**📝 Note-Taking Methods**:
• Cornell Note-Taking System for organized notes
• Use colors and diagrams for visual memory
• Summarize key points in your own words
• Create flashcards for important formulas/concepts

**🧠 Memory Techniques**:
• Use mnemonics for formulas and facts
• Create associations with familiar concepts
• Practice retrieval instead of just re-reading
• Sleep well - memory consolidation happens during sleep

**📱 Digital Tools**:
• Use apps like Anki for spaced repetition
• Record yourself explaining concepts
• Join online study groups and forums
• Use educational videos to supplement learning

**✅ Exam Preparation**:
• Practice past papers regularly
• Time yourself during practice sessions
• Identify weak areas and focus extra time there
• Stay calm and confident during exams

Would you like me to elaborate on any of these techniques or provide subject-specific strategies?`
  }

  const generateProblemSolvingHelp = (input: string, subject: string): string => {
    return `I'm here to help you solve this ${subject} problem! Let me guide you through my systematic approach:

**🔍 Problem Analysis**:
1. **Understand what's given**: [identify known information]
2. **Identify what to find**: [clarify the question]
3. **Recognize the problem type**: [categorize the problem]

**💡 Solution Strategy**:
1. **Choose the right approach**: [select appropriate method/formula]
2. **Set up the problem**: [organize the information]
3. **Solve step by step**: [work through systematically]
4. **Check your answer**: [verify the solution makes sense]

**📋 Step-by-Step Solution**:
[I'll work through your specific problem here once you provide the details]

**🎯 Key Tips for This Type of Problem**:
• [Tip 1 specific to the problem type]
• [Tip 2 for avoiding common mistakes]
• [Tip 3 for checking your work]

**🔄 Similar Practice Problems**:
I can generate similar problems for you to practice this concept.

Please share the specific problem you're working on, and I'll walk you through the solution step by step!`
  }

  const generateDefaultResponse = (input: string, subject: string): string => {
    return `I understand you're asking about ${subject}. Let me provide you with helpful information:

**Overview**: [General overview of the topic]

**Key Points**:
• [Important point 1]
• [Important point 2] 
• [Important point 3]

**Applications**: [How this applies in real life or exams]

**Next Steps**: [Suggestions for further learning]

Feel free to ask more specific questions about any aspect you'd like me to explain in detail!`
  }

  const handleQuickAction = (action: typeof QUICK_ACTIONS[0]) => {
    setInput(action.prompt + ' ')
  }

  const handleVoiceRecording = () => {
    if (isRecording) {
      setIsRecording(false)
      // Simulate voice input
      sendMessage('Voice message received', 'voice')
    } else {
      setIsRecording(true)
      // Start recording simulation
      setTimeout(() => {
        setIsRecording(false)
      }, 3000)
    }
  }

  const handleImageUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0]
    if (file) {
      // Simulate image processing
      sendMessage(`Image uploaded: ${file.name}`, 'image')
      setShowImageUpload(false)
    }
  }

  const clearChat = () => {
    setMessages([])
    // Re-add welcome message
    const welcomeMessage: Message = {
      id: Date.now().toString(),
      role: 'assistant',
      content: `Hello! I'm your AI Study Assistant. I'm here to help you with your studies across all subjects. What would you like to learn about today?`,
      timestamp: new Date(),
      type: 'text'
    }
    setMessages([welcomeMessage])
  }

  const newSession = () => {
    // Save current session if it has messages
    if (messages.length > 1) {
      const session: StudySession = {
        id: Date.now().toString(),
        title: `${selectedSubject} Study Session`,
        subject: selectedSubject,
        messages: messages,
        createdAt: new Date(),
        lastActivity: new Date()
      }
      setSessions(prev => [session, ...prev])
    }
    
    clearChat()
    setCurrentSession(null)
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-6xl mx-auto">
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6 h-screen">
          
          {/* Sidebar */}
          <div className="lg:col-span-1 bg-white border-r border-gray-200 p-4">
            {/* Header */}
            <div className="flex items-center space-x-2 mb-6">
              <div className="p-2 bg-purple-100 rounded-lg">
                <SparklesIcon className="w-5 h-5 text-purple-600" />
              </div>
              <div>
                <h2 className="font-semibold text-gray-900">AI Assistant</h2>
                <p className="text-xs text-gray-500">Study Helper</p>
              </div>
            </div>

            {/* New Session Button */}
            <button
              onClick={newSession}
              className="w-full mb-4 px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors flex items-center space-x-2"
            >
              <ChatBubbleLeftRightIcon className="w-4 h-4" />
              <span>New Session</span>
            </button>

            {/* Subject Selection */}
            <div className="mb-6">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Subject Focus
              </label>
              <select
                value={selectedSubject}
                onChange={(e) => setSelectedSubject(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 text-sm"
              >
                {Object.keys(SUBJECT_PROMPTS).map(subject => (
                  <option key={subject} value={subject}>{subject}</option>
                ))}
              </select>
            </div>

            {/* Quick Prompts */}
            <div className="mb-6">
              <h3 className="text-sm font-medium text-gray-700 mb-3">Quick Start</h3>
              <div className="space-y-2">
                {SUBJECT_PROMPTS[selectedSubject as keyof typeof SUBJECT_PROMPTS].map((prompt, index) => (
                  <button
                    key={index}
                    onClick={() => sendMessage(prompt)}
                    className="w-full text-left px-3 py-2 text-sm text-gray-600 hover:bg-gray-50 rounded-lg transition-colors"
                  >
                    {prompt}
                  </button>
                ))}
              </div>
            </div>

            {/* Quick Actions */}
            <div className="mb-6">
              <h3 className="text-sm font-medium text-gray-700 mb-3">Quick Actions</h3>
              <div className="grid grid-cols-2 gap-2">
                {QUICK_ACTIONS.map((action, index) => (
                  <button
                    key={index}
                    onClick={() => handleQuickAction(action)}
                    className="p-2 text-xs text-center border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors"
                  >
                    <action.icon className="w-4 h-4 mx-auto mb-1 text-gray-600" />
                    <div>{action.label}</div>
                  </button>
                ))}
              </div>
            </div>

            {/* Session History */}
            {sessions.length > 0 && (
              <div>
                <h3 className="text-sm font-medium text-gray-700 mb-3">Recent Sessions</h3>
                <div className="space-y-2 max-h-48 overflow-y-auto">
                  {sessions.slice(0, 5).map(session => (
                    <button
                      key={session.id}
                      onClick={() => {
                        setMessages(session.messages)
                        setCurrentSession(session.id)
                        setSelectedSubject(session.subject)
                      }}
                      className="w-full text-left p-2 text-sm hover:bg-gray-50 rounded-lg"
                    >
                      <div className="font-medium text-gray-900 truncate">{session.title}</div>
                      <div className="text-xs text-gray-500">
                        {session.createdAt.toLocaleDateString()}
                      </div>
                    </button>
                  ))}
                </div>
              </div>
            )}
          </div>

          {/* Main Chat Area */}
          <div className="lg:col-span-3 flex flex-col bg-white">
            {/* Chat Header */}
            <div className="flex items-center justify-between p-4 border-b border-gray-200">
              <div className="flex items-center space-x-3">
                <AcademicCapIcon className="w-6 h-6 text-purple-600" />
                <div>
                  <h1 className="font-semibold text-gray-900">AI Study Assistant</h1>
                  <p className="text-sm text-gray-500">Subject: {selectedSubject}</p>
                </div>
              </div>
              
              <div className="flex items-center space-x-2">
                <button
                  onClick={clearChat}
                  className="p-2 text-gray-500 hover:text-gray-700 hover:bg-gray-100 rounded-lg"
                  title="Clear chat"
                >
                  <TrashIcon className="w-4 h-4" />
                </button>
                <div className="flex items-center space-x-1">
                  <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                  <span className="text-sm text-gray-500">Online</span>
                </div>
              </div>
            </div>

            {/* Messages */}
            <div className="flex-1 overflow-y-auto p-4 space-y-4">
              <AnimatePresence>
                {messages.map((message) => (
                  <motion.div
                    key={message.id}
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, y: -20 }}
                    className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
                  >
                    <div className={`max-w-3xl ${message.role === 'user' ? 'order-2' : ''}`}>
                      <div className={`px-4 py-2 rounded-2xl ${
                        message.role === 'user'
                          ? 'bg-purple-600 text-white'
                          : 'bg-gray-100 text-gray-900'
                      }`}>
                        <div className="whitespace-pre-wrap">{message.content}</div>
                        {message.type !== 'text' && (
                          <div className="mt-2 flex items-center space-x-1 text-xs opacity-75">
                            {message.type === 'image' && <PhotoIcon className="w-3 h-3" />}
                            {message.type === 'voice' && <MicrophoneIcon className="w-3 h-3" />}
                            <span>{message.type} message</span>
                          </div>
                        )}
                      </div>
                      <div className={`text-xs text-gray-500 mt-1 ${
                        message.role === 'user' ? 'text-right' : 'text-left'
                      }`}>
                        {message.timestamp.toLocaleTimeString()}
                      </div>
                    </div>
                    
                    <div className={`flex-shrink-0 ${message.role === 'user' ? 'order-1 ml-3' : 'mr-3'}`}>
                      <div className={`w-8 h-8 rounded-full flex items-center justify-center ${
                        message.role === 'user'
                          ? 'bg-purple-600 text-white'
                          : 'bg-gray-200 text-gray-600'
                      }`}>
                        {message.role === 'user' ? (
                          user?.name?.charAt(0).toUpperCase() || 'U'
                        ) : (
                          <SparklesIcon className="w-4 h-4" />
                        )}
                      </div>
                    </div>
                  </motion.div>
                ))}
              </AnimatePresence>

              {isLoading && (
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="flex justify-start"
                >
                  <div className="max-w-3xl">
                    <div className="bg-gray-100 px-4 py-2 rounded-2xl">
                      <div className="flex space-x-1">
                        <div className="w-2 h-2 bg-gray-400 rounded-full animate-pulse"></div>
                        <div className="w-2 h-2 bg-gray-400 rounded-full animate-pulse" style={{ animationDelay: '0.2s' }}></div>
                        <div className="w-2 h-2 bg-gray-400 rounded-full animate-pulse" style={{ animationDelay: '0.4s' }}></div>
                      </div>
                    </div>
                  </div>
                </motion.div>
              )}

              <div ref={messagesEndRef} />
            </div>

            {/* Input Area */}
            <div className="border-t border-gray-200 p-4">
              <div className="flex items-end space-x-3">
                <div className="flex-1">
                  <div className="flex items-center space-x-2 mb-2">
                    <button
                      onClick={() => setShowImageUpload(!showImageUpload)}
                      className="p-1 text-gray-500 hover:text-purple-600 transition-colors"
                      title="Upload image"
                    >
                      <PhotoIcon className="w-5 h-5" />
                    </button>
                    
                    <button
                      onClick={handleVoiceRecording}
                      className={`p-1 transition-colors ${
                        isRecording 
                          ? 'text-red-600 hover:text-red-700' 
                          : 'text-gray-500 hover:text-purple-600'
                      }`}
                      title={isRecording ? 'Stop recording' : 'Voice input'}
                    >
                      {isRecording ? (
                        <StopIcon className="w-5 h-5" />
                      ) : (
                        <MicrophoneIcon className="w-5 h-5" />
                      )}
                    </button>

                    {isRecording && (
                      <span className="text-sm text-red-600 animate-pulse">Recording...</span>
                    )}
                  </div>

                  {showImageUpload && (
                    <div className="mb-2">
                      <input
                        ref={fileInputRef}
                        type="file"
                        accept="image/*"
                        onChange={handleImageUpload}
                        className="block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-purple-50 file:text-purple-700 hover:file:bg-purple-100"
                      />
                    </div>
                  )}

                  <div className="flex items-center space-x-2">
                    <textarea
                      value={input}
                      onChange={(e) => setInput(e.target.value)}
                      onKeyDown={(e) => {
                        if (e.key === 'Enter' && !e.shiftKey) {
                          e.preventDefault()
                          sendMessage(input)
                        }
                      }}
                      placeholder="Ask me anything about your studies..."
                      rows={1}
                      className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 resize-none"
                      style={{ minHeight: '42px', maxHeight: '120px' }}
                    />
                    
                    <button
                      onClick={() => sendMessage(input)}
                      disabled={!input.trim() || isLoading}
                      className="p-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                    >
                      <PaperAirplaneIcon className="w-5 h-5" />
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
