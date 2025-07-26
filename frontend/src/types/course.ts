export interface Course {
  id: string
  title: string
  description: string
  thumbnail?: string
  category: string
  level: CourseLevel
  duration: number
  price: number
  instructor: string
  instructorId: string
  enrollmentCount: number
  rating: number
  ratingCount: number
  isPublished: boolean
  isFeatured: boolean
  createdAt: string
  updatedAt: string
  tags: string[]
  prerequisites: string[]
  learningObjectives: string[]
  syllabus: CourseSyllabus[]
  resources: CourseResource[]
  settings: CourseSettings
}

export type CourseLevel = 'beginner' | 'intermediate' | 'advanced'

export interface CourseSyllabus {
  id: string
  title: string
  description?: string
  order: number
  lessons: CourseLesson[]
  duration: number
  isLocked: boolean
}

export interface CourseLesson {
  id: string
  title: string
  description?: string
  type: LessonType
  content?: string
  videoUrl?: string
  duration: number
  order: number
  isCompleted: boolean
  isLocked: boolean
  resources: CourseResource[]
}

export type LessonType = 'video' | 'text' | 'quiz' | 'assignment' | 'discussion'

export interface CourseResource {
  id: string
  title: string
  type: ResourceType
  url: string
  size?: number
  description?: string
}

export type ResourceType = 'pdf' | 'video' | 'audio' | 'document' | 'link' | 'image'

export interface CourseSettings {
  allowDiscussions: boolean
  allowDownloads: boolean
  certificateEnabled: boolean
  passingScore: number
  autoEnroll: boolean
  maxStudents?: number
  accessDuration?: number
}

export interface CourseEnrollment {
  id: string
  courseId: string
  userId: string
  enrolledAt: string
  completedAt?: string
  progress: number
  status: EnrollmentStatus
  certificateUrl?: string
  lastAccessedAt?: string
}

export type EnrollmentStatus = 'active' | 'completed' | 'suspended' | 'expired'

export interface CourseProgress {
  courseId: string
  userId: string
  completedLessons: string[]
  totalLessons: number
  completedQuizzes: string[]
  totalQuizzes: number
  overallProgress: number
  timeSpent: number
  lastAccessed: string
}

export interface CreateCourseRequest {
  title: string
  description: string
  category: string
  level: CourseLevel
  price: number
  tags: string[]
  prerequisites: string[]
  learningObjectives: string[]
}

export interface UpdateCourseRequest {
  title?: string
  description?: string
  thumbnail?: string
  category?: string
  level?: CourseLevel
  price?: number
  isPublished?: boolean
  isFeatured?: boolean
  tags?: string[]
  prerequisites?: string[]
  learningObjectives?: string[]
  settings?: Partial<CourseSettings>
}

export interface CourseFilters {
  category?: string
  level?: CourseLevel
  priceMin?: number
  priceMax?: number
  rating?: number
  isPublished?: boolean
  isFeatured?: boolean
  instructor?: string
  search?: string
}

export interface CourseStats {
  totalEnrollments: number
  activeStudents: number
  completionRate: number
  averageRating: number
  averageProgress: number
  totalRevenue: number
  recentEnrollments: CourseEnrollment[]
}
