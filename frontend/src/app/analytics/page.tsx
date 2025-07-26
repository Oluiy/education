'use client'

import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { useAuth } from '@/contexts/AuthContext'
import {
  ChartBarIcon,
  TrophyIcon,
  ClockIcon,
  BookOpenIcon,
  AcademicCapIcon,
  FireIcon,
  CalendarDaysIcon,
  ArrowTrendingUpIcon,
  ArrowTrendingDownIcon,
  CheckCircleIcon,
  XCircleIcon
} from '@heroicons/react/24/outline'

interface StudyStats {
  totalStudyTime: number
  streakDays: number
  completedQuizzes: number
  averageScore: number
  subjectProgress: { [key: string]: number }
  weeklyProgress: { day: string; hours: number; score: number }[]
  monthlyGoals: {
    studyHours: { current: number; target: number }
    quizzes: { current: number; target: number }
    subjects: { current: number; target: number }
  }
  achievements: Achievement[]
  recentActivity: Activity[]
}

interface Achievement {
  id: string
  title: string
  description: string
  icon: string
  unlockedAt: Date
  type: 'study_time' | 'quiz_score' | 'streak' | 'subject_mastery'
}

interface Activity {
  id: string
  type: 'quiz_completed' | 'study_session' | 'achievement_unlocked' | 'goal_reached'
  title: string
  description: string
  timestamp: Date
  metadata?: {
    score?: number
    duration?: number
    subject?: string
  }
}

const SUBJECTS = ['Mathematics', 'Physics', 'Chemistry', 'Biology', 'English', 'History']

const ACHIEVEMENTS_DATA: Achievement[] = [
  {
    id: '1',
    title: 'First Steps',
    description: 'Complete your first quiz',
    icon: '🎯',
    unlockedAt: new Date(Date.now() - 7 * 24 * 60 * 60 * 1000),
    type: 'quiz_score'
  },
  {
    id: '2',
    title: 'Study Streak',
    description: 'Study for 7 consecutive days',
    icon: '🔥',
    unlockedAt: new Date(Date.now() - 5 * 24 * 60 * 60 * 1000),
    type: 'streak'
  },
  {
    id: '3',
    title: 'Math Master',
    description: 'Score 90% or higher in 5 Mathematics quizzes',
    icon: '📐',
    unlockedAt: new Date(Date.now() - 3 * 24 * 60 * 60 * 1000),
    type: 'subject_mastery'
  },
  {
    id: '4',
    title: 'Time Champion',
    description: 'Study for 50 hours total',
    icon: '⏰',
    unlockedAt: new Date(Date.now() - 2 * 24 * 60 * 60 * 1000),
    type: 'study_time'
  }
]

