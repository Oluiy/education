'use client'

import { useState, useEffect } from 'react'
import { 
  ChartBarIcon,
  UserGroupIcon,
  BookOpenIcon,
  ClockIcon,
  ArrowTrendingUpIcon,
  ArrowTrendingDownIcon,
  EyeIcon,
  CheckCircleIcon,
  XCircleIcon,
  AcademicCapIcon
} from '@heroicons/react/24/outline'
import { 
  LineChart, 
  Line, 
  AreaChart, 
  Area, 
  BarChart, 
  Bar, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell
} from 'recharts'

interface DashboardStats {
  totalStudents: number
  totalCourses: number
  totalQuizzes: number
  totalFiles: number
  activeUsers: number
  completionRate: number
  avgQuizScore: number
  totalContentViews: number
}

interface CourseStats {
  id: number
  title: string
  enrollments: number
  completionRate: number
  avgProgress: number
  totalLessons: number
  avgRating: number
}

interface QuizStats {
  id: number
  title: string
  attempts: number
  avgScore: number
  passRate: number
  difficulty: string
}

interface ActivityData {
  date: string
  logins: number
  contentViews: number
  quizAttempts: number
  fileUploads: number
}

interface PerformanceData {
  subject: string
  score: number
  improvement: number
}

const COLORS = ['#3B82F6', '#EF4444', '#10B981', '#F59E0B', '#8B5CF6', '#EC4899']

