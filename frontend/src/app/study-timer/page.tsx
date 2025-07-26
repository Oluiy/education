'use client'

import { useState, useEffect, useRef } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { useAuth } from '@/contexts/AuthContext'
import { useToast } from '@/contexts/ToastContext'
import {
  PlayIcon,
  PauseIcon,
  StopIcon,
  ClockIcon,
  AcademicCapIcon,
  ChartBarIcon,
  CogIcon,
  BookOpenIcon,
  CheckCircleIcon,
  FireIcon
} from '@heroicons/react/24/outline'

interface StudySession {
  id: string
  subject: string
  duration: number
  completedAt: string
  type: 'focus' | 'short_break' | 'long_break'
}

interface PomodoroSettings {
  focusDuration: number
  shortBreakDuration: number
  longBreakDuration: number
  sessionsUntilLongBreak: number
  autoStartBreaks: boolean
  autoStartPomodoros: boolean
  soundEnabled: boolean
}

const DEFAULT_SETTINGS: PomodoroSettings = {
  focusDuration: 25,
  shortBreakDuration: 5,
  longBreakDuration: 15,
  sessionsUntilLongBreak: 4,
  autoStartBreaks: false,
  autoStartPomodoros: false,
  soundEnabled: true
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
  'Literature',
  'Further Mathematics',
  'General Studies'
]