export default function ProgressAnalytics() {
  const [stats, setStats] = useState<StudyStats | null>(null)
  const [selectedTimeframe, setSelectedTimeframe] = useState<'week' | 'month' | 'year'>('week')
  const [selectedSubject, setSelectedSubject] = useState<string>('all')
  const [isLoading, setIsLoading] = useState(true)

  const { user } = useAuth()

  useEffect(() => {
    loadAnalytics()
  }, [selectedTimeframe, selectedSubject])

  const loadAnalytics = async () => {
    setIsLoading(true)
    
    // Simulate API call
    await new Promise(resolve => setTimeout(resolve, 1000))
    
    const mockStats: StudyStats = {
      totalStudyTime: 47.5,
      streakDays: 12,
      completedQuizzes: 23,
      averageScore: 84.2,
      subjectProgress: {
        'Mathematics': 92,
        'Physics': 78,
        'Chemistry': 85,
        'Biology': 69,
        'English': 88,
        'History': 74
      },
      weeklyProgress: [
        { day: 'Mon', hours: 2.5, score: 88 },
        { day: 'Tue', hours: 3.2, score: 92 },
        { day: 'Wed', hours: 1.8, score: 76 },
        { day: 'Thu', hours: 4.1, score: 89 },
        { day: 'Fri', hours: 2.9, score: 85 },
        { day: 'Sat', hours: 3.7, score: 91 },
        { day: 'Sun', hours: 2.1, score: 82 }
      ],
      monthlyGoals: {
        studyHours: { current: 47.5, target: 60 },
        quizzes: { current: 23, target: 30 },
        subjects: { current: 4, target: 6 }
      },
      achievements: ACHIEVEMENTS_DATA,
      recentActivity: [
        {
          id: '1',
          type: 'quiz_completed',
          title: 'Physics Quiz Completed',
          description: 'Electricity and Magnetism',
          timestamp: new Date(Date.now() - 2 * 60 * 60 * 1000),
          metadata: { score: 92, subject: 'Physics' }
        },
        {
          id: '2',
          type: 'achievement_unlocked',
          title: 'Achievement Unlocked: Time Champion',
          description: 'Studied for 50 hours total',
          timestamp: new Date(Date.now() - 4 * 60 * 60 * 1000)
        },
        {
          id: '3',
          type: 'study_session',
          title: 'Study Session Completed',
          description: 'Mathematics - Calculus',
          timestamp: new Date(Date.now() - 6 * 60 * 60 * 1000),
          metadata: { duration: 45, subject: 'Mathematics' }
        },
        {
          id: '4',
          type: 'quiz_completed',
          title: 'Chemistry Quiz Completed',
          description: 'Organic Chemistry',
          timestamp: new Date(Date.now() - 8 * 60 * 60 * 1000),
          metadata: { score: 87, subject: 'Chemistry' }
        }
      ]
    }
    
    setStats(mockStats)
    setIsLoading(false)
  }

  const getProgressColor = (percentage: number): string => {
    if (percentage >= 90) return 'text-green-600 bg-green-100'
    if (percentage >= 70) return 'text-yellow-600 bg-yellow-100'
    return 'text-red-600 bg-red-100'
  }

  const getProgressBarColor = (percentage: number): string => {
    if (percentage >= 90) return 'bg-green-500'
    if (percentage >= 70) return 'bg-yellow-500'
    return 'bg-red-500'
  }

  const getTrendIcon = (current: number, target: number) => {
    const percentage = (current / target) * 100
    if (percentage >= 80) {
      return <ArrowTrendingUpIcon className="w-4 h-4 text-green-500" />
    }
    return <ArrowTrendingDownIcon className="w-4 h-4 text-red-500" />
  }

  const getActivityIcon = (type: string) => {
    switch (type) {
      case 'quiz_completed':
        return <CheckCircleIcon className="w-4 h-4 text-green-500" />
      case 'achievement_unlocked':
        return <TrophyIcon className="w-4 h-4 text-yellow-500" />
      case 'study_session':
        return <ClockIcon className="w-4 h-4 text-blue-500" />
      case 'goal_reached':
        return <FireIcon className="w-4 h-4 text-orange-500" />
      default:
        return <BookOpenIcon className="w-4 h-4 text-gray-500" />
    }
  }

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading your progress...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center justify-between">
            <div>
              <motion.h1
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                className="text-3xl font-bold text-gray-900"
              >
                Progress Analytics
              </motion.h1>
              <motion.p
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.1 }}
                className="text-gray-600 mt-1"
              >
                Track your learning journey and celebrate achievements
              </motion.p>
            </div>
            
            <div className="flex space-x-3">
              <select
                value={selectedTimeframe}
                onChange={(e) => setSelectedTimeframe(e.target.value as any)}
                className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500"
              >
                <option value="week">This Week</option>
                <option value="month">This Month</option>
                <option value="year">This Year</option>
              </select>
              
              <select
                value={selectedSubject}
                onChange={(e) => setSelectedSubject(e.target.value)}
                className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500"
              >
                <option value="all">All Subjects</option>
                {SUBJECTS.map(subject => (
                  <option key={subject} value={subject}>{subject}</option>
                ))}
              </select>
            </div>
          </div>
        </div>

        {/* Key Metrics */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="bg-white rounded-2xl shadow-lg p-6"
          >
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Total Study Time</p>
                <p className="text-2xl font-bold text-gray-900">{stats?.totalStudyTime}h</p>
                <p className="text-sm text-green-600 mt-1">+12% this week</p>
              </div>
              <div className="p-3 bg-blue-100 rounded-full">
                <ClockIcon className="w-6 h-6 text-blue-600" />
              </div>
            </div>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
            className="bg-white rounded-2xl shadow-lg p-6"
          >
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Current Streak</p>
                <p className="text-2xl font-bold text-gray-900">{stats?.streakDays} days</p>
                <p className="text-sm text-orange-600 mt-1">Keep it up!</p>
              </div>
              <div className="p-3 bg-orange-100 rounded-full">
                <FireIcon className="w-6 h-6 text-orange-600" />
              </div>
            </div>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
            className="bg-white rounded-2xl shadow-lg p-6"
          >
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Quizzes Completed</p>
                <p className="text-2xl font-bold text-gray-900">{stats?.completedQuizzes}</p>
                <p className="text-sm text-purple-600 mt-1">+5 this week</p>
              </div>
              <div className="p-3 bg-purple-100 rounded-full">
                <AcademicCapIcon className="w-6 h-6 text-purple-600" />
              </div>
            </div>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3 }}
            className="bg-white rounded-2xl shadow-lg p-6"
          >
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Average Score</p>
                <p className="text-2xl font-bold text-gray-900">{stats?.averageScore}%</p>
                <p className="text-sm text-green-600 mt-1">+3% improvement</p>
              </div>
              <div className="p-3 bg-green-100 rounded-full">
                <ChartBarIcon className="w-6 h-6 text-green-600" />
              </div>
            </div>
          </motion.div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Left Column */}
          <div className="lg:col-span-2 space-y-8">
            {/* Weekly Progress Chart */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.4 }}
              className="bg-white rounded-2xl shadow-lg p-6"
            >
              <h3 className="text-lg font-semibold text-gray-900 mb-6">Weekly Study Progress</h3>
              
              <div className="space-y-4">
                {stats?.weeklyProgress.map((day, index) => (
                  <div key={day.day} className="flex items-center space-x-4">
                    <div className="w-12 text-sm text-gray-600 font-medium">{day.day}</div>
                    
                    <div className="flex-1">
                      <div className="flex items-center justify-between mb-1">
                        <span className="text-sm text-gray-600">Study Hours</span>
                        <span className="text-sm font-medium">{day.hours}h</span>
                      </div>
                      <div className="w-full bg-gray-200 rounded-full h-2">
                        <div
                          className="bg-blue-500 h-2 rounded-full transition-all duration-300"
                          style={{ width: `${(day.hours / 5) * 100}%` }}
                        />
                      </div>
                    </div>
                    
                    <div className="flex-1">
                      <div className="flex items-center justify-between mb-1">
                        <span className="text-sm text-gray-600">Average Score</span>
                        <span className="text-sm font-medium">{day.score}%</span>
                      </div>
                      <div className="w-full bg-gray-200 rounded-full h-2">
                        <div
                          className={`h-2 rounded-full transition-all duration-300 ${getProgressBarColor(day.score)}`}
                          style={{ width: `${day.score}%` }}
                        />
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </motion.div>

            {/* Subject Progress */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.5 }}
              className="bg-white rounded-2xl shadow-lg p-6"
            >
              <h3 className="text-lg font-semibold text-gray-900 mb-6">Subject Progress</h3>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {Object.entries(stats?.subjectProgress || {}).map(([subject, progress]) => (
                  <div key={subject} className="p-4 border border-gray-200 rounded-lg">
                    <div className="flex items-center justify-between mb-2">
                      <span className="font-medium text-gray-900">{subject}</span>
                      <span className={`px-2 py-1 rounded-full text-xs font-medium ${getProgressColor(progress)}`}>
                        {progress}%
                      </span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-2">
                      <div
                        className={`h-2 rounded-full transition-all duration-500 ${getProgressBarColor(progress)}`}
                        style={{ width: `${progress}%` }}
                      />
                    </div>
                  </div>
                ))}
              </div>
            </motion.div>

            {/* Monthly Goals */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.6 }}
              className="bg-white rounded-2xl shadow-lg p-6"
            >
              <h3 className="text-lg font-semibold text-gray-900 mb-6">Monthly Goals</h3>
              
              <div className="space-y-6">
                <div>
                  <div className="flex items-center justify-between mb-2">
                    <div className="flex items-center space-x-2">
                      <ClockIcon className="w-4 h-4 text-blue-500" />
                      <span className="font-medium">Study Hours</span>
                      {getTrendIcon(stats?.monthlyGoals.studyHours.current || 0, stats?.monthlyGoals.studyHours.target || 0)}
                    </div>
                    <span className="text-sm text-gray-600">
                      {stats?.monthlyGoals.studyHours.current}/{stats?.monthlyGoals.studyHours.target}h
                    </span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-3">
                    <div
                      className="bg-blue-500 h-3 rounded-full transition-all duration-500"
                      style={{ width: `${((stats?.monthlyGoals.studyHours.current || 0) / (stats?.monthlyGoals.studyHours.target || 1)) * 100}%` }}
                    />
                  </div>
                </div>

                <div>
                  <div className="flex items-center justify-between mb-2">
                    <div className="flex items-center space-x-2">
                      <AcademicCapIcon className="w-4 h-4 text-purple-500" />
                      <span className="font-medium">Quizzes</span>
                      {getTrendIcon(stats?.monthlyGoals.quizzes.current || 0, stats?.monthlyGoals.quizzes.target || 0)}
                    </div>
                    <span className="text-sm text-gray-600">
                      {stats?.monthlyGoals.quizzes.current}/{stats?.monthlyGoals.quizzes.target}
                    </span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-3">
                    <div
                      className="bg-purple-500 h-3 rounded-full transition-all duration-500"
                      style={{ width: `${((stats?.monthlyGoals.quizzes.current || 0) / (stats?.monthlyGoals.quizzes.target || 1)) * 100}%` }}
                    />
                  </div>
                </div>

                <div>
                  <div className="flex items-center justify-between mb-2">
                    <div className="flex items-center space-x-2">
                      <BookOpenIcon className="w-4 h-4 text-green-500" />
                      <span className="font-medium">Subjects Studied</span>
                      {getTrendIcon(stats?.monthlyGoals.subjects.current || 0, stats?.monthlyGoals.subjects.target || 0)}
                    </div>
                    <span className="text-sm text-gray-600">
                      {stats?.monthlyGoals.subjects.current}/{stats?.monthlyGoals.subjects.target}
                    </span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-3">
                    <div
                      className="bg-green-500 h-3 rounded-full transition-all duration-500"
                      style={{ width: `${((stats?.monthlyGoals.subjects.current || 0) / (stats?.monthlyGoals.subjects.target || 1)) * 100}%` }}
                    />
                  </div>
                </div>
              </div>
            </motion.div>
          </div>

          {/* Right Column */}
          <div className="space-y-8">
            {/* Achievements */}
            <motion.div
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.7 }}
              className="bg-white rounded-2xl shadow-lg p-6"
            >
              <h3 className="text-lg font-semibold text-gray-900 mb-6 flex items-center">
                <TrophyIcon className="w-5 h-5 mr-2 text-yellow-500" />
                Recent Achievements
              </h3>
              
              <div className="space-y-4">
                {stats?.achievements.slice(0, 4).map((achievement) => (
                  <div key={achievement.id} className="flex items-start space-x-3 p-3 bg-yellow-50 rounded-lg">
                    <div className="text-2xl">{achievement.icon}</div>
                    <div className="flex-1">
                      <h4 className="font-medium text-gray-900">{achievement.title}</h4>
                      <p className="text-sm text-gray-600">{achievement.description}</p>
                      <p className="text-xs text-gray-500 mt-1">
                        {achievement.unlockedAt.toLocaleDateString()}
                      </p>
                    </div>
                  </div>
                ))}
              </div>
              
              <button className="w-full mt-4 px-4 py-2 text-purple-600 border border-purple-200 rounded-lg hover:bg-purple-50 transition-colors">
                View All Achievements
              </button>
            </motion.div>

            {/* Recent Activity */}
            <motion.div
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.8 }}
              className="bg-white rounded-2xl shadow-lg p-6"
            >
              <h3 className="text-lg font-semibold text-gray-900 mb-6 flex items-center">
                <CalendarDaysIcon className="w-5 h-5 mr-2 text-blue-500" />
                Recent Activity
              </h3>
              
              <div className="space-y-4">
                {stats?.recentActivity.map((activity) => (
                  <div key={activity.id} className="flex items-start space-x-3">
                    <div className="flex-shrink-0 mt-1">
                      {getActivityIcon(activity.type)}
                    </div>
                    <div className="flex-1">
                      <h4 className="font-medium text-gray-900 text-sm">{activity.title}</h4>
                      <p className="text-sm text-gray-600">{activity.description}</p>
                      {activity.metadata && (
                        <div className="flex items-center space-x-2 mt-1">
                          {activity.metadata.score && (
                            <span className="text-xs bg-green-100 text-green-800 px-2 py-1 rounded">
                              {activity.metadata.score}%
                            </span>
                          )}
                          {activity.metadata.duration && (
                            <span className="text-xs bg-blue-100 text-blue-800 px-2 py-1 rounded">
                              {activity.metadata.duration}m
                            </span>
                          )}
                        </div>
                      )}
                      <p className="text-xs text-gray-500 mt-1">
                        {activity.timestamp.toLocaleString()}
                      </p>
                    </div>
                  </div>
                ))}
              </div>
            </motion.div>

            {/* Study Insights */}
            <motion.div
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.9 }}
              className="bg-gradient-to-br from-purple-50 to-indigo-50 rounded-2xl p-6"
            >
              <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
                <ChartBarIcon className="w-5 h-5 mr-2 text-purple-600" />
                Study Insights
              </h3>
              
              <div className="space-y-3">
                <div className="flex items-start space-x-2">
                  <div className="w-2 h-2 bg-green-500 rounded-full mt-2"></div>
                  <div>
                    <p className="text-sm font-medium text-gray-900">Peak Performance</p>
                    <p className="text-xs text-gray-600">You perform best on Tuesdays and Saturdays</p>
                  </div>
                </div>
                
                <div className="flex items-start space-x-2">
                  <div className="w-2 h-2 bg-yellow-500 rounded-full mt-2"></div>
                  <div>
                    <p className="text-sm font-medium text-gray-900">Improvement Area</p>
                    <p className="text-xs text-gray-600">Biology needs more attention this week</p>
                  </div>
                </div>
                
                <div className="flex items-start space-x-2">
                  <div className="w-2 h-2 bg-blue-500 rounded-full mt-2"></div>
                  <div>
                    <p className="text-sm font-medium text-gray-900">Recommendation</p>
                    <p className="text-xs text-gray-600">Try shorter, more frequent study sessions</p>
                  </div>
                </div>
              </div>
            </motion.div>
          </div>
        </div>
      </div>
    </div>
  )
}
