'use client'

import { useState } from 'react'
import { motion } from 'framer-motion'
import { useAuth } from '@/contexts/AuthContext'
import { useToast } from '@/contexts/ToastContext'
import {
  DocumentTextIcon,
  AcademicCapIcon,
  ClockIcon,
  Cog6ToothIcon,
  ArrowDownTrayIcon,
  SparklesIcon,
  CheckCircleIcon,
  ExclamationTriangleIcon
} from '@heroicons/react/24/outline'

interface GeneratedPaper {
  id: string
  subject: string
  level: string
  questionCount: number
  sections: PaperSection[]
  estimatedDuration: number
  difficultyDistribution: { [key: string]: number }
  createdAt: string
}

interface PaperSection {
  id: string
  title: string
  instructions: string
  questions: Question[]
  timeAllocation: number
  marks: number
}

interface Question {
  id: string
  type: 'multiple_choice' | 'essay' | 'short_answer' | 'calculation'
  question: string
  options?: string[]
  correctAnswer?: string
  markingScheme: string
  difficulty: 'easy' | 'medium' | 'hard'
  topic: string
  marks: number
}

const SUBJECTS = [
  'Mathematics',
  'English Language', 
  'Physics',
  'Chemistry',
  'Biology',
  'Geography',
  'History',
  'Economics',
  'Literature in English',
  'Government',
  'Agricultural Science',
  'Further Mathematics'
]

const TOPICS_BY_SUBJECT: { [key: string]: string[] } = {
  'Mathematics': [
    'Number and Numeration',
    'Algebraic Processes',
    'Geometry and Trigonometry',
    'Calculus',
    'Statistics and Probability',
    'Vectors and Mechanics'
  ],
  'English Language': [
    'Comprehension',
    'Summary',
    'Lexis and Structure',
    'Oral English',
    'Essay Writing',
    'Literature'
  ],
  'Physics': [
    'Mechanics',
    'Heat and Thermodynamics',
    'Light and Optics',
    'Sound Waves',
    'Electricity and Magnetism',
    'Modern Physics'
  ],
  'Chemistry': [
    'Atomic Structure',
    'Chemical Bonding',
    'Rates of Reaction',
    'Acids and Bases',
    'Organic Chemistry',
    'Industrial Chemistry'
  ]
}