export default function AnalyticsPage() {
  const [stats, setStats] = useState<DashboardStats | null>(null)
  const [courseStats, setCourseStats] = useState<CourseStats[]>([])
  const [quizStats, setQuizStats] = useState<QuizStats[]>([])
  const [activityData, setActivityData] = useState<ActivityData[]>([])
  const [performanceData, setPerformanceData] = useState<PerformanceData[]>([])
  const [loading, setLoading] = useState(true)
  const [selectedTimeRange, setSelectedTimeRange] = useState('7d')

  // Mock data - replace with actual API calls
  useEffect(() => {
    loadAnalyticsData()
  }, [selectedTimeRange])

  const loadAnalyticsData = async () => {
    try {
      setLoading(true)
      
      // Mock data - replace with actual API calls
      setTimeout(() => {
        setStats({
          totalStudents: 1248,
          totalCourses: 87,
          totalQuizzes: 234,
          totalFiles: 1567,
          activeUsers: 342,
          completionRate: 78.5,
          avgQuizScore: 85.2,
          totalContentViews: 15234
        })

        setCourseStats([
          { id: 1, title: 'Mathematics Basics', enrollments: 156, completionRate: 85, avgProgress: 72, totalLessons: 12, avgRating: 4.5 },
          { id: 2, title: 'Science Fundamentals', enrollments: 134, completionRate: 78, avgProgress: 68, totalLessons: 15, avgRating: 4.2 },
          { id: 3, title: 'English Literature', enrollments: 98, completionRate: 92, avgProgress: 88, totalLessons: 10, avgRating: 4.7 },
          { id: 4, title: 'History Overview', enrollments: 87, completionRate: 65, avgProgress: 54, totalLessons: 18, avgRating: 4.0 },
          { id: 5, title: 'Computer Science', enrollments: 176, completionRate: 72, avgProgress: 65, totalLessons: 20, avgRating: 4.3 }
        ])

        setQuizStats([
          { id: 1, title: 'Math Quiz #1', attempts: 234, avgScore: 82.5, passRate: 78, difficulty: 'Medium' },
          { id: 2, title: 'Science Quiz #1', attempts: 198, avgScore: 76.8, passRate: 65, difficulty: 'Hard' },
          { id: 3, title: 'English Quiz #1', attempts: 156, avgScore: 88.2, passRate: 89, difficulty: 'Easy' },
          { id: 4, title: 'History Quiz #1', attempts: 134, avgScore: 74.3, passRate: 67, difficulty: 'Medium' },
          { id: 5, title: 'CS Quiz #1', attempts: 187, avgScore: 79.6, passRate: 72, difficulty: 'Hard' }
        ])

        setActivityData([
          { date: '2024-01-01', logins: 145, contentViews: 567, quizAttempts: 89, fileUploads: 23 },
          { date: '2024-01-02', logins: 132, contentViews: 634, quizAttempts: 94, fileUploads: 18 },
          { date: '2024-01-03', logins: 167, contentViews: 723, quizAttempts: 112, fileUploads: 31 },
          { date: '2024-01-04', logins: 154, contentViews: 689, quizAttempts: 98, fileUploads: 25 },
          { date: '2024-01-05', logins: 189, contentViews: 756, quizAttempts: 126, fileUploads: 42 },
          { date: '2024-01-06', logins: 176, contentViews: 692, quizAttempts: 108, fileUploads: 28 },
          { date: '2024-01-07', logins: 198, contentViews: 789, quizAttempts: 134, fileUploads: 35 }
        ])

        setPerformanceData([
          { subject: 'Mathematics', score: 85, improvement: 12 },
          { subject: 'Science', score: 78, improvement: -3 },
          { subject: 'English', score: 92, improvement: 8 },
          { subject: 'History', score: 74, improvement: 15 },
          { subject: 'Computer Science', score: 81, improvement: 6 }
        ])

        setLoading(false)
      }, 1000)
    } catch (error) {
      console.error('Error loading analytics data:', error)
      setLoading(false)
    }
  }

  const StatCard = ({ 
    title, 
    value, 
    change, 
    icon: Icon, 
    color = 'blue' 
  }: { 
    title: string
    value: string | number
    change?: number
    icon: any
    color?: string 
  }) => {
    const colorClasses = {
      blue: 'bg-blue-500',
      green: 'bg-green-500',
      yellow: 'bg-yellow-500',
      red: 'bg-red-500',
      purple: 'bg-purple-500'
    }

    return (
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-sm font-medium text-gray-600">{title}</p>
            <p className="text-2xl font-bold text-gray-900 mt-1">{value}</p>
            {change !== undefined && (
              <div className="flex items-center mt-2">
                {change >= 0 ? (
                  <ArrowTrendingUpIcon className="w-4 h-4 text-green-500 mr-1" />
                ) : (
                  <ArrowTrendingDownIcon className="w-4 h-4 text-red-500 mr-1" />
                )}
                <span className={`text-sm ${change >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                  {change >= 0 ? '+' : ''}{change}%
                </span>
              </div>
            )}
          </div>
          <div className={`p-3 rounded-lg ${colorClasses[color as keyof typeof colorClasses] || colorClasses.blue}`}>
            <Icon className="w-6 h-6 text-white" />
          </div>
        </div>
      </div>
    )
  }

  if (loading) {
    return (
      <div className="p-6 max-w-7xl mx-auto">
        <div className="animate-pulse">
          <div className="h-8 bg-gray-200 rounded w-1/4 mb-6"></div>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
            {[...Array(4)].map((_, i) => (
              <div key={i} className="h-32 bg-gray-200 rounded-lg"></div>
            ))}
          </div>
          <div className="h-80 bg-gray-200 rounded-lg"></div>
        </div>
      </div>
    )
  }

  return (
    <div className="p-6 max-w-7xl mx-auto">
      {/* Header */}
      <div className="flex justify-between items-center mb-6">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Analytics Dashboard</h1>
          <p className="text-gray-600 mt-1">Track performance and engagement across your platform</p>
        </div>
        <div className="flex gap-2">
          {['7d', '30d', '90d', '1y'].map((range) => (
            <button
              key={range}
              onClick={() => setSelectedTimeRange(range)}
              className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                selectedTimeRange === range
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
            >
              {range === '7d' ? 'Last 7 days' : 
               range === '30d' ? 'Last 30 days' :
               range === '90d' ? 'Last 90 days' : 'Last year'}
            </button>
          ))}
        </div>
      </div>

      {/* Stats Overview */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <StatCard
          title="Total Students"
          value={stats?.totalStudents || 0}
          change={12}
          icon={UserGroupIcon}
          color="blue"
        />
        <StatCard
          title="Active Courses"
          value={stats?.totalCourses || 0}
          change={8}
          icon={BookOpenIcon}
          color="green"
        />
        <StatCard
          title="Quiz Attempts"
          value={stats?.totalQuizzes || 0}
          change={-3}
          icon={AcademicCapIcon}
          color="purple"
        />
        <StatCard
          title="Completion Rate"
          value={`${stats?.completionRate || 0}%`}
          change={5}
          icon={CheckCircleIcon}
          color="yellow"
        />
      </div>

      {/* Activity Chart */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Daily Activity</h3>
          <ResponsiveContainer width="100%" height={300}>
            <AreaChart data={activityData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis 
                dataKey="date" 
                tickFormatter={(value) => new Date(value).toLocaleDateString()} 
              />
              <YAxis />
              <Tooltip 
                labelFormatter={(value) => new Date(value).toLocaleDateString()}
              />
              <Area 
                type="monotone" 
                dataKey="logins" 
                stroke="#3B82F6" 
                fill="#3B82F6" 
                fillOpacity={0.1}
                name="Logins"
              />
              <Area 
                type="monotone" 
                dataKey="contentViews" 
                stroke="#10B981" 
                fill="#10B981" 
                fillOpacity={0.1}
                name="Content Views"
              />
            </AreaChart>
          </ResponsiveContainer>
        </div>

        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Performance by Subject</h3>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={performanceData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="subject" />
              <YAxis />
              <Tooltip />
              <Bar dataKey="score" fill="#3B82F6" name="Score" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Course Performance */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 mb-8">
        <div className="p-6 border-b border-gray-200">
          <h3 className="text-lg font-semibold text-gray-900">Course Performance</h3>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Course
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Enrollments
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Completion Rate
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Avg Progress
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Rating
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Lessons
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {courseStats.map((course) => (
                <tr key={course.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm font-medium text-gray-900">{course.title}</div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm text-gray-900">{course.enrollments}</div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="flex items-center">
                      <div className="text-sm text-gray-900">{course.completionRate}%</div>
                      <div className="ml-2 w-16 bg-gray-200 rounded-full h-2">
                        <div 
                          className="bg-green-600 h-2 rounded-full" 
                          style={{ width: `${course.completionRate}%` }}
                        />
                      </div>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm text-gray-900">{course.avgProgress}%</div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="flex items-center">
                      <div className="text-sm text-gray-900">{course.avgRating}</div>
                      <div className="ml-1 text-yellow-400">★</div>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm text-gray-900">{course.totalLessons}</div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Quiz Performance */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200">
        <div className="p-6 border-b border-gray-200">
          <h3 className="text-lg font-semibold text-gray-900">Quiz Performance</h3>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Quiz
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Attempts
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Avg Score
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Pass Rate
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Difficulty
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {quizStats.map((quiz) => (
                <tr key={quiz.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm font-medium text-gray-900">{quiz.title}</div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm text-gray-900">{quiz.attempts}</div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm text-gray-900">{quiz.avgScore}%</div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="flex items-center">
                      <div className="text-sm text-gray-900">{quiz.passRate}%</div>
                      <div className="ml-2 w-16 bg-gray-200 rounded-full h-2">
                        <div 
                          className={`h-2 rounded-full ${
                            quiz.passRate >= 80 ? 'bg-green-600' :
                            quiz.passRate >= 60 ? 'bg-yellow-600' : 'bg-red-600'
                          }`}
                          style={{ width: `${quiz.passRate}%` }}
                        />
                      </div>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`px-2 py-1 text-xs font-medium rounded-full ${
                      quiz.difficulty === 'Easy' ? 'bg-green-100 text-green-800' :
                      quiz.difficulty === 'Medium' ? 'bg-yellow-100 text-yellow-800' :
                      'bg-red-100 text-red-800'
                    }`}>
                      {quiz.difficulty}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}
