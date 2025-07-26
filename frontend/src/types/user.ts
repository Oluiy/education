export interface User {
  id: string
  email: string
  firstName: string
  lastName: string
  role: UserRole
  avatar?: string
  bio?: string
  createdAt: string
  updatedAt: string
  lastLoginAt?: string
  isActive: boolean
  emailVerified: boolean
  profile?: UserProfile
  preferences?: UserPreferences
}

export type UserRole = 'student' | 'teacher' | 'admin'

export interface UserProfile {
  id: string
  userId: string
  phoneNumber?: string
  dateOfBirth?: string
  address?: UserAddress
  education?: UserEducation[]
  experience?: UserExperience[]
  skills?: string[]
  interests?: string[]
  socialLinks?: UserSocialLinks
  privacy?: UserPrivacySettings
}

export interface UserAddress {
  street?: string
  city?: string
  state?: string
  zipCode?: string
  country?: string
}

export interface UserEducation {
  id: string
  institution: string
  degree: string
  field: string
  startDate: string
  endDate?: string
  current: boolean
  description?: string
}

export interface UserExperience {
  id: string
  company: string
  position: string
  startDate: string
  endDate?: string
  current: boolean
  description?: string
}

export interface UserSocialLinks {
  linkedin?: string
  twitter?: string
  github?: string
  website?: string
}

export interface UserPrivacySettings {
  profileVisibility: 'public' | 'private' | 'contacts'
  showEmail: boolean
  showPhone: boolean
  showAddress: boolean
  allowMessaging: boolean
}

export interface UserPreferences {
  language: string
  timezone: string
  theme: 'light' | 'dark' | 'system'
  emailNotifications: boolean
  pushNotifications: boolean
  autoSave: boolean
}

export interface UserStats {
  totalCourses: number
  completedCourses: number
  totalQuizzes: number
  completedQuizzes: number
  averageScore: number
  totalStudyTime: number
  streak: number
  achievements: number
  rank?: number
  points?: number
}

export interface UserActivity {
  id: string
  userId: string
  type: ActivityType
  description: string
  metadata?: Record<string, any>
  createdAt: string
}

export type ActivityType = 
  | 'course_enrolled'
  | 'course_completed'
  | 'quiz_submitted'
  | 'quiz_passed'
  | 'assignment_submitted'
  | 'grade_received'
  | 'achievement_earned'
  | 'login'
  | 'profile_updated'

export interface UserAchievement {
  id: string
  userId: string
  achievementId: string
  title: string
  description: string
  iconUrl?: string
  earnedAt: string
  category: AchievementCategory
  points: number
}

export type AchievementCategory = 
  | 'completion'
  | 'performance'
  | 'engagement'
  | 'streak'
  | 'milestone'

export interface CreateUserRequest {
  email: string
  password: string
  firstName: string
  lastName: string
  role: UserRole
}

export interface UpdateUserRequest {
  firstName?: string
  lastName?: string
  avatar?: string
  bio?: string
  profile?: Partial<UserProfile>
  preferences?: Partial<UserPreferences>
}

export interface UserFilters {
  role?: UserRole
  isActive?: boolean
  emailVerified?: boolean
  createdAfter?: string
  createdBefore?: string
  search?: string
}