export default function StudyTimer() {
  const [timeLeft, setTimeLeft] = useState(25 * 60) // 25 minutes in seconds
  const [isActive, setIsActive] = useState(false)
  const [isPaused, setIsPaused] = useState(false)
  const [currentSession, setCurrentSession] = useState<'focus' | 'short_break' | 'long_break'>('focus')
  const [sessionCount, setSessionCount] = useState(0)
  const [completedSessions, setCompletedSessions] = useState<StudySession[]>([])
  const [selectedSubject, setSelectedSubject] = useState(SUBJECTS[0])
  const [settings, setSettings] = useState<PomodoroSettings>(DEFAULT_SETTINGS)
  const [showSettings, setShowSettings] = useState(false)
  const [todayStats, setTodayStats] = useState({
    totalFocusTime: 0,
    completedPomodoros: 0,
    totalBreakTime: 0,
    streak: 0
  })

  const { user } = useAuth()
  const { success: showSuccess, info: showInfo } = useToast()
  const intervalRef = useRef<NodeJS.Timeout | null>(null)
  const audioRef = useRef<HTMLAudioElement | null>(null)

  useEffect(() => {
    // Load saved settings and sessions from localStorage
    const savedSettings = localStorage.getItem('pomodoroSettings')
    if (savedSettings) {
      setSettings(JSON.parse(savedSettings))
    }

    const savedSessions = localStorage.getItem('studySessions')
    if (savedSessions) {
      const sessions = JSON.parse(savedSessions)
      setCompletedSessions(sessions)
      calculateTodayStats(sessions)
    }

    // Initialize audio
    audioRef.current = new Audio('/sounds/notification.mp3')
  }, [])

  useEffect(() => {
    if (isActive && !isPaused) {
      intervalRef.current = setInterval(() => {
        setTimeLeft((time) => {
          if (time <= 1) {
            handleSessionComplete()
            return 0
          }
          return time - 1
        })
      }, 1000)
    } else {
      if (intervalRef.current) {
        clearInterval(intervalRef.current)
      }
    }

    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current)
      }
    }
  }, [isActive, isPaused])

  const calculateTodayStats = (sessions: StudySession[]) => {
    const today = new Date().toDateString()
    const todaySessions = sessions.filter(
      session => new Date(session.completedAt).toDateString() === today
    )

    const stats = {
      totalFocusTime: todaySessions
        .filter(s => s.type === 'focus')
        .reduce((total, s) => total + s.duration, 0),
      completedPomodoros: todaySessions.filter(s => s.type === 'focus').length,
      totalBreakTime: todaySessions
        .filter(s => s.type !== 'focus')
        .reduce((total, s) => total + s.duration, 0),
      streak: calculateStreak(sessions)
    }

    setTodayStats(stats)
  }

  const calculateStreak = (sessions: StudySession[]) => {
    // Calculate consecutive days with completed pomodoros
    let streak = 0
    let currentDate = new Date()
    
    while (true) {
      const dateStr = currentDate.toDateString()
      const dayHasSession = sessions.some(
        session => new Date(session.completedAt).toDateString() === dateStr && session.type === 'focus'
      )
      
      if (dayHasSession) {
        streak++
        currentDate.setDate(currentDate.getDate() - 1)
      } else {
        break
      }
    }
    
    return streak
  }

  const handleSessionComplete = () => {
    setIsActive(false)
    setIsPaused(false)

    // Play notification sound
    if (settings.soundEnabled && audioRef.current) {
      audioRef.current.play().catch(console.error)
    }

    // Save completed session
    const session: StudySession = {
      id: Date.now().toString(),
      subject: selectedSubject,
      duration: getCurrentSessionDuration(),
      completedAt: new Date().toISOString(),
      type: currentSession
    }

    const newSessions = [...completedSessions, session]
    setCompletedSessions(newSessions)
    localStorage.setItem('studySessions', JSON.stringify(newSessions))
    calculateTodayStats(newSessions)

    // Show completion message
    if (currentSession === 'focus') {
      setSessionCount(prev => prev + 1)
      showSuccess(`Pomodoro completed! Great work on ${selectedSubject}`)
    } else {
      showInfo('Break completed! Ready for another pomodoro?')
    }

    // Determine next session type
    if (currentSession === 'focus') {
      const nextSessionCount = sessionCount + 1
      if (nextSessionCount % settings.sessionsUntilLongBreak === 0) {
        setCurrentSession('long_break')
        setTimeLeft(settings.longBreakDuration * 60)
      } else {
        setCurrentSession('short_break')
        setTimeLeft(settings.shortBreakDuration * 60)
      }
      
      if (settings.autoStartBreaks) {
        setIsActive(true)
      }
    } else {
      setCurrentSession('focus')
      setTimeLeft(settings.focusDuration * 60)
      
      if (settings.autoStartPomodoros) {
        setIsActive(true)
      }
    }
  }

  const getCurrentSessionDuration = () => {
    switch (currentSession) {
      case 'focus':
        return settings.focusDuration
      case 'short_break':
        return settings.shortBreakDuration
      case 'long_break':
        return settings.longBreakDuration
      default:
        return 25
    }
  }

  const handleStart = () => {
    setIsActive(true)
    setIsPaused(false)
  }

  const handlePause = () => {
    setIsPaused(!isPaused)
  }

  const handleStop = () => {
    setIsActive(false)
    setIsPaused(false)
    setCurrentSession('focus')
    setTimeLeft(settings.focusDuration * 60)
  }

  const handleSettingsChange = (newSettings: PomodoroSettings) => {
    setSettings(newSettings)
    localStorage.setItem('pomodoroSettings', JSON.stringify(newSettings))
    
    // Update current timer if not active
    if (!isActive) {
      setTimeLeft(newSettings.focusDuration * 60)
    }
  }

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60)
    const secs = seconds % 60
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`
  }

  const getSessionTitle = () => {
    switch (currentSession) {
      case 'focus':
        return 'Focus Time'
      case 'short_break':
        return 'Short Break'
      case 'long_break':
        return 'Long Break'
    }
  }

  const getSessionColor = () => {
    switch (currentSession) {
      case 'focus':
        return 'from-red-500 to-pink-500'
      case 'short_break':
        return 'from-green-500 to-emerald-500'
      case 'long_break':
        return 'from-blue-500 to-purple-500'
    }
  }

  const progressPercentage = ((getCurrentSessionDuration() * 60 - timeLeft) / (getCurrentSessionDuration() * 60)) * 100

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="text-center mb-8">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="inline-flex items-center space-x-2 bg-red-100 text-red-800 px-4 py-2 rounded-full text-sm font-medium mb-4"
          >
            <ClockIcon className="w-4 h-4" />
            <span>Pomodoro Timer</span>
          </motion.div>
          
          <motion.h1
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
            className="text-3xl font-bold text-gray-900 mb-2"
          >
            Study Timer
          </motion.h1>
          
          <motion.p
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
            className="text-lg text-gray-600"
          >
            Use the Pomodoro Technique to boost your focus and productivity
          </motion.p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Timer Section */}
          <div className="lg:col-span-2">
            <motion.div
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              className="bg-white rounded-2xl shadow-lg p-8 text-center"
            >
              {/* Session Type */}
              <div className={`inline-block px-6 py-2 rounded-full text-white font-semibold mb-6 bg-gradient-to-r ${getSessionColor()}`}>
                {getSessionTitle()}
              </div>

              {/* Subject Selection (only during focus) */}
              {currentSession === 'focus' && (
                <div className="mb-6">
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Current Subject
                  </label>
                  <select
                    value={selectedSubject}
                    onChange={(e) => setSelectedSubject(e.target.value)}
                    disabled={isActive}
                    className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500 focus:border-transparent disabled:opacity-50"
                  >
                    {SUBJECTS.map(subject => (
                      <option key={subject} value={subject}>{subject}</option>
                    ))}
                  </select>
                </div>
              )}

              {/* Timer Display */}
              <div className="relative mb-8">
                <svg className="w-64 h-64 mx-auto transform -rotate-90" viewBox="0 0 100 100">
                  <circle
                    cx="50"
                    cy="50"
                    r="45"
                    stroke="currentColor"
                    strokeWidth="2"
                    fill="none"
                    className="text-gray-200"
                  />
                  <circle
                    cx="50"
                    cy="50"
                    r="45"
                    stroke="currentColor"
                    strokeWidth="2"
                    fill="none"
                    strokeDasharray={`${2 * Math.PI * 45}`}
                    strokeDashoffset={`${2 * Math.PI * 45 * (1 - progressPercentage / 100)}`}
                    className={currentSession === 'focus' ? 'text-red-500' : currentSession === 'short_break' ? 'text-green-500' : 'text-blue-500'}
                    style={{ transition: 'stroke-dashoffset 1s linear' }}
                  />
                </svg>
                <div className="absolute inset-0 flex items-center justify-center">
                  <div className="text-center">
                    <div className="text-4xl font-bold text-gray-900 mb-2">
                      {formatTime(timeLeft)}
                    </div>
                    <div className="text-sm text-gray-600">
                      {currentSession === 'focus' ? selectedSubject : 'Take a break'}
                    </div>
                  </div>
                </div>
              </div>

              {/* Controls */}
              <div className="flex items-center justify-center space-x-4">
                {!isActive ? (
                  <button
                    onClick={handleStart}
                    className="flex items-center space-x-2 px-8 py-3 bg-red-600 text-white rounded-lg font-medium hover:bg-red-700 transition-colors"
                  >
                    <PlayIcon className="w-5 h-5" />
                    <span>Start</span>
                  </button>
                ) : (
                  <button
                    onClick={handlePause}
                    className="flex items-center space-x-2 px-8 py-3 bg-yellow-600 text-white rounded-lg font-medium hover:bg-yellow-700 transition-colors"
                  >
                    <PauseIcon className="w-5 h-5" />
                    <span>{isPaused ? 'Resume' : 'Pause'}</span>
                  </button>
                )}
                
                <button
                  onClick={handleStop}
                  className="flex items-center space-x-2 px-6 py-3 bg-gray-600 text-white rounded-lg font-medium hover:bg-gray-700 transition-colors"
                >
                  <StopIcon className="w-5 h-5" />
                  <span>Stop</span>
                </button>
                
                <button
                  onClick={() => setShowSettings(!showSettings)}
                  className="flex items-center space-x-2 px-6 py-3 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700 transition-colors"
                >
                  <CogIcon className="w-5 h-5" />
                  <span>Settings</span>
                </button>
              </div>

              {/* Session Progress */}
              <div className="mt-6 flex items-center justify-center space-x-2">
                {Array.from({ length: settings.sessionsUntilLongBreak }).map((_, index) => (
                  <div
                    key={index}
                    className={`w-3 h-3 rounded-full ${
                      index < sessionCount % settings.sessionsUntilLongBreak
                        ? 'bg-red-500'
                        : 'bg-gray-200'
                    }`}
                  />
                ))}
              </div>
            </motion.div>

            {/* Settings Panel */}
            <AnimatePresence>
              {showSettings && (
                <motion.div
                  initial={{ opacity: 0, height: 0 }}
                  animate={{ opacity: 1, height: 'auto' }}
                  exit={{ opacity: 0, height: 0 }}
                  className="mt-6 bg-white rounded-2xl shadow-lg p-6"
                >
                  <h3 className="text-lg font-semibold text-gray-900 mb-4">Timer Settings</h3>
                  
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        Focus Duration (minutes)
                      </label>
                      <input
                        type="number"
                        min="1"
                        max="60"
                        value={settings.focusDuration}
                        onChange={(e) => handleSettingsChange({
                          ...settings,
                          focusDuration: parseInt(e.target.value) || 25
                        })}
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500"
                      />
                    </div>
                    
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        Short Break (minutes)
                      </label>
                      <input
                        type="number"
                        min="1"
                        max="30"
                        value={settings.shortBreakDuration}
                        onChange={(e) => handleSettingsChange({
                          ...settings,
                          shortBreakDuration: parseInt(e.target.value) || 5
                        })}
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500"
                      />
                    </div>
                    
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        Long Break (minutes)
                      </label>
                      <input
                        type="number"
                        min="1"
                        max="60"
                        value={settings.longBreakDuration}
                        onChange={(e) => handleSettingsChange({
                          ...settings,
                          longBreakDuration: parseInt(e.target.value) || 15
                        })}
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                      />
                    </div>
                    
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        Sessions until Long Break
                      </label>
                      <input
                        type="number"
                        min="2"
                        max="8"
                        value={settings.sessionsUntilLongBreak}
                        onChange={(e) => handleSettingsChange({
                          ...settings,
                          sessionsUntilLongBreak: parseInt(e.target.value) || 4
                        })}
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500"
                      />
                    </div>
                  </div>
                  
                  <div className="mt-4 space-y-3">
                    <label className="flex items-center">
                      <input
                        type="checkbox"
                        checked={settings.autoStartBreaks}
                        onChange={(e) => handleSettingsChange({
                          ...settings,
                          autoStartBreaks: e.target.checked
                        })}
                        className="mr-2"
                      />
                      <span className="text-sm text-gray-700">Auto-start breaks</span>
                    </label>
                    
                    <label className="flex items-center">
                      <input
                        type="checkbox"
                        checked={settings.autoStartPomodoros}
                        onChange={(e) => handleSettingsChange({
                          ...settings,
                          autoStartPomodoros: e.target.checked
                        })}
                        className="mr-2"
                      />
                      <span className="text-sm text-gray-700">Auto-start pomodoros</span>
                    </label>
                    
                    <label className="flex items-center">
                      <input
                        type="checkbox"
                        checked={settings.soundEnabled}
                        onChange={(e) => handleSettingsChange({
                          ...settings,
                          soundEnabled: e.target.checked
                        })}
                        className="mr-2"
                      />
                      <span className="text-sm text-gray-700">Sound notifications</span>
                    </label>
                  </div>
                </motion.div>
              )}
            </AnimatePresence>
          </div>

          {/* Stats & History */}
          <div className="space-y-6">
            {/* Today's Stats */}
            <motion.div
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              className="bg-white rounded-2xl shadow-lg p-6"
            >
              <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
                <ChartBarIcon className="w-5 h-5 mr-2" />
                Today's Progress
              </h3>
              
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-2">
                    <CheckCircleIcon className="w-5 h-5 text-red-500" />
                    <span className="text-sm text-gray-600">Completed Pomodoros</span>
                  </div>
                  <span className="font-semibold text-gray-900">{todayStats.completedPomodoros}</span>
                </div>
                
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-2">
                    <ClockIcon className="w-5 h-5 text-blue-500" />
                    <span className="text-sm text-gray-600">Focus Time</span>
                  </div>
                  <span className="font-semibold text-gray-900">{Math.round(todayStats.totalFocusTime / 60)}m</span>
                </div>
                
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-2">
                    <FireIcon className="w-5 h-5 text-orange-500" />
                    <span className="text-sm text-gray-600">Streak</span>
                  </div>
                  <span className="font-semibold text-gray-900">{todayStats.streak} days</span>
                </div>
              </div>
            </motion.div>

            {/* Recent Sessions */}
            <motion.div
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.1 }}
              className="bg-white rounded-2xl shadow-lg p-6"
            >
              <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
                <BookOpenIcon className="w-5 h-5 mr-2" />
                Recent Sessions
              </h3>
              
              <div className="space-y-3 max-h-64 overflow-y-auto">
                {completedSessions.slice(-10).reverse().map((session) => (
                  <div key={session.id} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                    <div>
                      <div className="font-medium text-gray-900">{session.subject}</div>
                      <div className="text-sm text-gray-600">
                        {session.duration}m • {new Date(session.completedAt).toLocaleTimeString()}
                      </div>
                    </div>
                    <div className={`w-3 h-3 rounded-full ${
                      session.type === 'focus' ? 'bg-red-500' : 
                      session.type === 'short_break' ? 'bg-green-500' : 'bg-blue-500'
                    }`} />
                  </div>
                ))}
                
                {completedSessions.length === 0 && (
                  <div className="text-center py-8 text-gray-500">
                    <ClockIcon className="w-12 h-12 mx-auto mb-2 opacity-50" />
                    <p>No sessions yet. Start your first pomodoro!</p>
                  </div>
                )}
              </div>
            </motion.div>
          </div>
        </div>
      </div>
    </div>
  )
}
