export interface Quiz {
  id: string
  title: string
  description?: string
  instructions?: string
  courseId: string
  questions: Question[]
  timeLimit?: number
  maxAttempts?: number
  isPublished: boolean
  passingScore?: number
  createdBy: string
  createdAt: string
  updatedAt: string
  dueDate?: string
  shuffleQuestions?: boolean
  showCorrectAnswers?: boolean
  settings?: QuizSettings
}

export interface Question {
  id: string
  type: 'multiple-choice' | 'true-false' | 'short-answer' | 'essay' | 'fill-blank'
  question: string
  options?: string[]
  correctAnswer?: string | string[]
  points: number
  explanation?: string
  order: number
  required?: boolean
}

export interface QuizSettings {
  shuffleQuestions?: boolean
  shuffleAnswers?: boolean
  showProgressBar?: boolean
  allowBackNavigation?: boolean
  showTimer?: boolean
  autoSubmit?: boolean
  preventCheating?: boolean
  lockdownBrowser?: boolean
}

export interface QuizAttempt {
  id: string
  quizId: string
  userId: string
  answers: QuizAnswer[]
  score?: number
  totalPoints?: number
  percentage?: number
  status: 'in-progress' | 'submitted' | 'graded' | 'expired'
  startedAt: string
  submittedAt?: string
  timeSpent?: number
  attempt: number
  feedback?: string
  graded?: boolean
  gradedAt?: string
  gradedBy?: string
}

export interface QuizAnswer {
  questionId: string
  answer: string | string[]
  isCorrect?: boolean
  points?: number
  feedback?: string
  timeSpent?: number
}

export interface QuizStats {
  totalAttempts: number
  averageScore: number
  highestScore: number
  lowestScore: number
  passRate: number
  averageTimeSpent: number
  questionStats: QuestionStats[]
}

export interface QuestionStats {
  questionId: string
  correctAnswers: number
  totalAnswers: number
  averageTimeSpent: number
  difficulty: 'easy' | 'medium' | 'hard'
}

export interface QuizSubmission {
  id: string
  quizId: string
  userId: string
  answers: Record<string, any>
  submittedAt: string
  score?: number
  feedback?: string
  graded: boolean
}

export interface QuizFormData {
  title: string
  description?: string
  instructions?: string
  courseId: string
  timeLimit?: number
  maxAttempts?: number
  passingScore?: number
  dueDate?: string
  settings?: QuizSettings
  questions: QuestionFormData[]
}

export interface QuestionFormData {
  type: Question['type']
  question: string
  options?: string[]
  correctAnswer?: string | string[]
  points: number
  explanation?: string
  required?: boolean
}

export interface CreateQuizRequest {
  title: string
  description?: string
  courseId: string
  questions: Question[]
  settings?: QuizSettings
}

export interface UpdateQuizRequest {
  title?: string
  description?: string
  questions?: Question[]
  settings?: QuizSettings
  isPublished?: boolean
}

export interface SubmitQuizRequest {
  answers: QuizAnswer[]
  timeSpent?: number
}
