'use client'

import React from 'react'
import { motion } from 'framer-motion'
import { 
  ExclamationTriangleIcon, 
  XCircleIcon, 
  InformationCircleIcon,
  CheckCircleIcon,
  XMarkIcon
} from '@heroicons/react/24/outline'

interface ErrorBoundaryState {
  hasError: boolean
  error?: Error
}

interface ErrorBoundaryProps {
  children: React.ReactNode
  fallback?: React.ComponentType<{ error?: Error; resetError: () => void }>
}

export class ErrorBoundary extends React.Component<ErrorBoundaryProps, ErrorBoundaryState> {
  constructor(props: ErrorBoundaryProps) {
    super(props)
    this.state = { hasError: false }
  }

  static getDerivedStateFromError(error: Error): ErrorBoundaryState {
    return { hasError: true, error }
  }

  componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
    console.error('Error caught by boundary:', error, errorInfo)
  }

  resetError = () => {
    this.setState({ hasError: false, error: undefined })
  }

  render() {
    if (this.state.hasError) {
      const FallbackComponent = this.props.fallback || DefaultErrorFallback
      return <FallbackComponent error={this.state.error} resetError={this.resetError} />
    }

    return this.props.children
  }
}

interface ErrorFallbackProps {
  error?: Error
  resetError: () => void
}

function DefaultErrorFallback({ error, resetError }: ErrorFallbackProps) {
  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="text-center max-w-md mx-auto p-6"
      >
        <div className="w-16 h-16 bg-red-100 rounded-full flex items-center justify-center mx-auto mb-4">
          <XCircleIcon className="w-8 h-8 text-red-600" />
        </div>
        <h2 className="text-xl font-semibold text-gray-900 mb-2">
          Something went wrong
        </h2>
        <p className="text-gray-600 mb-6">
          {error?.message || 'An unexpected error occurred. Please try again.'}
        </p>
        <button
          onClick={resetError}
          className="btn-primary"
        >
          Try Again
        </button>
      </motion.div>
    </div>
  )
}

interface ErrorPageProps {
  title?: string
  message?: string
  action?: {
    label: string
    onClick: () => void
  }
  showHome?: boolean
}

export function ErrorPage({ 
  title = "Something went wrong",
  message = "An unexpected error occurred. Please try again.",
  action,
  showHome = true
}: ErrorPageProps) {
  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="text-center max-w-md mx-auto p-6"
      >
        <div className="w-16 h-16 bg-red-100 rounded-full flex items-center justify-center mx-auto mb-4">
          <XCircleIcon className="w-8 h-8 text-red-600" />
        </div>
        <h1 className="text-2xl font-bold text-gray-900 mb-2">{title}</h1>
        <p className="text-gray-600 mb-6">{message}</p>
        
        <div className="space-y-3">
          {action && (
            <button onClick={action.onClick} className="btn-primary w-full">
              {action.label}
            </button>
          )}
          {showHome && (
            <a href="/" className="btn-secondary w-full">
              Go to Home
            </a>
          )}
        </div>
      </motion.div>
    </div>
  )
}

interface EmptyStateProps {
  icon?: React.ComponentType<{ className?: string }>
  title: string
  description?: string
  action?: {
    label: string
    onClick: () => void
  }
  className?: string
}

export function EmptyState({ 
  icon: Icon = InformationCircleIcon,
  title,
  description,
  action,
  className = ""
}: EmptyStateProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className={`text-center py-12 ${className}`}
    >
      <div className="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
        <Icon className="w-8 h-8 text-gray-400" />
      </div>
      <h3 className="text-lg font-semibold text-gray-900 mb-2">{title}</h3>
      {description && (
        <p className="text-gray-600 mb-6 max-w-sm mx-auto">{description}</p>
      )}
      {action && (
        <button onClick={action.onClick} className="btn-primary">
          {action.label}
        </button>
      )}
    </motion.div>
  )
}

