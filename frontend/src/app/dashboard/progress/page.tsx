'use client'

import { useState } from 'react'
import { motion } from 'framer-motion'
import {
  ChartBarIcon,
  TrophyIcon,
  AcademicCapIcon,
  ClockIcon,
  FireIcon,
  BookOpenIcon,
  StarIcon,
  CheckCircleIcon,
  CalendarIcon,
  ArrowTrendingUpIcon,
  SparklesIcon,
  DocumentTextIcon
} from '@heroicons/react/24/outline'

interface ProgressData {
  overallProgress: number
  completedCourses: number
  totalCourses: number
  studyStreak: number
  totalStudyHours: number
  achievements: Array<{
    id: string
    title: string
    description: string
    icon: any
    earned: boolean
    earnedDate?: string
  }>
  recentActivity: Array<{
    id: string
    type: 'course_completed' | 'assignment_submitted' | 'quiz_passed' | 'milestone_reached'
    title: string
    date: string
    score?: number
  }>
  weeklyProgress: Array<{
    day: string
    hours: number
    completed: number
  }>
  courseProgress: Array<{
    id: string
    title: string
    progress: number
    totalLessons: number
    completedLessons: number
    lastActivity: string
  }>
}

// Mock data for demonstration
const mockData: ProgressData = {
  overallProgress: 67,
  completedCourses: 3,
  totalCourses: 8,
  studyStreak: 12,
  totalStudyHours: 48,
  achievements: [
    {
      id: '1',
      title: 'First Steps',
      description: 'Complete your first lesson',
      icon: CheckCircleIcon,
      earned: true,
      earnedDate: '2024-01-15'
    },
    {
      id: '2',
      title: 'Dedicated Learner',
      description: 'Study for 7 consecutive days',
      icon: FireIcon,
      earned: true,
      earnedDate: '2024-01-20'
    },
    {
      id: '3',
      title: 'Course Master',
      description: 'Complete your first course',
      icon: TrophyIcon,
      earned: true,
      earnedDate: '2024-01-25'
    },
    {
      id: '4',
      title: 'Quick Learner',
      description: 'Complete 5 lessons in one day',
      icon: SparklesIcon,
      earned: false
    },
    {
      id: '5',
      title: 'Study Marathon',
      description: 'Study for 30 consecutive days',
      icon: AcademicCapIcon,
      earned: false
    }
  ],
  recentActivity: [
    {
      id: '1',
      type: 'course_completed',
      title: 'Introduction to Mathematics',
      date: '2024-01-25',
      score: 92
    },
    {
      id: '2',
      type: 'quiz_passed',
      title: 'Physics Quiz #3',
      date: '2024-01-24',
      score: 88
    },
    {
      id: '3',
      type: 'assignment_submitted',
      title: 'Chemistry Lab Report',
      date: '2024-01-23'
    },
    {
      id: '4',
      type: 'milestone_reached',
      title: '50% Progress in Biology',
      date: '2024-01-22'
    }
  ],
  weeklyProgress: [
    { day: 'Mon', hours: 2.5, completed: 3 },
    { day: 'Tue', hours: 3.2, completed: 4 },
    { day: 'Wed', hours: 1.8, completed: 2 },
    { day: 'Thu', hours: 4.1, completed: 5 },
    { day: 'Fri', hours: 2.9, completed: 3 },
    { day: 'Sat', hours: 3.5, completed: 4 },
    { day: 'Sun', hours: 2.1, completed: 2 }
  ],
  courseProgress: [
    {
      id: '1',
      title: 'Advanced Physics',
      progress: 85,
      totalLessons: 20,
      completedLessons: 17,
      lastActivity: '2024-01-25'
    },
    {
      id: '2',
      title: 'Calculus Fundamentals',
      progress: 72,
      totalLessons: 25,
      completedLessons: 18,
      lastActivity: '2024-01-24'
    },
    {
      id: '3',
      title: 'Organic Chemistry',
      progress: 45,
      totalLessons: 30,
      completedLessons: 14,
      lastActivity: '2024-01-23'
    },
    {
      id: '4',
      title: 'Biology Basics',
      progress: 60,
      totalLessons: 22,
      completedLessons: 13,
      lastActivity: '2024-01-22'
    }
  ]
}

const StatCard = ({ title, value, subtitle, icon: Icon, color = 'slate' }: {
  title: string
  value: string | number
  subtitle?: string
  icon: any
  color?: 'slate' | 'teal' | 'blue' | 'green'
}) => {
  const colorClasses = {
    slate: 'text-slate-600 bg-slate-100',
    teal: 'text-teal-600 bg-teal-100',
    blue: 'text-blue-600 bg-blue-100',
    green: 'text-green-600 bg-green-100'
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 hover:shadow-md transition-shadow duration-200"
    >
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm font-medium text-gray-600">{title}</p>
          <p className="text-3xl font-bold text-gray-900 mt-1">{value}</p>
          {subtitle && <p className="text-sm text-gray-500 mt-1">{subtitle}</p>}
        </div>
        <div className={`p-3 rounded-lg ${colorClasses[color]}`}>
          <Icon className="w-6 h-6" />
        </div>
      </div>
    </motion.div>
  )
}

