// Common API response types
export interface ApiResponse<T = any> {
  success: boolean
  data: T
  message?: string
  error?: string
}

export interface PaginatedResponse<T = any> {
  data: T[]
  pagination: {
    page: number
    limit: number
    total: number
    totalPages: number
    hasNext: boolean
    hasPrev: boolean
  }
}

export interface ApiError {
  code: string
  message: string
  statusCode: number
  details?: Record<string, any>
}

// Common query parameters
export interface PaginationParams {
  page?: number
  limit?: number
  sort?: string
  order?: 'asc' | 'desc'
}

export interface SearchParams {
  search?: string
  filters?: Record<string, any>
}

// File upload types
export interface FileUpload {
  file: File
  fileName?: string
  folder?: string
}

export interface UploadResponse {
  url: string
  fileName: string
  size: number
  mimeType: string
}

// Common form validation types
export interface ValidationRule {
  required?: boolean
  minLength?: number
  maxLength?: number
  pattern?: RegExp
  custom?: (value: any) => string | null
}

export interface ValidationResult {
  isValid: boolean
  errors: Record<string, string>
}

export interface FormField<T = any> {
  value: T
  error?: string
  touched: boolean
  rules?: ValidationRule[]
}

// Common UI state types
export interface LoadingState {
  isLoading: boolean
  error?: string
}

export interface ModalState {
  isOpen: boolean
  data?: any
}

export interface Toast {
  id: string
  type: 'success' | 'error' | 'warning' | 'info'
  title: string
  message?: string
  duration?: number
  actions?: ToastAction[]
}

export interface ToastAction {
  label: string
  action: () => void
}

// Component prop types
export interface BaseComponentProps {
  className?: string
  children?: React.ReactNode
}

export interface IconProps extends BaseComponentProps {
  size?: number
  color?: string
}

export interface ButtonProps extends BaseComponentProps {
  variant?: 'primary' | 'secondary' | 'danger' | 'ghost'
  size?: 'sm' | 'md' | 'lg'
  disabled?: boolean
  loading?: boolean
  onClick?: () => void
  type?: 'button' | 'submit' | 'reset'
}

// Export all other types
export * from './auth'
export * from './user'
export * from './course'
export * from './quiz'
export * from './notification'
