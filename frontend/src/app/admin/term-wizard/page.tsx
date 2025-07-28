'use client'

import { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { useAuth } from '@/contexts/AuthContext'
import { useToast } from '@/contexts/ToastContext'
import {
  CheckCircleIcon,
  ClockIcon,
  AcademicCapIcon,
  CalendarIcon,
  ChartBarIcon,
  BookOpenIcon,
  CogIcon,
  ArrowRightIcon,
  ArrowLeftIcon,
  PlusIcon,
  TrashIcon
} from '@heroicons/react/24/outline'

interface WizardStep {
  id: string
  name: string
  description: string
  icon: any
  completed: boolean
}

interface TermData {
  basicInfo: {
    name: string
    academicYear: string
    startDate: string
    endDate: string
    description: string
  }
  schedules: Array<{
    className: string
    subjectName: string
    teacherId: number
    dayOfWeek: string
    startTime: string
    endTime: string
    room: string
  }>
  assessments: Array<{
    type: string
    name: string
    weightPercentage: number
    description: string
    isRequired: boolean
  }>
  grading: {
    gradeScale: string
    minScore: number
    maxScore: number
    passingScore: number
    gradeBoundaries: Record<string, number>
  }
  holidays: Array<{
    name: string
    startDate: string
    endDate: string
    description: string
  }>
}

const WIZARD_STEPS: WizardStep[] = [
  {
    id: 'basic_info',
    name: 'Basic Information',
    description: 'Set term name, dates, and basic details',
    icon: ClockIcon,
    completed: false
  },
  {
    id: 'schedule',
    name: 'Class Schedule',
    description: 'Configure class timetables',
    icon: CalendarIcon,
    completed: false
  },
  {
    id: 'subjects',
    name: 'Subjects',
    description: 'Set up subjects and curriculum',
    icon: BookOpenIcon,
    completed: false
  },
  {
    id: 'assessment',
    name: 'Assessment Configuration',
    description: 'Configure assessment types and weights',
    icon: ChartBarIcon,
    completed: false
  },
  {
    id: 'grading',
    name: 'Grading System',
    description: 'Set up grading scales and boundaries',
    icon: AcademicCapIcon,
    completed: false
  },
  {
    id: 'holidays',
    name: 'Holidays & Breaks',
    description: 'Define holidays and term breaks',
    icon: CalendarIcon,
    completed: false
  },
  {
    id: 'review',
    name: 'Review',
    description: 'Review all configurations',
    icon: CheckCircleIcon,
    completed: false
  }
]

const DAYS_OF_WEEK = [
  'monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday'
]

const ASSESSMENT_TYPES = [
  'quiz', 'assignment', 'exam', 'project', 'participation'
]

const GRADE_SCALES = [
  'percentage', 'letter', 'points', 'pass_fail'
]

export default function TermWizardPage() {
  const { user } = useAuth()
  const { success, error } = useToast()
  const [currentStep, setCurrentStep] = useState(0)
  const [completedSteps, setCompletedSteps] = useState<string[]>([])
  const [termData, setTermData] = useState<TermData>({
    basicInfo: {
      name: '',
      academicYear: '',
      startDate: '',
      endDate: '',
      description: ''
    },
    schedules: [],
    assessments: [],
    grading: {
      gradeScale: 'percentage',
      minScore: 0,
      maxScore: 100,
      passingScore: 60,
      gradeBoundaries: {}
    },
    holidays: []
  })
  const [isLoading, setIsLoading] = useState(false)
  const [sessionId, setSessionId] = useState<number | null>(null)

  // Initialize wizard session
  useEffect(() => {
    const initializeWizard = async () => {
      try {
        // Create a new term first, then start wizard session
        setSessionId(1) // Mock session ID
      } catch (err) {
        console.error('Failed to initialize wizard:', err)
        error('Failed to initialize term wizard')
      }
    }

    initializeWizard()
  }, [error])

  const updateTermData = (section: keyof TermData, data: any) => {
    setTermData(prev => ({
      ...prev,
      [section]: data
    }))
  }

  const addSchedule = () => {
    const newSchedule = {
      className: '',
      subjectName: '',
      teacherId: 0,
      dayOfWeek: 'monday',
      startTime: '',
      endTime: '',
      room: ''
    }
    updateTermData('schedules', [...termData.schedules, newSchedule])
  }

  const removeSchedule = (index: number) => {
    const updated = termData.schedules.filter((_, i) => i !== index)
    updateTermData('schedules', updated)
  }

  const updateSchedule = (index: number, field: string, value: any) => {
    const updated = termData.schedules.map((schedule, i) =>
      i === index ? { ...schedule, [field]: value } : schedule
    )
    updateTermData('schedules', updated)
  }

  const addAssessment = () => {
    const newAssessment = {
      type: 'quiz',
      name: '',
      weightPercentage: 0,
      description: '',
      isRequired: true
    }
    updateTermData('assessments', [...termData.assessments, newAssessment])
  }

  const removeAssessment = (index: number) => {
    const updated = termData.assessments.filter((_, i) => i !== index)
    updateTermData('assessments', updated)
  }

  const updateAssessment = (index: number, field: string, value: any) => {
    const updated = termData.assessments.map((assessment, i) =>
      i === index ? { ...assessment, [field]: value } : assessment
    )
    updateTermData('assessments', updated)
  }

  const addHoliday = () => {
    const newHoliday = {
      name: '',
      startDate: '',
      endDate: '',
      description: ''
    }
    updateTermData('holidays', [...termData.holidays, newHoliday])
  }

  const removeHoliday = (index: number) => {
    const updated = termData.holidays.filter((_, i) => i !== index)
    updateTermData('holidays', updated)
  }

  const updateHoliday = (index: number, field: string, value: any) => {
    const updated = termData.holidays.map((holiday, i) =>
      i === index ? { ...holiday, [field]: value } : holiday
    )
    updateTermData('holidays', updated)
  }

  const validateCurrentStep = (): boolean => {
    const step = WIZARD_STEPS[currentStep]
    
    switch (step.id) {
      case 'basic_info':
        return !!(termData.basicInfo.name && 
                 termData.basicInfo.academicYear && 
                 termData.basicInfo.startDate && 
                 termData.basicInfo.endDate)
      
      case 'schedule':
        return termData.schedules.length > 0 && 
               termData.schedules.every(s => s.className && s.subjectName && s.startTime && s.endTime)
      
      case 'assessment':
        const totalWeight = termData.assessments.reduce((sum, a) => sum + a.weightPercentage, 0)
        return termData.assessments.length > 0 && totalWeight === 100
      
      case 'grading':
        return termData.grading.maxScore > termData.grading.minScore &&
               termData.grading.passingScore >= termData.grading.minScore &&
               termData.grading.passingScore <= termData.grading.maxScore
      
      default:
        return true
    }
  }

  const nextStep = async () => {
    if (!validateCurrentStep()) {
      error('Please complete all required fields')
      return
    }

    const stepId = WIZARD_STEPS[currentStep].id
    if (!completedSteps.includes(stepId)) {
      setCompletedSteps(prev => [...prev, stepId])
    }

    if (currentStep < WIZARD_STEPS.length - 1) {
      setCurrentStep(prev => prev + 1)
    }
  }

  const prevStep = () => {
    if (currentStep > 0) {
      setCurrentStep(prev => prev - 1)
    }
  }

  const completeTerm = async () => {
    setIsLoading(true)
    try {
      // API call to complete wizard and create term
      await new Promise(resolve => setTimeout(resolve, 2000)) // Mock delay
      
      success('Term created successfully!')
      // Redirect to terms list or dashboard
    } catch (err) {
      console.error('Failed to complete term setup:', err)
      error('Failed to create term')
    } finally {
      setIsLoading(false)
    }
  }

  const renderStepContent = () => {
    const step = WIZARD_STEPS[currentStep]

    switch (step.id) {
      case 'basic_info':
        return (
          <div className="space-y-6">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Term Name *
              </label>
              <input
                type="text"
                value={termData.basicInfo.name}
                onChange={(e) => updateTermData('basicInfo', { ...termData.basicInfo, name: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                placeholder="e.g., First Term 2024"
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Academic Year *
              </label>
              <input
                type="text"
                value={termData.basicInfo.academicYear}
                onChange={(e) => updateTermData('basicInfo', { ...termData.basicInfo, academicYear: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                placeholder="e.g., 2024/2025"
              />
            </div>
            
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Start Date *
                </label>
                <input
                  type="date"
                  value={termData.basicInfo.startDate}
                  onChange={(e) => updateTermData('basicInfo', { ...termData.basicInfo, startDate: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  End Date *
                </label>
                <input
                  type="date"
                  value={termData.basicInfo.endDate}
                  onChange={(e) => updateTermData('basicInfo', { ...termData.basicInfo, endDate: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                />
              </div>
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Description
              </label>
              <textarea
                value={termData.basicInfo.description}
                onChange={(e) => updateTermData('basicInfo', { ...termData.basicInfo, description: e.target.value })}
                rows={3}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                placeholder="Optional description for this term"
              />
            </div>
          </div>
        )

      case 'schedule':
        return (
          <div className="space-y-6">
            <div className="flex justify-between items-center">
              <h3 className="text-lg font-semibold">Class Schedules</h3>
              <button
                onClick={addSchedule}
                className="flex items-center px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
              >
                <PlusIcon className="w-4 h-4 mr-2" />
                Add Schedule
              </button>
            </div>
            
            {termData.schedules.map((schedule, index) => (
              <div key={index} className="border border-gray-200 rounded-lg p-4">
                <div className="flex justify-between items-start mb-4">
                  <h4 className="text-md font-medium">Schedule {index + 1}</h4>
                  <button
                    onClick={() => removeSchedule(index)}
                    className="text-red-600 hover:text-red-800"
                  >
                    <TrashIcon className="w-4 h-4" />
                  </button>
                </div>
                
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Class Name *
                    </label>
                    <input
                      type="text"
                      value={schedule.className}
                      onChange={(e) => updateSchedule(index, 'className', e.target.value)}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                      placeholder="e.g., SS1A"
                    />
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Subject *
                    </label>
                    <input
                      type="text"
                      value={schedule.subjectName}
                      onChange={(e) => updateSchedule(index, 'subjectName', e.target.value)}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                      placeholder="e.g., Mathematics"
                    />
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Day of Week *
                    </label>
                    <select
                      value={schedule.dayOfWeek}
                      onChange={(e) => updateSchedule(index, 'dayOfWeek', e.target.value)}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                    >
                      {DAYS_OF_WEEK.map(day => (
                        <option key={day} value={day}>
                          {day.charAt(0).toUpperCase() + day.slice(1)}
                        </option>
                      ))}
                    </select>
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Room
                    </label>
                    <input
                      type="text"
                      value={schedule.room}
                      onChange={(e) => updateSchedule(index, 'room', e.target.value)}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                      placeholder="e.g., Room 101"
                    />
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Start Time *
                    </label>
                    <input
                      type="time"
                      value={schedule.startTime}
                      onChange={(e) => updateSchedule(index, 'startTime', e.target.value)}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                    />
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      End Time *
                    </label>
                    <input
                      type="time"
                      value={schedule.endTime}
                      onChange={(e) => updateSchedule(index, 'endTime', e.target.value)}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                    />
                  </div>
                </div>
              </div>
            ))}
            
            {termData.schedules.length === 0 && (
              <div className="text-center py-8 text-gray-500">
                No schedules added yet. Click "Add Schedule" to get started.
              </div>
            )}
          </div>
        )

      case 'assessment':
        return (
          <div className="space-y-6">
            <div className="flex justify-between items-center">
              <div>
                <h3 className="text-lg font-semibold">Assessment Configuration</h3>
                <p className="text-sm text-gray-600">
                  Total weight: {termData.assessments.reduce((sum, a) => sum + a.weightPercentage, 0)}% (must equal 100%)
                </p>
              </div>
              <button
                onClick={addAssessment}
                className="flex items-center px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
              >
                <PlusIcon className="w-4 h-4 mr-2" />
                Add Assessment
              </button>
            </div>
            
            {termData.assessments.map((assessment, index) => (
              <div key={index} className="border border-gray-200 rounded-lg p-4">
                <div className="flex justify-between items-start mb-4">
                  <h4 className="text-md font-medium">Assessment {index + 1}</h4>
                  <button
                    onClick={() => removeAssessment(index)}
                    className="text-red-600 hover:text-red-800"
                  >
                    <TrashIcon className="w-4 h-4" />
                  </button>
                </div>
                
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Type *
                    </label>
                    <select
                      value={assessment.type}
                      onChange={(e) => updateAssessment(index, 'type', e.target.value)}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                    >
                      {ASSESSMENT_TYPES.map(type => (
                        <option key={type} value={type}>
                          {type.charAt(0).toUpperCase() + type.slice(1)}
                        </option>
                      ))}
                    </select>
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Name *
                    </label>
                    <input
                      type="text"
                      value={assessment.name}
                      onChange={(e) => updateAssessment(index, 'name', e.target.value)}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                      placeholder="e.g., Mid-term Exam"
                    />
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Weight (%) *
                    </label>
                    <input
                      type="number"
                      min="0"
                      max="100"
                      value={assessment.weightPercentage}
                      onChange={(e) => updateAssessment(index, 'weightPercentage', parseInt(e.target.value) || 0)}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                    />
                  </div>
                  
                  <div className="flex items-center">
                    <input
                      type="checkbox"
                      checked={assessment.isRequired}
                      onChange={(e) => updateAssessment(index, 'isRequired', e.target.checked)}
                      className="mr-2"
                    />
                    <label className="text-sm font-medium text-gray-700">
                      Required
                    </label>
                  </div>
                </div>
                
                <div className="mt-4">
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Description
                  </label>
                  <textarea
                    value={assessment.description}
                    onChange={(e) => updateAssessment(index, 'description', e.target.value)}
                    rows={2}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                    placeholder="Assessment description"
                  />
                </div>
              </div>
            ))}
            
            {termData.assessments.length === 0 && (
              <div className="text-center py-8 text-gray-500">
                No assessments configured yet. Click "Add Assessment" to get started.
              </div>
            )}
          </div>
        )

      case 'grading':
        return (
          <div className="space-y-6">
            <h3 className="text-lg font-semibold">Grading System Configuration</h3>
            
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Grade Scale *
                </label>
                <select
                  value={termData.grading.gradeScale}
                  onChange={(e) => updateTermData('grading', { ...termData.grading, gradeScale: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                >
                  {GRADE_SCALES.map(scale => (
                    <option key={scale} value={scale}>
                      {scale.charAt(0).toUpperCase() + scale.slice(1).replace('_', ' ')}
                    </option>
                  ))}
                </select>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Passing Score *
                </label>
                <input
                  type="number"
                  value={termData.grading.passingScore}
                  onChange={(e) => updateTermData('grading', { ...termData.grading, passingScore: parseInt(e.target.value) || 0 })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Minimum Score *
                </label>
                <input
                  type="number"
                  value={termData.grading.minScore}
                  onChange={(e) => updateTermData('grading', { ...termData.grading, minScore: parseInt(e.target.value) || 0 })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Maximum Score *
                </label>
                <input
                  type="number"
                  value={termData.grading.maxScore}
                  onChange={(e) => updateTermData('grading', { ...termData.grading, maxScore: parseInt(e.target.value) || 100 })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                />
              </div>
            </div>
          </div>
        )

      case 'holidays':
        return (
          <div className="space-y-6">
            <div className="flex justify-between items-center">
              <h3 className="text-lg font-semibold">Holidays & Breaks</h3>
              <button
                onClick={addHoliday}
                className="flex items-center px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
              >
                <PlusIcon className="w-4 h-4 mr-2" />
                Add Holiday
              </button>
            </div>
            
            {termData.holidays.map((holiday, index) => (
              <div key={index} className="border border-gray-200 rounded-lg p-4">
                <div className="flex justify-between items-start mb-4">
                  <h4 className="text-md font-medium">Holiday {index + 1}</h4>
                  <button
                    onClick={() => removeHoliday(index)}
                    className="text-red-600 hover:text-red-800"
                  >
                    <TrashIcon className="w-4 h-4" />
                  </button>
                </div>
                
                <div className="grid grid-cols-2 gap-4">
                  <div className="col-span-2">
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Holiday Name *
                    </label>
                    <input
                      type="text"
                      value={holiday.name}
                      onChange={(e) => updateHoliday(index, 'name', e.target.value)}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                      placeholder="e.g., Christmas Break"
                    />
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Start Date *
                    </label>
                    <input
                      type="date"
                      value={holiday.startDate}
                      onChange={(e) => updateHoliday(index, 'startDate', e.target.value)}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                    />
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      End Date *
                    </label>
                    <input
                      type="date"
                      value={holiday.endDate}
                      onChange={(e) => updateHoliday(index, 'endDate', e.target.value)}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                    />
                  </div>
                  
                  <div className="col-span-2">
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Description
                    </label>
                    <textarea
                      value={holiday.description}
                      onChange={(e) => updateHoliday(index, 'description', e.target.value)}
                      rows={2}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                      placeholder="Holiday description"
                    />
                  </div>
                </div>
              </div>
            ))}
            
            {termData.holidays.length === 0 && (
              <div className="text-center py-8 text-gray-500">
                No holidays configured yet. Click "Add Holiday" to get started.
              </div>
            )}
          </div>
        )

      case 'review':
        return (
          <div className="space-y-6">
            <h3 className="text-lg font-semibold">Review Term Configuration</h3>
            
            <div className="bg-gray-50 rounded-lg p-4">
              <h4 className="font-medium mb-2">Basic Information</h4>
              <div className="text-sm text-gray-600 space-y-1">
                <p><strong>Name:</strong> {termData.basicInfo.name}</p>
                <p><strong>Academic Year:</strong> {termData.basicInfo.academicYear}</p>
                <p><strong>Duration:</strong> {termData.basicInfo.startDate} to {termData.basicInfo.endDate}</p>
                {termData.basicInfo.description && (
                  <p><strong>Description:</strong> {termData.basicInfo.description}</p>
                )}
              </div>
            </div>
            
            <div className="bg-gray-50 rounded-lg p-4">
              <h4 className="font-medium mb-2">Schedules</h4>
              <p className="text-sm text-gray-600">{termData.schedules.length} class schedules configured</p>
            </div>
            
            <div className="bg-gray-50 rounded-lg p-4">
              <h4 className="font-medium mb-2">Assessments</h4>
              <p className="text-sm text-gray-600">
                {termData.assessments.length} assessments configured 
                (Total weight: {termData.assessments.reduce((sum, a) => sum + a.weightPercentage, 0)}%)
              </p>
            </div>
            
            <div className="bg-gray-50 rounded-lg p-4">
              <h4 className="font-medium mb-2">Grading System</h4>
              <div className="text-sm text-gray-600 space-y-1">
                <p><strong>Scale:</strong> {termData.grading.gradeScale}</p>
                <p><strong>Score Range:</strong> {termData.grading.minScore} - {termData.grading.maxScore}</p>
                <p><strong>Passing Score:</strong> {termData.grading.passingScore}</p>
              </div>
            </div>
            
            <div className="bg-gray-50 rounded-lg p-4">
              <h4 className="font-medium mb-2">Holidays</h4>
              <p className="text-sm text-gray-600">{termData.holidays.length} holidays configured</p>
            </div>
          </div>
        )

      default:
        return <div>Step content not implemented</div>
    }
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 py-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Term Setup Wizard</h1>
          <p className="text-gray-600 mt-2">Set up a new academic term with guided configuration</p>
        </div>

        <div className="grid grid-cols-12 gap-8">
          {/* Sidebar - Steps */}
          <div className="col-span-3">
            <div className="bg-white rounded-lg shadow p-6 sticky top-8">
              <h3 className="font-semibold mb-4">Setup Progress</h3>
              <div className="space-y-4">
                {WIZARD_STEPS.map((step, index) => {
                  const Icon = step.icon
                  const isCompleted = completedSteps.includes(step.id)
                  const isCurrent = index === currentStep
                  
                  return (
                    <div
                      key={step.id}
                      className={`flex items-start p-3 rounded-lg transition-colors ${
                        isCurrent
                          ? 'bg-blue-50 border-l-4 border-blue-500'
                          : isCompleted
                          ? 'bg-green-50'
                          : 'hover:bg-gray-50'
                      }`}
                    >
                      <div className={`flex-shrink-0 mr-3 ${
                        isCurrent
                          ? 'text-blue-600'
                          : isCompleted
                          ? 'text-green-600'
                          : 'text-gray-400'
                      }`}>
                        {isCompleted ? (
                          <CheckCircleIcon className="w-5 h-5" />
                        ) : (
                          <Icon className="w-5 h-5" />
                        )}
                      </div>
                      <div>
                        <div className={`text-sm font-medium ${
                          isCurrent ? 'text-blue-900' : isCompleted ? 'text-green-900' : 'text-gray-700'
                        }`}>
                          {step.name}
                        </div>
                        <div className="text-xs text-gray-500 mt-1">
                          {step.description}
                        </div>
                      </div>
                    </div>
                  )
                })}
              </div>
            </div>
          </div>

          {/* Main Content */}
          <div className="col-span-9">
            <div className="bg-white rounded-lg shadow">
              {/* Step Header */}
              <div className="border-b border-gray-200 p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <h2 className="text-xl font-semibold text-gray-900">
                      {WIZARD_STEPS[currentStep].name}
                    </h2>
                    <p className="text-gray-600 mt-1">
                      {WIZARD_STEPS[currentStep].description}
                    </p>
                  </div>
                  <div className="text-sm text-gray-500">
                    Step {currentStep + 1} of {WIZARD_STEPS.length}
                  </div>
                </div>
              </div>

              {/* Step Content */}
              <div className="p-6">
                <AnimatePresence mode="wait">
                  <motion.div
                    key={currentStep}
                    initial={{ opacity: 0, x: 20 }}
                    animate={{ opacity: 1, x: 0 }}
                    exit={{ opacity: 0, x: -20 }}
                    transition={{ duration: 0.2 }}
                  >
                    {renderStepContent()}
                  </motion.div>
                </AnimatePresence>
              </div>

              {/* Navigation */}
              <div className="border-t border-gray-200 p-6">
                <div className="flex justify-between">
                  <button
                    onClick={prevStep}
                    disabled={currentStep === 0}
                    className="flex items-center px-4 py-2 text-gray-600 hover:text-gray-800 disabled:text-gray-400 disabled:cursor-not-allowed"
                  >
                    <ArrowLeftIcon className="w-4 h-4 mr-2" />
                    Previous
                  </button>

                  {currentStep === WIZARD_STEPS.length - 1 ? (
                    <button
                      onClick={completeTerm}
                      disabled={isLoading}
                      className="flex items-center px-6 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 disabled:opacity-50"
                    >
                      {isLoading ? 'Creating...' : 'Complete Setup'}
                    </button>
                  ) : (
                    <button
                      onClick={nextStep}
                      className="flex items-center px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
                    >
                      Next
                      <ArrowRightIcon className="w-4 h-4 ml-2" />
                    </button>
                  )}
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