const ProgressBar = ({ percentage, color = 'slate' }: { percentage: number; color?: 'slate' | 'teal' | 'blue' | 'green' }) => {
  const colorClasses = {
    slate: 'bg-slate-600',
    teal: 'bg-teal-600',
    blue: 'bg-blue-600',
    green: 'bg-green-600'
  }

  return (
    <div className="w-full bg-gray-200 rounded-full h-2">
      <motion.div
        initial={{ width: 0 }}
        animate={{ width: `${percentage}%` }}
        transition={{ duration: 1, ease: "easeOut" }}
        className={`h-2 rounded-full ${colorClasses[color]}`}
      />
    </div>
  )
}

const AchievementBadge = ({ achievement }: { achievement: ProgressData['achievements'][0] }) => {
  const Icon = achievement.icon

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.9 }}
      animate={{ opacity: 1, scale: 1 }}
      className={`p-4 rounded-xl border-2 transition-all duration-200 ${
        achievement.earned
          ? 'bg-slate-50 border-slate-200 shadow-sm'
          : 'bg-gray-50 border-gray-200 opacity-60'
      }`}
    >
      <div className="flex items-center space-x-3">
        <div className={`p-2 rounded-lg ${
          achievement.earned ? 'bg-slate-100 text-slate-600' : 'bg-gray-100 text-gray-400'
        }`}>
          <Icon className="w-5 h-5" />
        </div>
        <div className="flex-1">
          <h4 className={`font-semibold text-sm ${
            achievement.earned ? 'text-gray-900' : 'text-gray-500'
          }`}>
            {achievement.title}
          </h4>
          <p className={`text-xs ${
            achievement.earned ? 'text-gray-600' : 'text-gray-400'
          }`}>
            {achievement.description}
          </p>
          {achievement.earned && achievement.earnedDate && (
            <p className="text-xs text-slate-500 mt-1">
              Earned on {new Date(achievement.earnedDate).toLocaleDateString()}
            </p>
          )}
        </div>
        {achievement.earned && (
          <div className="text-slate-600">
            <CheckCircleIcon className="w-5 h-5" />
          </div>
        )}
      </div>
    </motion.div>
  )
}