type ToastType = 'success' | 'error' | 'warning' | 'info'

interface ToastProps {
  type: ToastType
  title: string
  message?: string
  isVisible: boolean
  onClose: () => void
  autoClose?: boolean
  duration?: number
}

export function Toast({ 
  type, 
  title, 
  message, 
  isVisible, 
  onClose,
  autoClose = true,
  duration = 5000
}: ToastProps) {
  React.useEffect(() => {
    if (isVisible && autoClose) {
      const timer = setTimeout(onClose, duration)
      return () => clearTimeout(timer)
    }
  }, [isVisible, autoClose, duration, onClose])

  if (!isVisible) return null

  const typeConfig = {
    success: {
      icon: CheckCircleIcon,
      bgColor: 'bg-green-50',
      iconColor: 'text-green-400',
      titleColor: 'text-green-800',
      messageColor: 'text-green-700',
      borderColor: 'border-green-200'
    },
    error: {
      icon: XCircleIcon,
      bgColor: 'bg-red-50',
      iconColor: 'text-red-400',
      titleColor: 'text-red-800',
      messageColor: 'text-red-700',
      borderColor: 'border-red-200'
    },
    warning: {
      icon: ExclamationTriangleIcon,
      bgColor: 'bg-yellow-50',
      iconColor: 'text-yellow-400',
      titleColor: 'text-yellow-800',
      messageColor: 'text-yellow-700',
      borderColor: 'border-yellow-200'
    },
    info: {
      icon: InformationCircleIcon,
      bgColor: 'bg-blue-50',
      iconColor: 'text-blue-400',
      titleColor: 'text-blue-800',
      messageColor: 'text-blue-700',
      borderColor: 'border-blue-200'
    }
  }

  const config = typeConfig[type]
  const Icon = config.icon

  return (
    <motion.div
      initial={{ opacity: 0, y: -50, scale: 0.95 }}
      animate={{ opacity: 1, y: 0, scale: 1 }}
      exit={{ opacity: 0, y: -50, scale: 0.95 }}
      className={`
        fixed top-4 right-4 z-50 max-w-sm w-full
        ${config.bgColor} ${config.borderColor}
        border rounded-lg shadow-lg
      `}
    >
      <div className="p-4">
        <div className="flex items-start">
          <Icon className={`w-5 h-5 ${config.iconColor} mt-0.5 mr-3 flex-shrink-0`} />
          <div className="flex-1 min-w-0">
            <p className={`text-sm font-medium ${config.titleColor}`}>
              {title}
            </p>
            {message && (
              <p className={`mt-1 text-sm ${config.messageColor}`}>
                {message}
              </p>
            )}
          </div>
          <button
            onClick={onClose}
            className={`ml-3 flex-shrink-0 ${config.iconColor} hover:opacity-75`}
          >
            <XMarkIcon className="w-4 h-4" />
          </button>
        </div>
      </div>
    </motion.div>
  )
}

interface ErrorAlertProps {
  title?: string
  message: string
  onClose?: () => void
  className?: string
}

export function ErrorAlert({ 
  title = "Error",
  message,
  onClose,
  className = ""
}: ErrorAlertProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: -10 }}
      animate={{ opacity: 1, y: 0 }}
      className={`bg-red-50 border border-red-200 rounded-lg p-4 ${className}`}
    >
      <div className="flex items-start">
        <XCircleIcon className="w-5 h-5 text-red-400 mt-0.5 mr-3 flex-shrink-0" />
        <div className="flex-1 min-w-0">
          <h3 className="text-sm font-medium text-red-800">{title}</h3>
          <p className="mt-1 text-sm text-red-700">{message}</p>
        </div>
        {onClose && (
          <button
            onClick={onClose}
            className="ml-3 text-red-400 hover:text-red-500"
          >
            <XMarkIcon className="w-4 h-4" />
          </button>
        )}
      </div>
    </motion.div>
  )
}