export default function WAECPaperGenerator() {
  const [selectedSubject, setSelectedSubject] = useState('Mathematics')
  const [selectedLevel, setSelectedLevel] = useState('O-Level')
  const [questionCount, setQuestionCount] = useState(50)
  const [includeEssay, setIncludeEssay] = useState(true)
  const [difficultyMix, setDifficultyMix] = useState({
    easy: 30,
    medium: 50,
    hard: 20
  })
  const [selectedTopics, setSelectedTopics] = useState<string[]>([])
  const [isGenerating, setIsGenerating] = useState(false)
  const [generatedPaper, setGeneratedPaper] = useState<GeneratedPaper | null>(null)
  const [showPreview, setShowPreview] = useState(false)

  const { user } = useAuth()
  const { success: showSuccess, error: showError } = useToast()

  const handleTopicToggle = (topic: string) => {
    setSelectedTopics(prev => 
      prev.includes(topic)
        ? prev.filter(t => t !== topic)
        : [...prev, topic]
    )
  }

  const generatePaper = async () => {
    if (selectedTopics.length === 0) {
      showError('Please select at least one topic')
      return
    }

    setIsGenerating(true)

    try {
      // Simulate AI paper generation
      const paper = await simulateAIPaperGeneration()
      setGeneratedPaper(paper)
      setShowPreview(true)
      showSuccess('WAEC paper generated successfully!')
    } catch (error) {
      console.error('Error generating paper:', error)
      showError('Failed to generate paper. Please try again.')
    } finally {
      setIsGenerating(false)
    }
  }

  const simulateAIPaperGeneration = async (): Promise<GeneratedPaper> => {
    // Simulate API delay
    await new Promise(resolve => setTimeout(resolve, 3000))

    const sections: PaperSection[] = []

    // Section A: Multiple Choice (40 questions)
    const mcqQuestions: Question[] = []
    for (let i = 1; i <= 40; i++) {
      mcqQuestions.push({
        id: `mcq_${i}`,
        type: 'multiple_choice',
        question: generateSampleQuestion(selectedSubject, 'multiple_choice', i),
        options: ['A. Option A', 'B. Option B', 'C. Option C', 'D. Option D'],
        correctAnswer: 'A',
        markingScheme: '1 mark for correct answer',
        difficulty: getDifficultyByIndex(i),
        topic: selectedTopics[i % selectedTopics.length],
        marks: 1
      })
    }

    sections.push({
      id: 'section_a',
      title: 'Section A: Multiple Choice Questions',
      instructions: 'Answer ALL questions in this section. Choose the most appropriate option (A, B, C, or D) for each question.',
      questions: mcqQuestions,
      timeAllocation: 60,
      marks: 40
    })

    // Section B: Essay Questions (if included)
    if (includeEssay) {
      const essayQuestions: Question[] = []
      for (let i = 1; i <= 6; i++) {
        essayQuestions.push({
          id: `essay_${i}`,
          type: 'essay',
          question: generateSampleQuestion(selectedSubject, 'essay', i),
          markingScheme: '10 marks - detailed marking scheme with allocation for different aspects',
          difficulty: 'medium',
          topic: selectedTopics[i % selectedTopics.length],
          marks: 10
        })
      }

      sections.push({
        id: 'section_b',
        title: 'Section B: Essay Questions',
        instructions: 'Answer any FOUR questions from this section.',
        questions: essayQuestions,
        timeAllocation: 120,
        marks: 40
      })
    }

    return {
      id: Date.now().toString(),
      subject: selectedSubject,
      level: selectedLevel,
      questionCount: 40 + (includeEssay ? 6 : 0),
      sections,
      estimatedDuration: 180,
      difficultyDistribution: difficultyMix,
      createdAt: new Date().toISOString()
    }
  }

  const generateSampleQuestion = (subject: string, type: string, index: number): string => {
    const sampleQuestions = {
      Mathematics: {
        multiple_choice: [
          'Simplify 3x + 2y - x + 4y',
          'Find the value of x in the equation 2x + 5 = 13',
          'Calculate the area of a circle with radius 7cm (Take π = 22/7)',
          'Solve for y: 3y - 7 = 2y + 8'
        ],
        essay: [
          'A rectangular plot of land has length (3x + 2) meters and width (2x - 1) meters. If the perimeter is 50 meters, find the dimensions of the plot.',
          'Given that the nth term of a sequence is Tn = 3n + 2, find the sum of the first 20 terms.',
          'A cone has base radius 6cm and height 8cm. Calculate its total surface area.'
        ]
      },
      'English Language': {
        multiple_choice: [
          'Choose the option that best completes the sentence: The students _____ to school every day.',
          'Identify the figure of speech in: "The classroom was a zoo during break time."',
          'Which of the following is a synonym for "abundant"?',
          'Select the correct spelling:'
        ],
        essay: [
          'Write a letter to your friend describing your experience during the last school holidays.',
          'You are the Senior Prefect of your school. Write a speech you would deliver to welcome new students.',
          'Write a story that ends with: "...and that was how I learned the importance of honesty."'
        ]
      }
    }

    const subjectQuestions = sampleQuestions[subject as keyof typeof sampleQuestions] || sampleQuestions.Mathematics
    const typeQuestions = subjectQuestions[type as keyof typeof subjectQuestions]
    return typeQuestions[index % typeQuestions.length]
  }

  const getDifficultyByIndex = (index: number): 'easy' | 'medium' | 'hard' => {
    if (index <= 12) return 'easy'
    if (index <= 32) return 'medium'
    return 'hard'
  }

  const downloadPaper = () => {
    if (!generatedPaper) return

    const paperContent = formatPaperForDownload(generatedPaper)
    const blob = new Blob([paperContent], { type: 'text/plain' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `${generatedPaper.subject}_WAEC_Paper_${new Date().getFullYear()}.txt`
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    URL.revokeObjectURL(url)
  }

  const formatPaperForDownload = (paper: GeneratedPaper): string => {
    let content = `WEST AFRICAN EXAMINATIONS COUNCIL\n`
    content += `WEST AFRICAN SENIOR SCHOOL CERTIFICATE EXAMINATION\n\n`
    content += `${paper.subject.toUpperCase()}\n`
    content += `Paper 1 & 2\n`
    content += `${new Date().getFullYear()}\n\n`
    content += `Time Allowed: ${Math.floor(paper.estimatedDuration / 60)} hours ${paper.estimatedDuration % 60} minutes\n\n`
    content += `INSTRUCTIONS\n`
    content += `Answer ALL questions in Section A and any FOUR questions from Section B.\n`
    content += `All questions carry equal marks.\n`
    content += `Write your answers in the spaces provided in this question paper.\n\n`

    paper.sections.forEach((section, sectionIndex) => {
      content += `${section.title.toUpperCase()}\n`
      content += `${section.instructions}\n\n`

      section.questions.forEach((question, questionIndex) => {
        content += `${questionIndex + 1}. ${question.question}\n`
        
        if (question.options) {
          question.options.forEach(option => {
            content += `   ${option}\n`
          })
        }
        content += `   [${question.marks} mark${question.marks > 1 ? 's' : ''}]\n\n`
      })
      
      content += `\n`
    })

    return content
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="text-center mb-8">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="inline-flex items-center space-x-2 bg-purple-100 text-purple-800 px-4 py-2 rounded-full text-sm font-medium mb-4"
          >
            <SparklesIcon className="w-4 h-4" />
            <span>AI-Powered</span>
          </motion.div>
          
          <motion.h1
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
            className="text-3xl font-bold text-gray-900 mb-2"
          >
            WAEC Paper Generator
          </motion.h1>
          
          <motion.p
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
            className="text-lg text-gray-600"
          >
            Generate WAEC-standard examination papers with AI assistance
          </motion.p>
        </div>

        {!showPreview ? (
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
            {/* Configuration Panel */}
            <div className="lg:col-span-2 space-y-6">
              {/* Basic Settings */}
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                className="bg-white rounded-2xl shadow-lg p-6"
              >
                <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
                  <Cog6ToothIcon className="w-5 h-5 mr-2" />
                  Paper Configuration
                </h3>
                
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Subject
                    </label>
                    <select
                      value={selectedSubject}
                      onChange={(e) => {
                        setSelectedSubject(e.target.value)
                        setSelectedTopics([])
                      }}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500"
                    >
                      {SUBJECTS.map(subject => (
                        <option key={subject} value={subject}>{subject}</option>
                      ))}
                    </select>
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Level
                    </label>
                    <select
                      value={selectedLevel}
                      onChange={(e) => setSelectedLevel(e.target.value)}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500"
                    >
                      <option value="O-Level">O-Level (WAEC)</option>
                      <option value="A-Level">A-Level</option>
                    </select>
                  </div>
                </div>

                <div className="mt-4">
                  <label className="flex items-center">
                    <input
                      type="checkbox"
                      checked={includeEssay}
                      onChange={(e) => setIncludeEssay(e.target.checked)}
                      className="mr-2"
                    />
                    <span className="text-sm text-gray-700">Include Essay/Theory Section</span>
                  </label>
                </div>
              </motion.div>

              {/* Topic Selection */}
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.1 }}
                className="bg-white rounded-2xl shadow-lg p-6"
              >
                <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
                  <AcademicCapIcon className="w-5 h-5 mr-2" />
                  Topics to Include
                </h3>
                
                <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
                  {(TOPICS_BY_SUBJECT[selectedSubject] || []).map(topic => (
                    <button
                      key={topic}
                      onClick={() => handleTopicToggle(topic)}
                      className={`p-3 rounded-lg border-2 text-sm font-medium transition-all ${
                        selectedTopics.includes(topic)
                          ? 'border-purple-500 bg-purple-50 text-purple-800'
                          : 'border-gray-200 hover:border-gray-300 text-gray-700'
                      }`}
                    >
                      {topic}
                    </button>
                  ))}
                </div>
                
                {selectedTopics.length === 0 && (
                  <div className="mt-4 p-3 bg-yellow-50 border border-yellow-200 rounded-lg flex items-center">
                    <ExclamationTriangleIcon className="w-5 h-5 text-yellow-600 mr-2" />
                    <span className="text-sm text-yellow-800">Please select at least one topic</span>
                  </div>
                )}
              </motion.div>

              {/* Difficulty Distribution */}
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.2 }}
                className="bg-white rounded-2xl shadow-lg p-6"
              >
                <h3 className="text-lg font-semibold text-gray-900 mb-4">
                  Difficulty Distribution
                </h3>
                
                <div className="space-y-4">
                  <div>
                    <div className="flex justify-between mb-1">
                      <span className="text-sm text-gray-600">Easy Questions</span>
                      <span className="text-sm font-medium">{difficultyMix.easy}%</span>
                    </div>
                    <input
                      type="range"
                      min="0"
                      max="100"
                      value={difficultyMix.easy}
                      onChange={(e) => setDifficultyMix(prev => ({
                        ...prev,
                        easy: parseInt(e.target.value)
                      }))}
                      className="w-full h-2 bg-green-200 rounded-lg appearance-none cursor-pointer slider-green"
                    />
                  </div>
                  
                  <div>
                    <div className="flex justify-between mb-1">
                      <span className="text-sm text-gray-600">Medium Questions</span>
                      <span className="text-sm font-medium">{difficultyMix.medium}%</span>
                    </div>
                    <input
                      type="range"
                      min="0"
                      max="100"
                      value={difficultyMix.medium}
                      onChange={(e) => setDifficultyMix(prev => ({
                        ...prev,
                        medium: parseInt(e.target.value)
                      }))}
                      className="w-full h-2 bg-yellow-200 rounded-lg appearance-none cursor-pointer slider-yellow"
                    />
                  </div>
                  
                  <div>
                    <div className="flex justify-between mb-1">
                      <span className="text-sm text-gray-600">Hard Questions</span>
                      <span className="text-sm font-medium">{difficultyMix.hard}%</span>
                    </div>
                    <input
                      type="range"
                      min="0"
                      max="100"
                      value={difficultyMix.hard}
                      onChange={(e) => setDifficultyMix(prev => ({
                        ...prev,
                        hard: parseInt(e.target.value)
                      }))}
                      className="w-full h-2 bg-red-200 rounded-lg appearance-none cursor-pointer slider-red"
                    />
                  </div>
                </div>
              </motion.div>
            </div>

            {/* Summary & Generate */}
            <div className="space-y-6">
              <motion.div
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
                className="bg-white rounded-2xl shadow-lg p-6"
              >
                <h3 className="text-lg font-semibold text-gray-900 mb-4">
                  Paper Summary
                </h3>
                
                <div className="space-y-3">
                  <div className="flex justify-between">
                    <span className="text-gray-600">Subject:</span>
                    <span className="font-medium">{selectedSubject}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Level:</span>
                    <span className="font-medium">{selectedLevel}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Topics:</span>
                    <span className="font-medium">{selectedTopics.length}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Format:</span>
                    <span className="font-medium">
                      MCQ {includeEssay ? '+ Essay' : 'Only'}
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Est. Duration:</span>
                    <span className="font-medium">3 hours</span>
                  </div>
                </div>

                <button
                  onClick={generatePaper}
                  disabled={isGenerating || selectedTopics.length === 0}
                  className="w-full mt-6 px-6 py-3 bg-purple-600 text-white rounded-lg font-medium hover:bg-purple-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center justify-center space-x-2"
                >
                  {isGenerating ? (
                    <>
                      <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white" />
                      <span>Generating...</span>
                    </>
                  ) : (
                    <>
                      <SparklesIcon className="w-5 h-5" />
                      <span>Generate Paper</span>
                    </>
                  )}
                </button>
              </motion.div>

              {/* AI Features */}
              <motion.div
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 0.1 }}
                className="bg-gradient-to-br from-purple-50 to-indigo-50 rounded-2xl p-6"
              >
                <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
                  <SparklesIcon className="w-5 h-5 mr-2 text-purple-600" />
                  AI Features
                </h3>
                
                <div className="space-y-3">
                  <div className="flex items-start space-x-3">
                    <CheckCircleIcon className="w-5 h-5 text-green-500 flex-shrink-0 mt-0.5" />
                    <div>
                      <div className="font-medium text-gray-900">Curriculum Aligned</div>
                      <div className="text-sm text-gray-600">Questions follow WAEC syllabus</div>
                    </div>
                  </div>
                  
                  <div className="flex items-start space-x-3">
                    <CheckCircleIcon className="w-5 h-5 text-green-500 flex-shrink-0 mt-0.5" />
                    <div>
                      <div className="font-medium text-gray-900">Balanced Difficulty</div>
                      <div className="text-sm text-gray-600">Mix of easy, medium, and hard questions</div>
                    </div>
                  </div>
                  
                  <div className="flex items-start space-x-3">
                    <CheckCircleIcon className="w-5 h-5 text-green-500 flex-shrink-0 mt-0.5" />
                    <div>
                      <div className="font-medium text-gray-900">Marking Schemes</div>
                      <div className="text-sm text-gray-600">Detailed marking guide included</div>
                    </div>
                  </div>
                  
                  <div className="flex items-start space-x-3">
                    <CheckCircleIcon className="w-5 h-5 text-green-500 flex-shrink-0 mt-0.5" />
                    <div>
                      <div className="font-medium text-gray-900">Instant Generation</div>
                      <div className="text-sm text-gray-600">Ready in seconds</div>
                    </div>
                  </div>
                </div>
              </motion.div>
            </div>
          </div>
        ) : (
          /* Paper Preview */
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="bg-white rounded-2xl shadow-lg p-8"
          >
            <div className="flex items-center justify-between mb-6">
              <div>
                <h2 className="text-2xl font-bold text-gray-900">Generated Paper Preview</h2>
                <p className="text-gray-600">{generatedPaper?.subject} - {generatedPaper?.level}</p>
              </div>
              
              <div className="flex space-x-3">
                <button
                  onClick={() => setShowPreview(false)}
                  className="px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50"
                >
                  Edit Configuration
                </button>
                <button
                  onClick={downloadPaper}
                  className="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 flex items-center space-x-2"
                >
                  <ArrowDownTrayIcon className="w-4 h-4" />
                  <span>Download</span>
                </button>
              </div>
            </div>

            {/* Paper Header */}
            <div className="text-center border-b pb-6 mb-6">
              <h3 className="text-xl font-bold">WEST AFRICAN EXAMINATIONS COUNCIL</h3>
              <h4 className="text-lg font-semibold mt-2">WEST AFRICAN SENIOR SCHOOL CERTIFICATE EXAMINATION</h4>
              <div className="mt-4">
                <div className="text-lg font-semibold">{generatedPaper?.subject.toUpperCase()}</div>
                <div className="text-gray-600">Paper 1 & 2</div>
                <div className="text-gray-600">{new Date().getFullYear()}</div>
              </div>
              <div className="mt-4 text-sm">
                <div>Time Allowed: {Math.floor((generatedPaper?.estimatedDuration || 180) / 60)} hours {(generatedPaper?.estimatedDuration || 180) % 60} minutes</div>
              </div>
            </div>

            {/* Instructions */}
            <div className="mb-8">
              <h5 className="font-semibold text-gray-900 mb-2">INSTRUCTIONS</h5>
              <ul className="text-sm text-gray-600 space-y-1">
                <li>• Answer ALL questions in Section A and any FOUR questions from Section B.</li>
                <li>• All questions carry equal marks.</li>
                <li>• Write your answers in the spaces provided in this question paper.</li>
              </ul>
            </div>

            {/* Sections Preview */}
            {generatedPaper?.sections.map((section, index) => (
              <div key={section.id} className="mb-8">
                <h4 className="text-lg font-semibold text-gray-900 mb-2">{section.title}</h4>
                <p className="text-sm text-gray-600 mb-4">{section.instructions}</p>
                
                {/* Show first 3 questions as preview */}
                <div className="space-y-4">
                  {section.questions.slice(0, 3).map((question, qIndex) => (
                    <div key={question.id} className="pl-4 border-l-2 border-gray-200">
                      <div className="font-medium text-gray-900">
                        {qIndex + 1}. {question.question}
                      </div>
                      {question.options && (
                        <div className="mt-2 ml-4 space-y-1">
                          {question.options.map((option, oIndex) => (
                            <div key={oIndex} className="text-sm text-gray-600">{option}</div>
                          ))}
                        </div>
                      )}
                      <div className="mt-1 text-xs text-gray-500">
                        [{question.marks} mark{question.marks > 1 ? 's' : ''}] - {question.difficulty} difficulty
                      </div>
                    </div>
                  ))}
                  
                  {section.questions.length > 3 && (
                    <div className="text-sm text-gray-500 italic">
                      ... and {section.questions.length - 3} more questions
                    </div>
                  )}
                </div>
              </div>
            ))}

            <div className="mt-8 pt-6 border-t text-center text-sm text-gray-500">
              Generated by EduNerve AI Paper Generator - {new Date().toLocaleDateString()}
            </div>
          </motion.div>
        )}
      </div>
    </div>
  )
}