export default function ProgressPage() {
  const [data] = useState<ProgressData>(mockData)
  const [activeTab, setActiveTab] = useState<'overview' | 'achievements' | 'activity'>('overview')

  const maxHours = Math.max(...data.weeklyProgress.map(d => d.hours))

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Learning Progress</h1>
          <p className="text-gray-600 mt-2">Track your educational journey and achievements</p>
        </div>
        <div className="flex items-center space-x-2 text-sm text-gray-600">
          <CalendarIcon className="w-4 h-4" />
          <span>Last updated: {new Date().toLocaleDateString()}</span>
        </div>
      </div>

      {/* Stats Overview */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <StatCard
          title="Overall Progress"
          value={`${data.overallProgress}%`}
          subtitle="Across all courses"
          icon={ChartBarIcon}
          color="slate"
        />
        <StatCard
          title="Completed Courses"
          value={data.completedCourses}
          subtitle={`of ${data.totalCourses} total`}
          icon={AcademicCapIcon}
          color="teal"
        />
        <StatCard
          title="Study Streak"
          value={data.studyStreak}
          subtitle="consecutive days"
          icon={FireIcon}
          color="blue"
        />
        <StatCard
          title="Total Study Time"
          value={`${data.totalStudyHours}h`}
          subtitle="this month"
          icon={ClockIcon}
          color="green"
        />
      </div>

      {/* Motivational Message */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="bg-gradient-to-r from-slate-50 to-teal-50 rounded-xl p-6 border border-slate-200"
      >
        <div className="flex items-center space-x-4">
          <div className="p-3 bg-slate-100 rounded-lg">
            <SparklesIcon className="w-6 h-6 text-slate-600" />
          </div>
          <div>
            <h3 className="font-semibold text-gray-900">Keep up the great work!</h3>
            <p className="text-gray-600 mt-1">
              You're on a {data.studyStreak}-day streak! You're {100 - data.overallProgress}% away from reaching your learning goals.
            </p>
          </div>
        </div>
      </motion.div>

      {/* Tabs */}
      <div className="border-b border-gray-200">
        <nav className="-mb-px flex space-x-8">
          {[
            { id: 'overview', label: 'Overview', icon: ChartBarIcon },
            { id: 'achievements', label: 'Achievements', icon: TrophyIcon },
            { id: 'activity', label: 'Recent Activity', icon: ClockIcon }
          ].map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id as any)}
              className={`flex items-center space-x-2 py-4 px-1 border-b-2 font-medium text-sm transition-colors duration-200 ${
                activeTab === tab.id
                  ? 'border-slate-500 text-slate-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              <tab.icon className="w-4 h-4" />
              <span>{tab.label}</span>
            </button>
          ))}
        </nav>
      </div>

      {/* Tab Content */}
      {activeTab === 'overview' && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Weekly Progress Chart */}
          <motion.div
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            className="bg-white rounded-xl shadow-sm border border-gray-200 p-6"
          >
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Weekly Activity</h3>
            <div className="space-y-4">
              {data.weeklyProgress.map((day) => (
                <div key={day.day} className="flex items-center space-x-4">
                  <div className="w-12 text-sm font-medium text-gray-600">{day.day}</div>
                  <div className="flex-1">
                    <div className="flex items-center justify-between mb-1">
                      <span className="text-sm text-gray-500">{day.hours}h studied</span>
                      <span className="text-sm text-gray-500">{day.completed} completed</span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-2">
                      <motion.div
                        initial={{ width: 0 }}
                        animate={{ width: `${(day.hours / maxHours) * 100}%` }}
                        transition={{ duration: 0.8, delay: 0.1 }}
                        className="h-2 rounded-full bg-slate-600"
                      />
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </motion.div>

          {/* Course Progress */}
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            className="bg-white rounded-xl shadow-sm border border-gray-200 p-6"
          >
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Course Progress</h3>
            <div className="space-y-4">
              {data.courseProgress.map((course) => (
                <div key={course.id} className="space-y-2">
                  <div className="flex items-center justify-between">
                    <h4 className="font-medium text-gray-900">{course.title}</h4>
                    <span className="text-sm font-medium text-slate-600">{course.progress}%</span>
                  </div>
                  <ProgressBar percentage={course.progress} color="slate" />
                  <div className="flex items-center justify-between text-sm text-gray-500">
                    <span>{course.completedLessons}/{course.totalLessons} lessons</span>
                    <span>Last activity: {new Date(course.lastActivity).toLocaleDateString()}</span>
                  </div>
                </div>
              ))}
            </div>
          </motion.div>
        </div>
      )}

      {activeTab === 'achievements' && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="space-y-6"
        >
          <div className="flex items-center justify-between">
            <h3 className="text-lg font-semibold text-gray-900">Your Achievements</h3>
            <div className="text-sm text-gray-600">
              {data.achievements.filter(a => a.earned).length} of {data.achievements.length} earned
            </div>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {data.achievements.map((achievement) => (
              <AchievementBadge key={achievement.id} achievement={achievement} />
            ))}
          </div>
        </motion.div>
      )}

      {activeTab === 'activity' && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="bg-white rounded-xl shadow-sm border border-gray-200 p-6"
        >
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Recent Activity</h3>
          <div className="space-y-4">
            {data.recentActivity.map((activity) => {
              const getIcon = () => {
                switch (activity.type) {
                  case 'course_completed': return AcademicCapIcon
                  case 'quiz_passed': return StarIcon
                  case 'assignment_submitted': return DocumentTextIcon
                  case 'milestone_reached': return ArrowTrendingUpIcon
                  default: return BookOpenIcon
                }
              }
              
              const getColor = () => {
                switch (activity.type) {
                  case 'course_completed': return 'text-green-600 bg-green-100'
                  case 'quiz_passed': return 'text-blue-600 bg-blue-100'
                  case 'assignment_submitted': return 'text-slate-600 bg-slate-100'
                  case 'milestone_reached': return 'text-teal-600 bg-teal-100'
                  default: return 'text-gray-600 bg-gray-100'
                }
              }

              const Icon = getIcon()

              return (
                <div key={activity.id} className="flex items-center space-x-4 p-3 hover:bg-gray-50 rounded-lg transition-colors duration-200">
                  <div className={`p-2 rounded-lg ${getColor()}`}>
                    <Icon className="w-4 h-4" />
                  </div>
                  <div className="flex-1">
                    <h4 className="font-medium text-gray-900">{activity.title}</h4>
                    <p className="text-sm text-gray-500">{new Date(activity.date).toLocaleDateString()}</p>
                  </div>
                  {activity.score && (
                    <div className="text-right">
                      <span className="text-sm font-medium text-gray-900">{activity.score}%</span>
                      <p className="text-xs text-gray-500">Score</p>
                    </div>
                  )}
                </div>
              )
            })}
          </div>
        </motion.div>
      )}
    </div>
  )
}
